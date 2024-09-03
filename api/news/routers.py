from fastapi import APIRouter
from .get_news import router

news_router = APIRouter(
    prefix="/api/v1",
    tags=["Страница новостей"],
)


news_router.include_router(router)
