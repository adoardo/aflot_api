from pydantic import BaseModel
from datetime import date
from typing import List, Optional
from beanie import PydanticObjectId


class Vacancy(BaseModel):
    id: PydanticObjectId
    position: str
    salary: str
    ship_name: str
    date_of_departure: Optional[date] = date.today()
    contract_duration: str


class SearchVacanciesResponse(BaseModel):
    vacancies: List[Vacancy]
    total_pages: int
    current_page: int
