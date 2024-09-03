from pydantic import BaseModel
from beanie import Document
from typing import Optional, List


class tariffs(BaseModel):
    title: str
    count_publications: int
    count_possibilities: int
    price: int


class company_tariffs(Document):
    description: Optional[List[tariffs]] = None
