from datetime import date
from beanie import PydanticObjectId
from pydantic import BaseModel
from typing import Optional
import base64


class ImageInfo(BaseModel):
    width: int
    height: int
    format: str
    filename: str
    contentType: str
    chunkSize: int
    length: int


class ImageData(BaseModel):
    files_id: PydanticObjectId
    photo_path: str = None


class NewsSchema(BaseModel):
    title: str
    content: str
    created_at: Optional[date]
    view_count: int

