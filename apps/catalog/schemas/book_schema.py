from decimal import Decimal
from typing import Optional

from pydantic import HttpUrl, BaseModel, Field

from core.schemas import ORMSchema


class ExternalBookSchema(ORMSchema):
    title: str
    price: Decimal
    availability: int
    rating: int
    description: Optional[str]
    page_url: HttpUrl
    image_url: HttpUrl


class BookSchema(ExternalBookSchema):
    id: int


class BookScrapedItemSchema(ExternalBookSchema):
    upc: str
    category_name: str


class BookFilterParams(BaseModel):
    query: Optional[str] = Field(None, min_length=1, max_length=100, description="Поиск по названию (ILike)")
    category_id: Optional[int] = Field(None, gt=0, description="ID категории")
    category_slug: Optional[str] = Field(None, min_length=1, description="Slug категории")
    min_price: Optional[Decimal] = Field(None, ge=Decimal("0.00"), description="Минимальная цена")
    max_price: Optional[Decimal] = Field(None, ge=Decimal("0.00"), description="Максимальная цена")
    rating: Optional[int] = Field(None, ge=0, le=5, description="Точный рейтинг")
    min_rating: Optional[int] = Field(None, ge=0, le=5, description="Минимальный рейтинг")
    in_stock_only: bool = Field(False, description="Только товары в наличии (availability > 0)")
