from typing import Optional, List
from pydantic import BaseModel, EmailStr
from fastapi.security import OAuth2PasswordRequestForm
from beanie import PydanticObjectId
from datetime import date, datetime

class NotificationSettings(BaseModel):
    send_email: bool = False
    send_sms: bool = False
    send_telegram: bool = False
    mailing_notification: bool = False


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    confirm_password: str
    phone_number: str
    first_name: str
    last_name: str
    patronymic: Optional[str] = None
    country: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    telegram: Optional[str] = None
    positions: Optional[List[str]] = None
    worked: Optional[List[str]] = None
    notification_settings: NotificationSettings
    telegram_id: Optional[str] = None
    vk_id: Optional[str] = None
    is_vk: Optional[bool] = None
    is_tg: Optional[bool] = None


class UserAuthenticate(OAuth2PasswordRequestForm):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    info: dict


class CompanyCreate(BaseModel):
    photo_path: Optional[str] = None
    email: EmailStr
    password: str
    confirm_password: str
    first_name: str
    last_name: str
    patronymic: Optional[str] = None
    f_i_o: str
    phone_number: str
    phone1: Optional[str]
    phone2: Optional[str]
    company_name: str
    company_inn: str
    company_address: str
    telegram: Optional[str] = None
    notification_settings: NotificationSettings
    telegram_id: Optional[str] = None
    vk_id: Optional[str] = None
    is_vk: Optional[bool] = None
    is_tg: Optional[bool] = None

class EmailValidate(BaseModel):
    hash: str

class TokenUpdate(BaseModel):
    token: Optional[str] = None

class CompanyUpdateProfile(BaseModel):
    photo_path: Optional[str] = None
    company_name: Optional[str]
    company_inn: Optional[str]
    company_address: Optional[str]
    f_i_o: Optional[str]
    email: Optional[str]
    phone1: Optional[str]
    phone2: Optional[str]
    notification_settings: NotificationSettings


class UserAuthResumeId(BaseModel):
    id: Optional[PydanticObjectId]
    resumeID: Optional[PydanticObjectId]

class BlackListComment(BaseModel):
    sailor_id: Optional[PydanticObjectId]
    created_at: Optional[datetime]
    comment: Optional[str]