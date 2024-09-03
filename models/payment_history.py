from datetime import datetime

from pydantic import Field
from beanie import Document, PydanticObjectId


class paymentHistory(Document):
    id: PydanticObjectId = Field(None, alias="_id")
    product: str = Field(None)
    amount: float = Field(None)
    date: datetime = Field(default=datetime.now())
    paymentMethod: str = Field(default="Visa/MC/MIR/UnionPay")
    receipt: str = Field(None)
    resumeID: PydanticObjectId = Field(None)
