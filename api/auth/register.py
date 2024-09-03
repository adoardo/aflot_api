from datetime import datetime
from fastapi import APIRouter
from fastapi import Depends, HTTPException
from models.register import user_model, company_model
from models.auth import auth as auth_model
from .config import (generate_jwt_token, generate_salt, hash_password, oauth2_scheme,
                     verify_jwt_token, convert_objectid_to_str)
from schemas.auth.auth import UserCreate, CompanyCreate
from starlette import status
from api.auth.auth import AuthServices, AuthSchemas
from schemas.auth.auth import Token
from fastapi.security import OAuth2PasswordRequestForm
from beanie import PydanticObjectId

router = APIRouter()


@router.post("/register/user", response_model=user_model, status_code=status.HTTP_201_CREATED,
             summary="Регистрация моряка")
async def register_user(user_data: UserCreate):
    try:

        if await auth_model.find_one({"email": user_data.email}):

            raise HTTPException(status_code=status.HTTP_200_OK, detail="Email already exists")

        if await auth_model.find_one({"phone_number": user_data.phone_number}):

            raise HTTPException(status_code=status.HTTP_200_OK, detail="Phone number already exists")

        if user_data.password != user_data.confirm_password:

            raise HTTPException(status_code=status.HTTP_200_OK, detail="The passwords don't match")

        salt = generate_salt()
        hashed_password = hash_password(user_data.password, salt)

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
        )

        await auth.create()

        return user
    except HTTPException as e:
        raise HTTPException(detail=str(e), status_code=status.HTTP_400_BAD_REQUEST)


@router.post("/register/company", response_model=company_model, status_code=status.HTTP_201_CREATED,
             summary="Регистрация компании")
async def register_company(company_data: CompanyCreate):
    try:

        if await auth_model.find_one({"email": company_data.email}):

            raise HTTPException(status_code=status.HTTP_200_OK, detail="Email already exists")

        if await auth_model.find_one({"phone_number": company_data.phone_number}):

            raise HTTPException(status_code=status.HTTP_200_OK, detail="Phone number already exists")

        if await auth_model.find_one({"company_inn": company_data.company_inn}):

            raise HTTPException(status_code=status.HTTP_200_OK, detail="INN already exists")

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


@router.post("/token", response_model=Token,
             summary="Токен авторизации")
async def authenticate_user(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        service = AuthServices()

        user = await service.authenticate(form_data.username, form_data.password)

        if not user:

            raise HTTPException(detail="Invalid username or password", status_code=status.HTTP_401_UNAUTHORIZED)

        data_token = convert_objectid_to_str(user, AuthSchemas)
        jwt_token = generate_jwt_token(data_token)

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
