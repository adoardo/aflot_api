from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel, EmailStr
from beanie import PydanticObjectId

class VacanciesCompany(BaseModel):
    id: Optional[PydanticObjectId] = None
    position: str
    salary_from: Optional[int]
    salary_to: Optional[int]
    vessel: Optional[str]
    date_of_departure: date
    contract_duration: str

class VesselSchemas(BaseModel):
    id: Optional[PydanticObjectId] = None
    vessel_name: Optional[str] = None
    imo: Optional[str] = None
    ship_type: Optional[str] = None
    year_built: Optional[str] = None
    dwt: Optional[str] = None
    kw: Optional[str] = None
    length: Optional[str] = None
    width: Optional[str] = None
    is_active: Optional[bool] = False

class VacancySchemas(BaseModel):
    id: Optional[PydanticObjectId] = None
    position: str
    salary_from: Optional[int]
    salary_to: Optional[int]
    date_of_departure: Optional[date] = date.today()
    date_of_departure_from: Optional[date] = date.today()
    date_of_departure_to: Optional[date] = date.today()
    contract_duration: str
    contact_person: Optional[str]
    email: Optional[EmailStr]
    phone1: Optional[str]
    phone2: Optional[str]
    vessel: str
    responses: Optional[List[PydanticObjectId]]
    job_offers: Optional[List[PydanticObjectId]]
    approved_responses: Optional[List[PydanticObjectId]]
    approved_offers: Optional[List[PydanticObjectId]]
    is_publish: Optional[bool] = False
    is_active: Optional[bool] = False
    append_company: Optional[bool] = False
    created_at: Optional[datetime]
    view_count: Optional[int]

class CompanySchemas(BaseModel):
    id: Optional[PydanticObjectId]
    company_name: str
    vacancies: Optional[List[PydanticObjectId]]
    count_publications: int
    photo_path: Optional[str] = None

class VacanciesResponse(BaseModel):
    current_page: int
    total_pages: int
    vacancies: List[VacancySchemas]
    vessels: List[VesselSchemas]
    companies: List[CompanySchemas]

