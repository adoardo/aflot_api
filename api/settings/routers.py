from fastapi import APIRouter
from .all_settings import router

settings_router = APIRouter(
    prefix="/api/v1",
    tags=["Глобальные настройки"],
)


settings_router.include_router(router)
