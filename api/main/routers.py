from fastapi import APIRouter
from .main_page import router

main_router = APIRouter(
    prefix="/api/v1",
    tags=["Main Page"],
)

main_router.include_router(router)
