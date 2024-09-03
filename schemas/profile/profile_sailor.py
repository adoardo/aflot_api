from pydantic import BaseModel, EmailStr
from typing import Optional, List
from models.register import MainDocumentsUsers, ShipwrightsPapers, AdditionalDocuments, WorkExperience


class ProfileUserSchemas(BaseModel):
    email: EmailStr
    phone_number: str
    first_name: str
    last_name: str
    patronymic: Optional[str] = None
    country: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    telegram: Optional[str] = None
    positions: Optional[List[str]] = None
    worked: Optional[List[str]] = None
    main_documents: Optional[MainDocumentsUsers] = None
    shipwrights_papers: Optional[ShipwrightsPapers] = None
    additional_documents: Optional[AdditionalDocuments] = None
    working_experience: WorkExperience
