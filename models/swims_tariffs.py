from beanie import Document
from pydantic import BaseModel
from typing import Optional, List


class swims_tariffs(Document):
    status: str
    period: str
    cost: int


class list_description_tariffs(BaseModel):
    number: int
    description: str


class description_tariffs(Document):
    title: str
    description_list: Optional[List[list_description_tariffs]] = None
