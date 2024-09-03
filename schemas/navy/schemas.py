from pydantic import BaseModel
from beanie import PydanticObjectId


class CompanyInfo(BaseModel):
    id: PydanticObjectId
    name: str


class NavySchema(BaseModel):
    ship_name: str
    imo: str
    photo_path: str
    ship_type: str
    year_built: str
    dwt: str
    active_vacancy: int
    company_info: CompanyInfo
