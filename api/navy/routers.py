from fastapi import APIRouter
from .navy import router as company_info_router

company_router = APIRouter(
    prefix="/ap1/v1",
    tags=["Морской флот"],
)

company_router.include_router(company_info_router)
