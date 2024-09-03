from fastapi import APIRouter
from .sailor_profile import router

sailor_profile_router = APIRouter(
    prefix="/api/v1",
    tags=["Sailor profile"],
)

sailor_profile_router.include_router(router)
