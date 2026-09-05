from decimal import Decimal
from typing import Optional

from pydantic import HttpUrl

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
