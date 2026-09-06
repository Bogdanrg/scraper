import asyncio
import logging
import re
from decimal import Decimal
from typing import Dict, List, Optional
from urllib.parse import urljoin

import aiohttp
from bs4 import BeautifulSoup
from dependency_injector.wiring import Provide, inject
from tenacity import (
    AsyncRetrying,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

from apps.catalog.enums import ScrapeStatus
from apps.catalog.schemas import BookScrapedItemSchema
from apps.catalog.storages import BookStorage, CategoryStorage, ScrapeRunStorage

logger = logging.getLogger(__name__)

RATING_MAP = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
}

AVAILABILITY_REGEX = re.compile(r"\((\d+)\s+available\)")
PRICE_REGEX = re.compile(r"[\d.]+")


def is_retryable_error(exc: BaseException) -> bool:
    """Ретраим только сетевые ошибки и 5xx, 4xx не ретраим."""
    if isinstance(exc, (aiohttp.ClientConnectionError, aiohttp.ServerTimeoutError)):
        return True
    if isinstance(exc, aiohttp.ClientResponseError):
        return exc.status >= 500
    return False


class ScrapService:
    @inject
    def __init__(
        self,
        book_storage: BookStorage = Provide["book_storage"],
        category_storage: CategoryStorage = Provide["category_storage"],
        scrape_run_storage: ScrapeRunStorage = Provide["scrape_run_storage"],
        base_url: str = "https://books.toscrape.com/",
        concurrency_limit: int = 10,
    ):
        self.book_storage = book_storage
        self.category_storage = category_storage
        self.scrape_run_storage = scrape_run_storage
        self.base_url = base_url
        self.concurrency_limit = concurrency_limit
        self.semaphore = asyncio.Semaphore(concurrency_limit)
        self._categories_cache: Dict[str, int] = {}

    async def fetch_html(self, session: aiohttp.ClientSession, url: str) -> str:
        """Скачивание HTML с контролем семафора и экспоненциальным бэкоффом."""
        async with self.semaphore:
            async for attempt in AsyncRetrying(
                stop=stop_after_attempt(4),
                wait=wait_exponential(multiplier=1, min=1, max=10),
                retry=retry_if_exception(is_retryable_error),
                reraise=True,
            ):
                with attempt:
                    async with session.get(url) as response:
                        if response.status >= 400:
                            response.raise_for_status()
                        return await response.text()

    def parse_catalogue_page(self, html: str, current_url: str) -> tuple[List[str], Optional[str]]:
        """Извлечение ссылок на книги и следующую страницу каталога."""
        soup = BeautifulSoup(html, "lxml")
        book_links: List[str] = []

        for article in soup.select("article.product_pod h3 a"):
            href = article.get("href")
            if href:
                book_links.append(urljoin(current_url, href))

        next_btn = soup.select_one("ul.pager li.next a")
        next_url = urljoin(current_url, next_btn["href"]) if next_btn and next_btn.get("href") else None

        return book_links, next_url

    def parse_book_detail(self, html: str, page_url: str) -> BookScrapedItemSchema:
        """Парсинг карточки товара в DTO BookScrapedItem."""
        soup = BeautifulSoup(html, "lxml")

        title_el = soup.select_one("div.product_main h1")
        title = title_el.get_text(strip=True) if title_el else "Unknown"

        upc = None
        for tr in soup.select("table.table-striped tr"):
            th = tr.find("th")
            td = tr.find("td")
            if th and td and th.get_text(strip=True) == "UPC":
                upc = td.get_text(strip=True)
                break

        if not upc:
            raise ValueError(f"UPC not found on page {page_url}")

        breadcrumb_links = soup.select("ul.breadcrumb li a")
        category_name = (
            breadcrumb_links[2].get_text(strip=True)
            if len(breadcrumb_links) >= 3
            else "Default"
        )

        price_el = soup.select_one("div.product_main p.price_color")
        price_match = PRICE_REGEX.search(price_el.get_text() if price_el else "")
        price = Decimal(price_match.group(0)) if price_match else Decimal("0.00")

        avail_el = soup.select_one("div.product_main p.instock.availability")
        avail_text = avail_el.get_text() if avail_el else ""
        avail_match = AVAILABILITY_REGEX.search(avail_text)
        availability = int(avail_match.group(1)) if avail_match else 0

        rating = 0
        star_el = soup.select_one("div.product_main p.star-rating")
        if star_el:
            classes = star_el.get("class", [])
            for cls in classes:
                if cls in RATING_MAP:
                    rating = RATING_MAP[cls]
                    break

        desc_el = soup.select_one("div#product_description + p")
        description = desc_el.get_text(strip=True) if desc_el else None

        img_el = soup.select_one("div#product_gallery img") or soup.select_one("div.item.active img")
        img_src = img_el.get("src", "") if img_el else ""
        image_url = urljoin(page_url, img_src)

        return BookScrapedItemSchema(
            upc=upc,
            title=title,
            price=price,
            availability=availability,
            rating=rating,
            description=description,
            page_url=page_url,
            image_url=image_url,
            category_name=category_name,
        )

    async def _resolve_category_ids(self, category_names: set[str]) -> Dict[str, int]:
        """Получение или создание ID категорий через CategoryStorage."""
        for name in category_names:
            if name not in self._categories_cache:
                slug = re.sub(r"[^\w]+", "-", name.lower()).strip("-")
                category_schema = await self.category_storage.get_or_create_by_name(name=name, slug=slug)
                self._categories_cache[name] = category_schema.id

        return self._categories_cache

    async def _scrape_single_book(
        self, session: aiohttp.ClientSession, url: str
    ) -> Optional[BookScrapedItemSchema]:
        """Парсинг единичной страницы товара."""
        try:
            html = await self.fetch_html(session, url)
            return self.parse_book_detail(html, url)
        except Exception as exc:
            logger.error("Failed to parse book at %s: %s", url, exc)
            return None

    async def run(self, run_id: int) -> None:
        """Оркестратор скрапинга через слои хранилищ."""
        connector = aiohttp.TCPConnector(
            limit=self.concurrency_limit,
            limit_per_host=self.concurrency_limit,
            ssl=False,
        )
        timeout = aiohttp.ClientTimeout(total=30, connect=10)

        await self.scrape_run_storage.set_status(run_id=run_id, status=ScrapeStatus.RUNNING)

        processed_total = 0
        created_total = 0
        updated_total = 0
        failed_total = 0

        try:
            async with aiohttp.ClientSession(
                connector=connector, timeout=timeout, raise_for_status=False
            ) as http_session:
                current_page_url: Optional[str] = urljoin(self.base_url, "catalogue/page-1.html")

                while current_page_url:
                    page_html = await self.fetch_html(http_session, current_page_url)
                    book_urls, next_page = self.parse_catalogue_page(page_html, current_page_url)

                    tasks = [self._scrape_single_book(http_session, url) for url in book_urls]
                    results = await asyncio.gather(*tasks, return_exceptions=False)

                    valid_items: List[BookScrapedItemSchema] = [r for r in results if isinstance(r, BookScrapedItemSchema)]
                    failed_total += len(book_urls) - len(valid_items)

                    if valid_items:
                        categories_map = await self._resolve_category_ids(
                            {item.category_name for item in valid_items}
                        )

                        books_payload = [
                            {
                                "upc": item.upc,
                                "title": item.title,
                                "price": item.price,
                                "availability": item.availability,
                                "rating": item.rating,
                                "description": item.description,
                                "page_url": str(item.page_url),
                                "image_url": str(item.image_url),
                                "category_id": categories_map[item.category_name],
                            }
                            for item in valid_items
                        ]

                        created, updated = await self.book_storage.bulk_upsert_books(books_payload)
                        created_total += created
                        updated_total += updated
                        processed_total += len(valid_items)

                        await self.scrape_run_storage.update(
                            filters={"id": run_id},
                            items_processed=processed_total,
                            items_created=created_total,
                            items_updated=updated_total,
                            items_failed=failed_total,
                        )

                    current_page_url = next_page

            await self.scrape_run_storage.set_status(run_id=run_id, status=ScrapeStatus.COMPLETED)

        except Exception as exc:
            logger.exception("Scraping execution error: %s", exc)
            await self.scrape_run_storage.set_status(
                run_id=run_id,
                status=ScrapeStatus.FAILED,
                error_log=str(exc),
            )
            raise
