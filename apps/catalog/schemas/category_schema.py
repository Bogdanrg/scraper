from core.schemas import ORMSchema


class ExternalCategorySchema(ORMSchema):
    name: str
    slug: str


class CategorySchema(ExternalCategorySchema):
    id: int
