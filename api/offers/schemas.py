from pydantic import BaseModel, EmailStr
from typing import Optional, List
from beanie import PydanticObjectId
from datetime import date


class OffersSailor(BaseModel):
    id: PydanticObjectId
    position: str
    date_of_departure: date
    ship_name: str
    salary: str
    contract_duration: str


class OffersCompanyInfo(BaseModel):
    id: PydanticObjectId
    company_name: str
    photo_path: Optional[str] = None


class ResponsesOffers(BaseModel):
    offers: OffersSailor
    companyInfo: OffersCompanyInfo


class Response(BaseModel):
    offers: Optional[List[ResponsesOffers]] = None
    countIncoming: str


class OfferID(BaseModel):
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
    status: str
    email: Optional[EmailStr] = None
    dwt: int
    kw: int
    length: int
    width: int
    phone1: str
    phone2: Optional[str] = None
