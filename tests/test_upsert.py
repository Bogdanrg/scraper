import pytest
from decimal import Decimal
from apps.catalog.storages import BookStorage, CategoryStorage


@pytest.mark.asyncio
async def test_bulk_upsert_idempotency(db_session):
    category_storage = CategoryStorage()
    book_storage = BookStorage()

    category = await category_storage.create(
        session=db_session,
        name="Fiction",
        slug="fiction",
    )

    base_payload = {
        "upc": "b00k1234567890",
        "title": "Idempotent Book",
        "price": Decimal("10.00"),
        "availability": 5,
        "rating": 4,
        "description": "First write",
        "page_url": "https://books.toscrape.com/catalogue/book_1/index.html",
        "image_url": "https://books.toscrape.com/media/book_1.jpg",
        "category_id": category.id,
    }

    # 1. Первый запуск: строка создается
    created, updated = await book_storage.bulk_upsert_books([base_payload], session=db_session)
    assert created == 1
    assert updated == 0

    first_fetch = await book_storage.get_object(session=db_session, upc="b00k1234567890")
    assert first_fetch.price == Decimal("10.00")
    assert first_fetch.description == "First write"

    # 2. Второй запуск: обновляем цену и описание для того же UPC
    updated_payload = dict(base_payload)
    updated_payload["price"] = Decimal("19.99")
    updated_payload["description"] = "Updated write"

    created, updated = await book_storage.bulk_upsert_books([updated_payload], session=db_session)
    assert created == 0
    assert updated == 1

    # 3. Проверяем, что в БД ровно 1 запись и её данные обновились
    total_books = await book_storage.count(session=db_session, upc="b00k1234567890")
    assert total_books == 1

    second_fetch = await book_storage.get_object(session=db_session, upc="b00k1234567890")
    assert second_fetch.id == first_fetch.id
    assert second_fetch.price == Decimal("19.99")
    assert second_fetch.description == "Updated write"
