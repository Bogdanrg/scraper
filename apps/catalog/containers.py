from dependency_injector import providers, containers

from apps.catalog.cases import CatalogCases
from apps.catalog.storages import CategoryStorage


class Container(containers.DeclarativeContainer):
    category_storage = providers.Singleton(CategoryStorage)
    catalog_cases = providers.Singleton(
        CatalogCases,
        category_storage=category_storage,
    )
