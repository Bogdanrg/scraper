from decimal import Decimal
from apps.scraper.scraper_service import ScrapService


def test_parse_book_detail_fixture(book_detail_html: str):
    service = ScrapService(
        book_storage=None,
        category_storage=None,
        scrape_run_storage=None,
    )
    base_page_url = "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"

    dto = service.parse_book_detail(html=book_detail_html, page_url=base_page_url)

    assert dto.upc == "a897fe39b1053632"
    assert dto.title == "A Light in the Attic"
    assert dto.category_name == "Poetry"
    assert dto.price == Decimal("51.77")
    assert dto.availability == 22
    assert dto.rating == 3
    assert dto.description == "It's hard to imagine a world without A Light in the Attic."
    assert str(dto.page_url) == base_page_url
    assert str(dto.image_url) == "https://books.toscrape.com/media/cache/2c/da/2cdad67c44b002e7ec0187c3d903d307.jpg"
