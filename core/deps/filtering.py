from decimal import Decimal
from typing import Optional
from fastapi import Query

from apps.catalog.schemas.book_schema import BookFilterParams


def get_book_filter_params(
    query: Optional[str] = Query(None, description="Поиск по названию книги"),
    category_id: Optional[int] = Query(None, gt=0, description="ID категории"),
    category_slug: Optional[str] = Query(None, description="Slug категории"),
    min_price: Optional[Decimal] = Query(None, ge=Decimal("0.00"), description="Минимальная цена"),
    max_price: Optional[Decimal] = Query(None, ge=Decimal("0.00"), description="Максимальная цена"),
    rating: Optional[int] = Query(None, ge=0, le=5, description="Точный рейтинг от 0 до 5"),
    min_rating: Optional[int] = Query(None, ge=0, le=5, description="Минимальный рейтинг"),
    in_stock_only: bool = Query(False, description="Только книги в наличии"),
) -> BookFilterParams:
    return BookFilterParams(
        query=query,
        category_id=category_id,
        category_slug=category_slug,
        min_price=min_price,
        max_price=max_price,
        rating=rating,
        min_rating=min_rating,
        in_stock_only=in_stock_only,
    )
