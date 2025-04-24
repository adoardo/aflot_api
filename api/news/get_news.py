from fastapi import APIRouter, HTTPException, Depends
from starlette import status
from models.news import news_model
from beanie import PydanticObjectId

import math

router = APIRouter()


@router.get('/news', status_code=status.HTTP_200_OK, summary="Страница новостей")
async def news_get(page: int = 1, page_size: int = 5):
    try:

        skip = (page - 1) * page_size

        total_news = await news_model.find().count()
        total_pages = math.ceil(total_news / page_size)
        news = await news_model.find().skip(skip).limit(page_size).to_list()


        data = {
            "news": news,
            "total_pages": total_pages,
            "current_page": page
        }
        return data
    except HTTPException as e:
        return HTTPException(detail=e, status_code=status.HTTP_400_BAD_REQUEST)


@router.get('/news/{news_id}', summary="Возвращает новость по ID")
async def get_news_id(news_id: PydanticObjectId):
    try:

        news_obj = await news_model.get(news_id)
        if not news_obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='News not found')

        prev_news = await news_model.find_one({"_id": {"$lt": news_id}}, sort=[("_id", -1)])
        next_news = await news_model.find_one({"_id": {"$gt": news_id}}, sort=[("_id", 1)])

        data = {
            "current_news": news_obj,
            "prev_news": prev_news,
            "next_news": next_news
        }
        return data
    except HTTPException as e:

        return HTTPException(detail=e, status_code=status.HTTP_400_BAD_REQUEST)
