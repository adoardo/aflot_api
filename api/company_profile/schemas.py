from pydantic import BaseModel
from typing import List
from beanie import PydanticObjectId


class NewShipSchema(BaseModel):
    vessel_name: str
    imo: str
    ship_type: str
    year_built: str
    dwt: str
    kw: str
    length: str
    width: str


class MyNavy(BaseModel):
    id: PydanticObjectId
    vessel_name: str
    imo: str
    ship_type: str
    year_built: str


class ResponseMyNavy(BaseModel):
    myNavy: List[MyNavy] = []
    moderationNavy: List[MyNavy] = []
