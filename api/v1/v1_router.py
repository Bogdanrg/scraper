from fastapi import APIRouter
from .scrap_router.scrap_routes import scrap_router


v1_router = APIRouter(prefix="/v1")
v1_router.include_router(scrap_router)
