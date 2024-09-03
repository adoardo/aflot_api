from pydantic import BaseModel
from beanie import PydanticObjectId


class CompanyInfo(BaseModel):
    id: PydanticObjectId
    company_name: str
    photo_path: str


class NavyInfo(BaseModel):
    id: PydanticObjectId
    ship_name: str
    ship_type: str
    year_built: str
    dwt: str
    imo: str


class ResponseNavy(BaseModel):
    companyInfo: CompanyInfo
    navyInfo: NavyInfo
    openVacancy: int
