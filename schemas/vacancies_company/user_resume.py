from pydantic import BaseModel, Field, EmailStr
from beanie import PydanticObjectId
from typing import Optional, List


class Resume(BaseModel):
    id: PydanticObjectId
    email: EmailStr
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
    status: Optional[str] = None
