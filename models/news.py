from datetime import date
from beanie import Document, PydanticObjectId
from typing import Optional


class news_model(Document):
    title: str
    content: str
    created_at: Optional[date] = None
    photo: Optional[PydanticObjectId] = None
    photo_path: Optional[str] = None
    view_count: Optional[int] = None
