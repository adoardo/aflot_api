from beanie import Document, PydanticObjectId
from pydantic import Field


class vessel(Document):
    id: PydanticObjectId = Field(None, alias="_id")
    vessel_name: str
