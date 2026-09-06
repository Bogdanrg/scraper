from dependency_injector import providers, containers

from apps.catalog.storages.catalog_storage import BookStorage, CategoryStorage, ScrapeRunStorage
from apps.scraper.scraper_service import ScrapService


class Container(containers.DeclarativeContainer):
    book_storage = providers.Singleton(BookStorage)
    category_storage = providers.Singleton(CategoryStorage)
    scrape_run_storage = providers.Singleton(ScrapeRunStorage)
    scrap_service = providers.Singleton(
        ScrapService,
        book_storage=book_storage,
        category_storage=category_storage,
        scrape_run_storage=scrape_run_storage,

    )
