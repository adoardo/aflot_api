from pydantic import BaseModel


class PaymentCreateSchemas(BaseModel):
    description: str
    amount: float
