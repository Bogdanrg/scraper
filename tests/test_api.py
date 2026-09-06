import pytest
from decimal import Decimal
from apps.catalog.storages import BookStorage, CategoryStorage


@pytest.mark.asyncio
async def test_get_books_filtered(aiohttp_client, db_session):
    category_storage = CategoryStorage()
    book_storage = BookStorage()

    cat = await category_storage.create(
        session=db_session,
        name="Science",
        slug="science",
    )

    await book_storage.bulk_create(
        session=db_session,
        items=[
            {
                "upc": "book_sci_1",
                "title": "Quantum Physics for Beginners",
                "price": Decimal("25.00"),
                "availability": 10,
                "rating": 5,
                "category_id": cat.id,
                "page_url": "http://example.com/1",
                "image_url": "http://example.com/1.jpg",
            },
            {
                "upc": "book_sci_2",
                "title": "Advanced Classical Mechanics",
                "price": Decimal("85.00"),
                "availability": 0,
                "rating": 3,
                "category_id": cat.id,
                "page_url": "http://example.com/2",
                "image_url": "http://example.com/2.jpg",
            },
        ],
    )

    async with aiohttp_client.get(
            "/api/v1/scrap/books",
            params={
                "query": "Quantum",
                "min_price": "10.00",
                "max_price": "50.00",
                "in_stock_only": "true",
            },
    ) as resp:
        assert resp.status == 200

    assert resp.status == 200
    data = await resp.json()

    assert len(data) == 1
    assert data[0]["upc"] == "book_sci_1"
    assert data[0]["title"] == "Quantum Physics for Beginners"
    assert Decimal(str(data[0]["price"])) == Decimal("25.00")
