from fastapi import APIRouter
from .get_tariffs import router


tariffs_router = APIRouter(
    prefix="/api/v1",
    tags=['Тарифы компании и моряка'],
)

tariffs_router.include_router(router)
