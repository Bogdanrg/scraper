from typing import List

from apps.catalog.schemas import BookSchema
from apps.catalog.schemas.book_schema import BookFilterParams
from apps.catalog.schemas.category_schema import CategorySchema
from apps.catalog.schemas.scrap_run_schema import ScrapeRunReadSchema
from apps.catalog.storages import CategoryStorage, ScrapeRunStorage, BookStorage
from apps.scraper.celery import scrape_catalog_task
from core.schemas import PaginationParams


class CatalogCases:
    def __init__(
            self,
            category_storage: CategoryStorage,
            scrap_storge: ScrapeRunStorage,
            book_storage: BookStorage
    ) -> None:
        self._book_storage = book_storage
        self._category_storage = category_storage
        self._scrap_storage = scrap_storge

    async def list_categories(self, params: PaginationParams) -> List[CategorySchema]:
        return await self._category_storage.list_objects(**dict(params))

    async def list_books(self, params: PaginationParams, filters: BookFilterParams) -> List[BookSchema]:
        return await self._book_storage.filter_books(**dict(params), params=filters)

    async def run_scrap(self) -> None:
        scrap_run = await self._scrap_storage.create()
        scrape_catalog_task.delay(run_id=scrap_run.id)

    async def list_scrape_runs(
            self,
            pagination_params: PaginationParams,
    ) -> List[ScrapeRunReadSchema]:
        return await self._scrap_storage.list_objects(**dict(pagination_params), order_by="started_at")
