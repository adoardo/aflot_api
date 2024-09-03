from pydantic import BaseModel


class PaymentSchemas(BaseModel):
    description: str
    amount: int
