from typing import Optional, List
from pydantic import BaseModel, EmailStr
from fastapi.security import OAuth2PasswordRequestForm


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


class UserAuthenticate(OAuth2PasswordRequestForm):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    info: dict


class CompanyCreate(BaseModel):
    email: EmailStr
    password: str
    confirm_password: str
    first_name: str
    last_name: str
    patronymic: Optional[str] = None
    phone_number: str
    company_name: str
    company_inn: int
    company_address: str
    telegram: Optional[str] = None
    notification_settings: NotificationSettings
