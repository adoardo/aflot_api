from beanie import Document, PydanticObjectId
from pydantic import Field, EmailStr


class contact(Document):

    __collection__ = 'contacts'

    id: PydanticObjectId = Field(None, alias="_id")
    email: EmailStr
    phone_number: str
    whatsapp: str
    inn: int
    legal_address: str
    requisites: str


class feedback(Document):

    __collection__ = 'feedback'

    id: PydanticObjectId = Field(None, alias="_id")
    email: EmailStr
    phone_number: str
    name: str
    request: str
