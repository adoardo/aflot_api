from fastapi import APIRouter
from .api_settings import router

settings_router = APIRouter(
    prefix="/api/v1",
    tags=["Настройки апи"],
)

settings_router.include_router(router)
