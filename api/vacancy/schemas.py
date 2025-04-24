from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import date
from beanie import PydanticObjectId

class VacancyRead(BaseModel):
    id: PydanticObjectId
    position: str
    vessel: str

class Salary(BaseModel):
    From: Optional[str] = None
    To: Optional[str] = None

class VacancySchemas(BaseModel):
    position: str
    salary_from: Optional[int]
    salary_to: Optional[int]
    date_of_departure: Optional[date] = date.today()
    contract_duration: str
    contact_person: Optional[str]
    email: Optional[EmailStr]
    phone1: Optional[str]
    phone2: Optional[str]
    vessel: str
    responses: Optional[List[PydanticObjectId]]
    job_offers: Optional[List[PydanticObjectId]]
    is_publish: Optional[bool] = False
    is_active: Optional[bool] = False

class ResponseCount(BaseModel):
    responseCount: int

class VacanciesResponse(BaseModel):
    vacancies: VacancySchemas
    responseCount: ResponseCount








class NavySchemas(BaseModel):
    id: Optional[PydanticObjectId] = None
    ship_name: Optional[str] = None
    imo: Optional[str] = None
    ship_type: Optional[str] = None
    year_built: Optional[str] = None
    dwt: Optional[str] = None
    kw: Optional[str] = None
    length: Optional[str] = None
    width: Optional[str] = None


class ResponseNavySchemas(BaseModel):
    companyNavy: List[NavySchemas] = None
    navy: List[NavySchemas] = None