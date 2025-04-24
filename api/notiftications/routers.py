from fastapi import APIRouter
from .notifications import router

notifications_router = APIRouter(
    prefix="/api/v1",
    tags=["Уведомления"],
)

notifications_router.include_router(router)

