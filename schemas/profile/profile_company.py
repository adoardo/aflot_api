from pydantic import BaseModel, EmailStr
from typing import List, Optional, Union


class CompanyNotification(BaseModel):
    send_email: bool
    send_sms: bool
    send_telegram: bool
    mailing_notification: Optional[bool]


class CompanyOldSettings(BaseModel):
    email: EmailStr
    phone_number: str
    telegram: Optional[str]
    notification_settings: Optional[CompanyNotification]


class CompanySchema(BaseModel):
    email: EmailStr
    phone_number: str
    first_name: str
    last_name: str
    patronymic: Optional[str] = None
    photo_path: Optional[str] = None
    telegram: Optional[str] = None
    company_name: str
    company_inn: int
    company_address: str