from datetime import date, datetime
from beanie import Document, PydanticObjectId
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from models.db import db

class vacancy(Document):
    position: str
    salary_from: Optional[int]
    salary_to: Optional[int]
    date_of_departure: Optional[date] = date.today()
    date_of_departure_from: Optional[date] = date.today()
    date_of_departure_to: Optional[date] = date.today()
    contract_duration: Optional[str]
    contact_person: Optional[str]
    email: Optional[EmailStr]
    phone1: Optional[str]
    phone2: Optional[str]
    vessel: str
    responses: Optional[List[PydanticObjectId]] = None
    job_offers: Optional[List[PydanticObjectId]] = None
    approved_responses: Optional[List[PydanticObjectId]] = None
    approved_offers: Optional[List[PydanticObjectId]] = None
    is_publish: Optional[bool] = False
    is_active: Optional[bool] = False
    created_at: datetime = datetime.now()
    view_count: Optional[int] = 0