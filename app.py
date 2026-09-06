import uvicorn
import settings

from fastapi import FastAPI
from api.v1.v1_router import v1_router

fast_api = FastAPI()
fast_api.include_router(v1_router)


if __name__ == "__main__":
    uvicorn.run("app:fast_api", host=settings.APP_HOST, port=settings.APP_PORT, reload=True)
