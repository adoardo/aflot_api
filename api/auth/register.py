from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from models.register import user_model, company_model
from models.auth import auth as auth_model
from .config import (generate_jwt_token, generate_salt, hash_password, oauth2_scheme,
                     verify_jwt_token, convert_objectid_to_str)
from schemas.auth.auth import UserAuthResumeId, UserCreate, CompanyCreate, EmailValidate, TokenUpdate, CompanyUpdateProfile
from starlette import status
from api.auth.auth import AuthServices, AuthSchemas
from schemas.auth.auth import Token
from fastapi.security import OAuth2PasswordRequestForm
from beanie import PydanticObjectId
from typing import Optional, Annotated
from api.auth.config import get_current_user

import random
import string
import re

from bson import ObjectId

import urllib.request
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
import os
import io
import requests
from dotenv import load_dotenv
load_dotenv()

router = APIRouter()

def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    print("Random string of length", length, "is:", result_str)


@router.post("/register/user", response_model=user_model, status_code=status.HTTP_201_CREATED,
             summary="Регистрация моряка")
async def register_user(user_data: UserCreate):
    try:

        if await auth_model.find_one({"email": user_data.email}):

            raise HTTPException(status_code=status.HTTP_200_OK, detail="Пользователь с таким email уже зарегистрирован.")

        if await auth_model.find_one({"phone_number": user_data.phone_number}):

            raise HTTPException(status_code=status.HTTP_200_OK, detail="Пользователь с таким номером телефона уже зарегистрирован.")

        if user_data.notification_settings.mailing_notification == False:

            raise HTTPException(status_code=status.HTTP_200_OK, detail="Вы не приняли условия пользовательского соглашения.")

        plen = len(user_data.password)
        if (plen < 7):

            raise HTTPException(status_code=status.HTTP_200_OK, detail="Слишком короткий пароль (мин. длина 8 символов).")

        if user_data.password != user_data.confirm_password:

            raise HTTPException(status_code=status.HTTP_200_OK, detail="Пароли не совпадают.")

        salt = generate_salt()
        hashed_password = hash_password(user_data.password, salt)
        tokenVal = hash_password(user_data.email, salt)

        user = user_model(**user_data.dict())

        await user.create_default()
        await user.create()

        auth = auth_model(
            resumeID=user.id,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            patronymic=user_data.patronymic if user_data.patronymic is not None else None,
            email=user_data.email,
            hashed_password=hashed_password,
            salt=salt,
            phone_number=user_data.phone_number,
            role="Моряк",
            is_active=True,
            is_superuser=False,
            is_verified=False,
            date_joined=datetime.now(),
            token=tokenVal,
            telegram_id=user_data.telegram_id,
            vk_id=user_data.vk_id,
            is_vk=user_data.is_vk,
            is_tg=user_data.is_tg,
        )

        await auth.create()

        return user
    except HTTPException as e:
        raise HTTPException(detail=str(e), status_code=status.HTTP_400_BAD_REQUEST)


@router.post("/register/company", response_model=company_model, status_code=status.HTTP_201_CREATED,
             summary="Регистрация компании")
async def register_company(company_data: CompanyCreate):
    try:

        if await auth_model.find_one({"company_inn": company_data.company_inn}):

            raise HTTPException(status_code=status.HTTP_200_OK, detail="Пользователь с таким ИНН уже зарегистрирован.")

        if await auth_model.find_one({"email": company_data.email}):

            raise HTTPException(status_code=status.HTTP_200_OK, detail="Пользователь с таким email уже зарегистрирован.")

        if await auth_model.find_one({"phone_number": company_data.phone_number}):

            raise HTTPException(status_code=status.HTTP_200_OK, detail="Пользователь с таким номером телефона уже зарегистрирован.")

        if company_data.notification_settings.mailing_notification == False:

            raise HTTPException(status_code=status.HTTP_200_OK, detail="Вы не приняли условия пользовательского соглашения.")

        plen = len(company_data.password)
        if (plen < 7):

            raise HTTPException(status_code=status.HTTP_200_OK, detail="Слишком короткий пароль (мин. длина 8 символов).")

        if company_data.password != company_data.confirm_password:

            raise HTTPException(status_code=status.HTTP_200_OK, detail="Пароли не совпадают.")

        salt = generate_salt()
        hashed_password = hash_password(company_data.password, salt)
        tokenVal = hash_password(company_data.email, salt)

        company = company_model(**company_data.dict())


        await company.create()

        auth = auth_model(
            resumeID=company.id,
            first_name=company_data.first_name,
            last_name=company_data.last_name,
            patronymic=company_data.patronymic if company_data.patronymic is not None else None,
            email=company_data.email,
            hashed_password=hashed_password,
            salt=salt,
            inn=company_data.company_inn,
            phone_number=company_data.phone_number,
            role="Компания",
            is_active=True,
            is_superuser=False,
            is_verified=False,
            date_joined=datetime.now(),
            token=tokenVal,
            telegram_id=company_data.telegram_id,
            vk_id=company_data.vk_id,
            is_vk=company_data.is_vk,
            is_tg=company_data.is_tg,
        )

        await auth.create()

        return company

    except HTTPException as e:
        raise HTTPException(detail=str(e), status_code=status.HTTP_400_BAD_REQUEST)


@router.post("/token", response_model=Token,
             summary="Токен авторизации")
async def authenticate_user(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        service = AuthServices()

        user = await service.authenticate(form_data.username, form_data.password)

        if not user:

            raise HTTPException(detail="Неверный логин или пароль.", status_code=status.HTTP_401_UNAUTHORIZED)

        data_token = convert_objectid_to_str(user, AuthSchemas)
        jwt_token = generate_jwt_token(data_token)

#        salt = generate_salt()
#        tokenVal = hash_password(form_data.username, salt)

#        user_upd = await user_model.get(user['id'])

#        request = TokenUpdate()
#        request.token=tokenVal

#        request = {k: v for k, v in request.dict().items() if v is not None}

#        update_query = {"$set": {
#            field: value for field, value in request.items()
#        }}

#        user.update(update_query)


        return jwt_token

    except HTTPException as e:
        raise HTTPException(detail=str(e), status_code=status.HTTP_400_BAD_REQUEST)


@router.post("/refresh_token", response_model=Token,
             summary="Рефреш токен")
async def refresh_token_get(refresh_token: str = Depends(oauth2_scheme)):
    try:
        decoded_data = verify_jwt_token(refresh_token)

        service = AuthServices()

        if not decoded_data:
            raise HTTPException(status_code=400, detail="Invalid token")

        user = await service.find_user(decoded_data['sub'])

        if not user:

            raise HTTPException(status_code=401, detail="Invalid user or navy")

        token = generate_jwt_token(decoded_data)

        return token

    except HTTPException as e:
        raise HTTPException(detail=str(e), status_code=status.HTTP_400_BAD_REQUEST)


@router.post("/register/validate", response_model=company_model, status_code=status.HTTP_201_CREATED,
             summary="Валидация email")
async def validate_email(email: EmailValidate):
    try:
        service = AuthServices()

        user = await service.find_user_by_hash(email.hash)


        if company_data.password != company_data.confirm_password:

            raise HTTPException(status_code=status.HTTP_200_OK, detail="The passwords don't match")

        salt = generate_salt()
        hashed_password = hash_password(company_data.password, salt)

        company = company_model(**company_data.dict())

        await company.create()

        auth = auth_model(
            resumeID=company.id,
            first_name=company_data.first_name,
            last_name=company_data.last_name,
            patronymic=company_data.patronymic if company_data.patronymic is not None else None,
            email=company_data.email,
            hashed_password=hashed_password,
            salt=salt,
            inn=company_data.company_inn,
            phone_number=company_data.phone_number,
            role="Компания",
            is_active=True,
            is_superuser=False,
            is_verified=False,
            date_joined=datetime.now(),
        )

        await auth.create()

        return company

    except HTTPException as e:
        raise HTTPException(detail=str(e), status_code=status.HTTP_400_BAD_REQUEST)



@router.get("/vkuser", summary="Поиск user по vk")
async def get_available_vkusers(vk_id: str = '999999'):

    try:
        res = await auth_model.find({"vk_id": vk_id}).to_list()

        return {"data": len(res)}

    except HTTPException as e:

        return HTTPException(detail=e, status_code=status.HTTP_400_BAD_REQUEST)

@router.get("/tguser", summary="Поиск user по tg")
async def get_available_tgusers(tg_id: str = '999999'):

    try:
        res = await auth_model.find({"telegram_id": tg_id}).to_list()

        return {"data": len(res)}

    except HTTPException as e:

        return HTTPException(detail=e, status_code=status.HTTP_400_BAD_REQUEST)


@router.put("/company/profile", summary="Обновить информацию о компании")
async def update_company_profile(request: CompanyUpdateProfile, current_user: Optional[dict] = Depends(get_current_user)):

    try:

        if current_user is None or current_user['role'] != "Компания":
            return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

        company_id = current_user.get('id')

        account_info = await auth_model.get(company_id)
        company_info = await company_model.get(account_info.resumeID)




        if not company_info:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Company not found")

        update_query = {"$set": {
            "company_name": request.company_name,
            "company_address": request.company_address,
            "f_i_o": request.f_i_o,
            "email": request.email,
            "phone1": request.phone1,
            "phone2": request.phone2,
            "notification_settings": request.notification_settings,
            "photo_path": request.photo_path
        }}

        await company_info.update(update_query)

        return company_info

    except HTTPException as e:

        return HTTPException(detail=e, status_code=status.HTTP_400_BAD_REQUEST)


@router.get("/company/profile", summary="Информация о компании")
async def get_company_profile(current_user: Optional[dict] = Depends(get_current_user)):

    try:

        if current_user is None or current_user['role'] != "Компания":
            return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

        company_id = current_user.get('id')

        account_info = await auth_model.get(company_id)
        company_info = await company_model.get(account_info.resumeID)

        return company_info

    except HTTPException as e:

        return HTTPException(detail=e, status_code=status.HTTP_400_BAD_REQUEST)

@router.get("/user_profile_id", summary="Получить ID профиля")
async def get_user_profile_id(id: str):

    try:

        user = await auth_model.find_one({"_id": ObjectId(id)})
        return UserAuthResumeId(**user.dict())

    except HTTPException as e:

        return HTTPException(detail=e, status_code=status.HTTP_400_BAD_REQUEST)


# @router.post("/uploadfile/")
# async def create_upload_file(file: UploadFile):
#     return {"filename": file.filename}

class CustomFileLike:
    def __init__(self):
        self.content = ""

    def write(self, data):
        self.content = data

    def read(self):
        return self.content

    def close(self):
        pass  # No resource to release in this case

@router.post("/upload-cloud-file", summary="Загрузка файлов в облако")
#async def upload_cloud_file(file: UploadFile = File(...)):
    #contents = file.file.read()
async def upload_cloud_file(file: Annotated[bytes, File()]):
    #return {"file_read": file,"file_size": len(file)}
    #return {"file_size": len(file)}
    #files: List[UploadFile] = File(...)
    try:
        #return {"data": File(...).read()}
        PROJECT_ID = os.getenv('PROJECT_ID')
        TOKEN = os.getenv('TOKEN_S3')
        BUCKET = os.getenv('BUCKET_NAME')

        url = f"https://api.clo.ru/v2/projects/{PROJECT_ID}/s3/users"

        header = {'Content-Type': 'application/json', 'Authorization': f'Bearer {TOKEN}'}

        r = requests.get(url, headers=header)

        parse = r.json()

        object_id = parse['result'][0]['id']

        TOKEN = os.getenv('TOKEN_S3')

        url = f"https://api.clo.ru/v2/s3/users/{object_id}/credentials"

        r = requests.get(url=url, headers=header)

        #await file.read()
        #await file.read()
        #await temp_file = io.BytesIO()
        #await temp_file.write(contents)
        #await temp_file.seek(0)
        #await file.seek(0)
        access_key, secret_key = r.json()['result']['access_key'], r.json()['result']['secret_key']

        client_s3 = boto3.client(
            's3',
            endpoint_url="https://storage.clo.ru/{BUCKET}",
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
        )

        object_id = PydanticObjectId()
        folder_name = f"account_{object_id}/data/"
        file_key = f"{folder_name}{object_id}.jpg"


        try:
            #await file.seek(0)
            #fo = io.BytesIO(file)

            # Create a BytesIO object
            #file_like_object = io.BytesIO(file)

            # Write binary data
            #file_like_object.write(b"Hello, World!\n")
            #file_like_object.write(b"This is a file-like object.\n")

            # Get the content
            #content = file_like_object.getvalue()
            #print(content)

            # Don't forget to close it
            #file_like_object.close()

            # Example usage
            file_like_object = CustomFileLike()
            file_like_object.write(file)
            #print(file_like_object.read())
            #file_like_object.close()

            client_s3.upload_fileobj(
                file_like_object,
                str(BUCKET),
                file_key,
                ExtraArgs={'ACL': 'public-read'}
            )
        except (NoCredentialsError, PartialCredentialsError) as e:

            raise RuntimeError(f"S3 credentials are invalid or not provided: {e}")

        photo_path = f"https://{BUCKET}.storage.clo.ru/{BUCKET}/{file_key}"

        return {"data": photo_path}

    except HTTPException as e:
        raise HTTPException(detail=str(e), status_code=status.HTTP_400_BAD_REQUEST)
