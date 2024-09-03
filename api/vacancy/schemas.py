from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date
from beanie import PydanticObjectId


class ShipRead(BaseModel):
    id: PydanticObjectId
    position: str
    ship_name: str


class ShipSalary(BaseModel):
    salaryFrom: Optional[str] = None
    salaryTo: Optional[str] = None


class Ship(BaseModel):
    position: str
    salary: Optional[ShipSalary] = None
    date_of_departure: Optional[date] = date.today()
    contract_duration: str
    ship_name: str
    imo: Optional[str] = None
    ship_type: str
    year_built: int
    contact_person: str
    status: Optional[str] = None
    email: Optional[EmailStr] = None
    dwt: int
    kw: int
    length: int
    width: int
    phone1: str
    phone2: Optional[str] = None


class ResponseCount(BaseModel):
    responseCount: int


class Vacancies(BaseModel):
    id: PydanticObjectId
    position: str
    salary: str
    date_of_departure: Optional[date] = date.today()
    contract_duration: str
    ship_name: str
    imo: Optional[str] = None
    ship_type: str
    year_built: int
    contact_person: str
    status: Optional[str] = None
    email: Optional[EmailStr] = None
    dwt: int
    kw: int
    length: int
    width: int
    phone1: str
    phone2: Optional[str] = None


class VacanciesResponse(BaseModel):
    vacancies: Vacancies
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


class CompanyNavySchemas(BaseModel):
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
    companyNavy: List[CompanyNavySchemas] = None
    navy: List[NavySchemas] = None
