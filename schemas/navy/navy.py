from pydantic import BaseModel
from typing import Optional

class NavyCreate(BaseModel):
    vessel_name: str
    imo: str
    ship_type: str
    year_built: str
    dwt: str
    kw: str
    length: str
    width: str
    is_active: bool = False
    company_email: Optional[str]
    append_company: Optional[bool] = True
