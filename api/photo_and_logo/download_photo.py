from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from starlette import status
from typing import Annotated
from models import user_model, company_model, auth
from api.auth.config import get_current_user
from api.s3API.request import credentials_request, bucket_name
import boto3

router = APIRouter()


@router.post("/photo", summary="Загрузка фото и логотипа")
async def photo_and_logo(current_user: Annotated[dict, Depends(get_current_user)],
                         photo: UploadFile = File(...)):
    try:

        access_key, secret_key = credentials_request()

        client_s3 = boto3.client(
            's3',
            endpoint_url="https://storage.clo.ru/s3-user-e5a009-default-bucket",
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
        )
        user_id = current_user.get('id')

        folder_name = f"user_{user_id}/photo/"
        file_key = f"{folder_name}{photo.filename}"

        client_s3.upload_fileobj(
            photo.file,
            str(bucket_name),
            file_key,
            ExtraArgs={'ACL': 'public-read'}
        )

        path = f"https://{bucket_name}.storage.clo.ru/{bucket_name}/{file_key}"

        if current_user['role'] == 'Моряк':

            user_info = await auth.get(user_id)

            resume = await user_model.get(user_info.resumeID)

            await resume.update({"$set": {"photo_path": path}})

            return resume

        elif current_user['role'] == 'Компания':

            company_info = await auth.get(user_id)

            resume = await company_model.get(company_info.resumeID)

            await resume.update({"$set": {"photo_path": path}})

            return resume

    except HTTPException as e:
        return HTTPException(detail=e.detail, status_code=status.HTTP_400_BAD_REQUEST)
