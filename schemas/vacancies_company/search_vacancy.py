from pydantic import BaseModel
from datetime import date
from typing import List, Optional
from beanie import PydanticObjectId


class SearchVacancy(BaseModel):
    id: PydanticObjectId
    position: str
    salary: Optional[int]
    salary: Optional[int]
    vessel: str
    date_of_departure: Optional[date] = date.today()
    contract_duration: str


class SearchVacanciesResponse(BaseModel):
    vacancies: List[SearchVacancy]
    total_pages: int
    current_page: int
