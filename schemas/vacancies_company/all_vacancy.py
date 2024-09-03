from typing import List, Optional
from datetime import date
from pydantic import BaseModel
from beanie import PydanticObjectId


class SalarySchema(BaseModel):
    salaryFrom: str
    salaryTo: str


class VacanciesCompany(BaseModel):
    id: Optional[PydanticObjectId] = None
    position: Optional[str] = None
    salary: Optional[SalarySchema] = None
    ship_name: Optional[str] = None
    date_of_departure: Optional[date] = date.today()
    contract_duration: Optional[str] = None


class VacanciesResponse(BaseModel):
    current_page: int
    total_pages: int
    vacancies: List[VacanciesCompany]
