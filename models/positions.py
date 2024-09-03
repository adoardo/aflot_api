from beanie import Document, PydanticObjectId
from pydantic import Field


class position(Document):
    id: PydanticObjectId = Field(None, alias="_id")
    position_name: str
