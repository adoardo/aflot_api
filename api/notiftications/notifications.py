from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from models.notifications import notifications
from starlette import status

router = APIRouter()

@router.get("/notifications/{sailor_id}")
async def get_notifications(sailor_id: str):
    try:
        notification = await notifications.find_one({"user_id": sailor_id})

        if notification is None:
            return {"message": "No notifications found for this sailor."}

        return {"data": notification}
    except Exception as e:
        raise HTTPException(
            detail=str(e),
            status_code=status.HTTP_400_BAD_REQUEST
        )