from pydantic import BaseModel
from beanie import Document
from typing import Optional, List

class company_tariffs(Document):
    title: Optional[str]
    count_publications: Optional[int]
    count_possibilities: Optional[int]
    price: Optional[int]
    additional: Optional[bool]
