from fastapi import APIRouter
from .navy import router as navy_data_router

navy_router = APIRouter(
    prefix="/api/v1",
    tags=["Морской флот"],
)

navy_router.include_router(navy_data_router)
