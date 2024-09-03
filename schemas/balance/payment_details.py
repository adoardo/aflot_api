from pydantic import BaseModel
from typing import Optional
from beanie import PydanticObjectId
from datetime import datetime


class PaymentDetails(BaseModel):
    balance: float
    autofill: bool
    count_history: int


class PaymentHistory(BaseModel):
    id: Optional[PydanticObjectId] = None
    product: Optional[str] = None
    datetime: Optional[datetime] = None
    sum: Optional[float] = None
    method_of_payment: Optional[str] = None
    check: Optional[str] = None
