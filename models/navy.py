from beanie import Document, PydanticObjectId
from pydantic import Field
from typing import Optional

class navy(Document):
    vessel_name: Optional[str] = None
    imo: Optional[str] = None
    ship_type: Optional[str] = None
    year_built: Optional[str] = None
    dwt: Optional[str] = None
    kw: Optional[str] = None
    length: Optional[str] = None
    width: Optional[str] = None
    is_active: Optional[bool] = False