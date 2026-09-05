from typing import List

from apps.catalog.schemas.category_schema import CategorySchema
from apps.catalog.storages import CategoryStorage
from core.schemas import PaginationParams


class CatalogCases:
    def __init__(self, category_storage: CategoryStorage) -> None:
        self._category_storage = category_storage

    async def list_categories(self, params: PaginationParams) -> List[CategorySchema]:
        return await self._category_storage.list_objects(**dict(params))
