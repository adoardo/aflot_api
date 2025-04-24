from beanie import Document
from pydantic import BaseModel
from typing import Optional, List


class swims_tariffs(Document):
    title: Optional[str]
    period: Optional[str]
    cost: Optional[int]
    description_list: Optional[List[str]] = None


class list_description_tariffs(BaseModel):
    number: int
    description: str


class description_tariffs(Document):
    title: str
    description_list: Optional[List[list_description_tariffs]] = None
