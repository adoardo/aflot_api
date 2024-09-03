from .swims_favorites import router as swims_favorites_router
from fastapi import APIRouter

favorite_router = APIRouter(
    prefix="/api/v1",
    tags=["Избранные вакансии и компании для моряка"],
)

favorite_router.include_router(swims_favorites_router)
