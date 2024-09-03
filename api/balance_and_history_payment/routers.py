from fastapi import APIRouter
from .balance_sailor_company import router

balance_router = APIRouter(
    prefix="/api/v1",
    tags=["Баланс и истории операций"],
)

balance_router.include_router(router)
