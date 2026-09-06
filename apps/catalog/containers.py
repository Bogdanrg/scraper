from dependency_injector import providers, containers

from apps.catalog.cases import CatalogCases
from apps.catalog.storages import CategoryStorage, ScrapeRunStorage, BookStorage


class Container(containers.DeclarativeContainer):
    category_storage = providers.Singleton(CategoryStorage)
    scrap_storage = providers.Singleton(ScrapeRunStorage)
    book_storage = providers.Singleton(BookStorage)
    catalog_cases = providers.Singleton(
        CatalogCases,
        category_storage=category_storage,
        scrap_storge=scrap_storage,
        book_storage=book_storage
    )
