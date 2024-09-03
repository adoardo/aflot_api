from fastapi import APIRouter
from .sailor_offers import router

offers_router = APIRouter(
    prefix="/api/v1",
    tags=["Входящие предложения для моряков"],
)


offers_router.include_router(router)
