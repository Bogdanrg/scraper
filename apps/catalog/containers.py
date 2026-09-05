from dependency_injector import providers, containers

from apps.catalog.cases import CatalogCases
from apps.catalog.storages import CatalogStorage


class Container(containers.DeclarativeContainer):
    catalog_storage = providers.Singleton(CatalogStorage)
    catalog_cases = providers.Singleton(
        CatalogCases,
        catalog_storage=catalog_storage,
    )
