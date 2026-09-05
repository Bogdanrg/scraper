from apps.catalog.models import Category
from apps.catalog.schemas.category_schema import CategorySchema
from core.shared.base_storage import BaseStorage


class CategoryStorage(BaseStorage[CategorySchema]):
    model_cls = Category
    schema_cls = CategorySchema
