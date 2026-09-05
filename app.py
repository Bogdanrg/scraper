import uvicorn
import settings

from fastapi import FastAPI
from api.v1.scrap_router.scrap_routes import scrap_router

fast_api = FastAPI()
fast_api.include_router(scrap_router)


if __name__ == "__main__":
    uvicorn.run("app:fast_api", host=settings.APP_HOST, port=settings.APP_PORT, reload=True)
