from fastapi import APIRouter
from .register import router


auth_router = APIRouter(
    prefix="/api/v1",
    tags=["Авторизация и Регистрация"]
)

auth_router.include_router(router)
