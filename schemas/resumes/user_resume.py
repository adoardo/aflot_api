from pydantic import BaseModel
from typing import Optional, List
from beanie import PydanticObjectId


class UserResume(BaseModel):
    id: PydanticObjectId
    first_name: str
    last_name: str
    patronymic: Optional[str] = None
    photo_path: Optional[str] = None
    country: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    worked: Optional[List[str]] = None
    status: Optional[str] = None


class UserResumeResponse(BaseModel):
    current_page: int
    total_page: int
    vacancies: List[UserResume]


class PostAJobsRequest(BaseModel):
    id: PydanticObjectId
