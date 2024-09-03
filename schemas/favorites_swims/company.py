from beanie import PydanticObjectId
from pydantic import BaseModel


class CompanyFavoritesSchemas(BaseModel):
    id: PydanticObjectId
    company_name: str
    company_address: str
    date_joined: str
    active_vacancy: int
