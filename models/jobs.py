from beanie import Document, PydanticObjectId
from pydantic import Field
from models.db import db
from typing import Optional, List, Literal
from datetime import date
from pydantic import EmailStr, BaseModel

class ship(Document):
    __database__ = db

    id: Optional[PydanticObjectId] = Field(None, alias="_id")
    position: Optional[str] = None
    salary_RUB: Optional[str] = None
    salary_USD: Optional[str] = None
    date_of_departure: Optional[date] = None
    contract_duration: Optional[str] = None
    ship_name: Optional[str] = None
    imo: Optional[str] = None
    ship_type: Optional[str] = None
    year_built: Optional[int] = 0
    contact_person: Optional[str] = None
    status: Optional[str] = None
    email: Optional[EmailStr] = None
    dwt: Optional[int] = 0
    kw: Optional[int] = 0
    length: Optional[int] = 0
    width: Optional[int] = 0
    phone1: Optional[str] = None
    phone2: Optional[str] = None
    responses: Optional[List[PydanticObjectId]] = None
    job_offers: Optional[List[PydanticObjectId]] = None
