from beanie import Document, PydanticObjectId
from pydantic import Field
from typing import Optional


class navy(Document):
    id: PydanticObjectId = Field(None, alias="_id")
    ship_name: str
    imo: Optional[str] = None
    ship_type: str
    year_built: str
    dwt: str
    kw: str
    length: str
    width: str


class moderation_navy(Document):
    ship_name: str
    imo: str
    ship_type: str
    year_built: str
    dwt: str
    kw: str
    length: str
    width: str
    company_id: PydanticObjectId
    is_active: bool = False
