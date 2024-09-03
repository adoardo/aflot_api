from pydantic import BaseModel, EmailStr


class ContactSchema(BaseModel):
    email: EmailStr
    name: str
    phone_number: str
    request: str
