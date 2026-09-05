import sys

from contextlib import asynccontextmanager
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from settings import DB_URL_ASYNC, LOG_ORM

Base = declarative_base()

engine = create_async_engine(
    DB_URL_ASYNC,
    echo=LOG_ORM,
    pool_size=10,
    max_overflow=5,
    pool_pre_ping=True,
    pool_recycle=1800,
    connect_args={"server_settings": {"jit": "off"}},
)

async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)


@asynccontextmanager
async def start_session(session):
    trans = None
    nested = False
    try:
        nested = session.in_transaction()
        if nested:
            trans = session.begin_nested()
        else:
            trans = session.begin()

        await trans.__aenter__()
        yield session
    finally:
        if trans:
            await trans.__aexit__(*sys.exc_info())
        if not nested:
            await session.__aexit__(*sys.exc_info())
