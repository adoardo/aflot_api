from datetime import datetime
from beanie import Document, Indexed, PydanticObjectId
from pydantic import EmailStr, Field, BaseModel
from typing import Optional, List


class auth(Document):
    __collection__ = 'auth'

    id: PydanticObjectId = Field(None, alias="_id")
    resumeID: PydanticObjectId = Field(None, alias="resumeID")
    first_name: str
    last_name: str
    patronymic: Optional[str] = None
    email: Indexed(EmailStr, unique=True)
    inn: Optional[int] = None
    phone_number: Indexed(str, unique=True)
    hashed_password: str
    role: str
    is_active: bool
    is_superuser: bool
    is_verified: bool
    last_login: Optional[datetime] = None
    date_joined: datetime
    salt: str
    token: Optional[str] = None
    telegram_id: Optional[str] = None
    vk_id: Optional[str] = None
    is_vk: Optional[bool] = None
    is_tg: Optional[bool] = None
