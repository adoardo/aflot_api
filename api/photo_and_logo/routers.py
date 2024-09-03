from fastapi import APIRouter
from .download_photo import router

download_router = APIRouter(
    prefix="/api/v1",
    tags=['Загрузка фото и логотипа']
)

download_router.include_router(router)



