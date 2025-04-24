from beanie import Document, PydanticObjectId
from pydantic import Field
from typing import Optional, List

class settings_global(Document):
    option_name: str
    option_slug: str
    option_values: List[str]