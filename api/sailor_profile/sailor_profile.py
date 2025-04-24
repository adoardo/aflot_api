from fastapi import APIRouter, Depends, HTTPException
from schemas.profile.profile_sailor import ProfileUserSchemas
from starlette import status
from models import user_model, auth
from typing import Annotated
from api.auth.config import get_current_user


router = APIRouter()


@router.get("/resume", status_code=status.HTTP_200_OK, response_model=ProfileUserSchemas,
            summary="Резюме моряка")
async def get_resume(current_user: Annotated[dict, Depends(get_current_user)]):

    try:

        if current_user is None or current_user['role'] == 'Компания':

            return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        user_id = current_user.get('id')

        resume_id = await auth.get(user_id)

        resume = await user_model.get(resume_id.resumeID)

        if not resume:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No resume found")

        return resume

    except HTTPException as e:
        return HTTPException(detail=e, status_code=status.HTTP_400_BAD_REQUEST)

@router.get("/resume-full", summary="Полное резюме моряка")
async def get_full_resume(current_user: Annotated[dict, Depends(get_current_user)]):

    try:

        if current_user is None or current_user['role'] == 'Компания':

            return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        user_id = current_user.get('id')

        resume_id = await auth.get(user_id)

        resume = await user_model.get(resume_id.resumeID)

        return resume

    except HTTPException as e:
        return HTTPException(detail=e, status_code=status.HTTP_400_BAD_REQUEST)


@router.put('/resume', status_code=status.HTTP_201_CREATED, summary="Изменить резюме моряка")
async def put_resume_sailor(current_user: Annotated[dict, Depends(get_current_user)],
                            request: ProfileUserSchemas):


    try:

        if current_user is None or current_user['role'] == 'Компания':

            return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        user_id = current_user.get('id')

        resume_id = await auth.get(user_id)

        resume = await user_model.get(resume_id.resumeID)

        if not resume:

            return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No resume found")

        request = {k: v for k, v in request.dict().items() if v is not None}

        update_query = {"$set": {
            field: value for field, value in request.items()
        }}

        await resume.update(update_query)

        return resume

    except HTTPException as e:

        return HTTPException(detail=e, status_code=status.HTTP_400_BAD_REQUEST)
