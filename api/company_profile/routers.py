from .company_profile import router
from fastapi import APIRouter

profile_router = APIRouter(
    prefix="/api/v1",
    tags=["Профиль компании"],
)

profile_router.include_router(router)
