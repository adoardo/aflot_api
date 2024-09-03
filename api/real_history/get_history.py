from fastapi import APIRouter, HTTPException
from starlette import status
from models import real_history
from typing import List


router = APIRouter(
    prefix="/api/v1",
    tags=["Real History"],
)


@router.get("/real-history", status_code=status.HTTP_200_OK, response_model=List[real_history],
            summary="Страница РЕАЛЬНЫЕ ИСТОРИИ")
async def get_history():
    try:

        history = await real_history.find().to_list()

        if not history:

            raise HTTPException(detail="No history found", status_code=status.HTTP_404_NOT_FOUND)

        return history
    except HTTPException as e:

        return HTTPException(detail=e, status_code=status.HTTP_400_BAD_REQUEST)
