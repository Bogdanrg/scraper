import asyncio
import socket

import aiohttp
import pytest
import pytest_asyncio
import uvicorn
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

import settings
from db import Base
from app import fast_api


HTML_DETAIL_FIXTURE = """
<!DOCTYPE html>
<html>
<head><title>A Light in the Attic | Books to Scrape</title></head>
<body>
    <ul class="breadcrumb">
        <li><a href="../../index.html">Home</a></li>
        <li><a href="../category/books_1/index.html">Books</a></li>
        <li><a href="../category/books/poetry_23/index.html">Poetry</a></li>
        <li class="active">A Light in the Attic</li>
    </ul>
    <div class="product_main">
        <h1>A Light in the Attic</h1>
        <p class="price_color">£51.77</p>
        <p class="instock availability"><i class="icon-ok"></i> In stock (22 available)</p>
        <p class="star-rating Three"></p>
    </div>
    <div id="product_description" class="sub-heading"><h2>Product Description</h2></div>
    <p>It's hard to imagine a world without A Light in the Attic.</p>
    <div id="product_gallery"><img src="../../media/cache/2c/da/2cdad67c44b002e7ec0187c3d903d307.jpg" /></div>
    <table class="table table-striped">
        <tr><th>UPC</th><td>a897fe39b1053632</td></tr>
        <tr><th>Product Type</th><td>Books</td></tr>
    </table>
</body>
</html>
"""


@pytest.fixture
def book_detail_html() -> str:
    return HTML_DETAIL_FIXTURE


@pytest_asyncio.fixture
async def async_engine():
    engine = create_async_engine(
        settings.TEST_DB_URL_ASYNC,
        echo=False,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(async_engine):
    session_factory = async_sessionmaker(async_engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session


def get_free_port() -> int:
    """Находит свободный порт на машине."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


@pytest_asyncio.fixture
async def aiohttp_client():
    port = get_free_port()
    config = uvicorn.Config(app=fast_api, host="127.0.0.1", port=port, log_level="warning")
    server = uvicorn.Server(config)

    # Запускаем Uvicorn в фоновом таске текущего event loop
    server_task = asyncio.create_task(server.serve())

    # Ждем, пока сервер поднимется и начнет принимать соединения
    while not server.started:
        await asyncio.sleep(0.05)

    base_url = f"http://127.0.0.1:{port}"

    async with aiohttp.ClientSession(base_url=base_url) as session:
        yield session

    # Корректно останавливаем сервер после завершения теста
    server.should_exit = True
    await server_task
