from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends

from apps.catalog.cases import CatalogCases
from apps.catalog.schemas.category_schema import CategorySchema
from core.deps.pagination import get_pagination_params
from core.schemas import PaginationParams
from apps.catalog.containers import Container

scrap_router = APIRouter(prefix="/scrap")


@scrap_router.get('/category')
@inject
async def get_checks(
        pagination_params: PaginationParams = Depends(get_pagination_params),
        catalog_cases: CatalogCases = Depends(Provide["catalog_cases"]),
) -> list[CategorySchema]:
    return await catalog_cases.list_categories(pagination_params)


container = Container()
container.wire(modules=[__name__])
