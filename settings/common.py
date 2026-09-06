import os
from pathlib import Path

import dotenv

path_to_env = Path(__file__).parents[1].joinpath(".env")

try:
    dotenv.read_dotenv(path_to_env)
except AttributeError:
    from dotenv import load_dotenv

    load_dotenv(dotenv_path=path_to_env)

DB_HOST = os.environ.get("DB_HOST")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")
DB_PORT = int(os.environ.get("DB_PORT"))
DB_URL = f"{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
DB_URL_ASYNC = f"postgresql+asyncpg://{DB_URL}"
DB_URL_SYNC = f"postgresql://{DB_URL}"
LOG_ORM = True
ENV = os.environ.get("ENV")
BROKER_HOST = os.environ.get("BROKER_HOST")
BROKER_PORT = os.environ.get("BROKER_PORT")
BROKER_URL = f"redis://{BROKER_HOST}:{BROKER_PORT}"
APP_HOST = os.environ.get("APP_HOST")
APP_PORT = int(os.environ.get("APP_PORT"))
TEST_DB_NAME = os.environ.get("TEST_DB_NAME")
TEST_DB_URL = f"{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{TEST_DB_NAME}"
TEST_DB_URL_ASYNC = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{TEST_DB_NAME}"
