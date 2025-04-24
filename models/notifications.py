from beanie import Document
from typing import Optional, List

class notifications(Document):
    user_id: Optional[str] = None
    guests: List[object] = List