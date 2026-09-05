from dependency_injector import containers, providers
from db.orm import async_session


class DBContainer(containers.DeclarativeContainer):
    session = providers.Callable(async_session)
