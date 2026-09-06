from dependency_injector import containers, providers

from db.containers import DBContainer
from apps.catalog.containers import Container as CatalogContainer
from apps.scraper.containers import Container as ScrapContainer

db_container = DBContainer()
db_container.wire(packages=[__name__])


class RootContainer(containers.DeclarativeContainer):
    catalog_app = providers.Container(CatalogContainer)
    scrap_app = providers.Container(ScrapContainer)


root_container = RootContainer()
root_container.wire(packages=[__name__])
root_container.catalog_app.wire(packages=[__name__])
root_container.scrap_app.wire(packages=[__name__])
