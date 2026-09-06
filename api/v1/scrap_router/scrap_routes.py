from typing import Annotated

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, Query

from apps.catalog.cases import CatalogCases
from apps.catalog.schemas import BookSchema
from apps.catalog.schemas.book_schema import BookFilterParams
from apps.catalog.schemas.category_schema import CategorySchema
from apps.catalog.schemas.scrap_run_schema import ScrapeRunReadSchema
from core.deps.filtering import get_book_filter_params
from core.deps.pagination import get_pagination_params
from core.schemas import PaginationParams
from apps.catalog.containers import Container

scrap_router = APIRouter(prefix="/scrap")


@scrap_router.get('/category')
@inject
async def get_categories(
        pagination_params: PaginationParams = Depends(get_pagination_params),
        catalog_cases: CatalogCases = Depends(Provide["catalog_cases"]),
) -> list[CategorySchema]:
    return await catalog_cases.list_categories(pagination_params)


@scrap_router.get('/books')
@inject
async def get_books(
        book_filters: BookFilterParams = Depends(get_book_filter_params),
        pagination_params: PaginationParams = Depends(get_pagination_params),
        catalog_cases: CatalogCases = Depends(Provide["catalog_cases"]),
) -> list[BookSchema]:
    return await catalog_cases.list_books(pagination_params, book_filters)


@scrap_router.post('/run_scrap')
@inject
async def run_scrap(
        catalog_cases: CatalogCases = Depends(Provide["catalog_cases"]),
) -> None:
    return await catalog_cases.run_scrap()


@scrap_router.get("/scraps")
@inject
async def get_scraps(
    pagination_params: PaginationParams = Depends(get_pagination_params),
    catalog_cases: CatalogCases = Depends(Provide["catalog_cases"]),
) -> list[ScrapeRunReadSchema]:
    return await catalog_cases.list_scrape_runs(pagination_params)


container = Container()
container.wire(modules=[__name__])
