from datetime import date
from beanie import Document, PydanticObjectId
from typing import Optional, List
from pydantic import EmailStr

class ship_model(Document):
    position: str
    salary_RUB: Optional[str]
    salary_USD: Optional[str]
    date_of_departure: Optional[date] = date.today()
    contract_duration: str
    ship_name: str
    imo: Optional[str]
    ship_type: str
    year_built: int
    contact_person: str
    status: str
    email: Optional[EmailStr]
    dwt: int
    kw: int
    length: int
    width: int
    phone1: str
    phone2: Optional[str]
    responses: Optional[List[PydanticObjectId]]
    job_offers: Optional[List[PydanticObjectId]]
