import asyncio

from celery import Celery

from apps.scraper.scraper_service import ScrapService, logger
from settings import BROKER_URL

app = Celery("scrap", broker=f"{BROKER_URL}/0")


@app.task(bind=True, name="tasks.scrape_catalog", max_retries=0)
def scrape_catalog_task(self, run_id: int):
    """
    Фоновая Celery-таска, инициирующая скрапинг каталога.
    """
    logger.info("Starting scrape catalog task for run_id=%d", run_id)

    try:
        scrap_service = ScrapService()
        asyncio.run(scrap_service.run(run_id=run_id))
    except Exception as exc:
        logger.error("Scrape task failed: %s", exc)
        raise exc
