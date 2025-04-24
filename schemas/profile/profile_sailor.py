from pydantic import BaseModel, EmailStr
from typing import Optional, List
from models.register import MainDocumentsUsers, ShipwrightsPapers, AdditionalDocuments, WorkExperience
from datetime import date, datetime
from beanie import PydanticObjectId

class MainDocumentsUsers(BaseModel):
    foreign_passport: Optional[date] = None
    seafarers_ID_card: Optional[str] = None
    diploma: Optional[date] = None
    initial_safety_training: Optional[str] = None
    designated_safeguarding_responsibilities: Optional[str] = None
    dinghy_and_raft_specialist: Optional[str] = None
    fighting_fire_with_an_expanded_program: Optional[str] = None
    providing_first_aid: Optional[str] = None
    prevention_of_marine_pollution: Optional[str] = None
    tanker_certificate: Optional[str] = None
    occupational_health_and_safety: Optional[str] = None
    medical_commission: Optional[str] = None

class ShipwrightsPapers(BaseModel):
    gmssb: Optional[date] = None
    eknis: Optional[str] = None
    rlt: Optional[date] = None
    sarp: Optional[str] = None

class UserNotification(BaseModel):
    send_email: bool
    send_sms: bool
    send_telegram: bool
    mailing_notification: Optional[bool]

class AdditionalDocuments(BaseModel):
    isolation_breathing_apparatus: Optional[date] = None
    naval_training: Optional[str] = None
    transportation_safety: Optional[date] = None
    tanker_certificate: Optional[str] = None

class WorkExperience(BaseModel):
    shipowner: Optional[str] = None
    type_of_vessel: Optional[str] = None
    ships_name: Optional[str] = None
    position: Optional[str] = None
    period_of_work_from: Optional[date] = None
    period_of_work_to: Optional[date] = None

class WorkExperienceNew(BaseModel):
    shipowner: Optional[str] = None
    type_of_vessel: Optional[str] = None
    ships_name: Optional[str] = None
    position: Optional[str] = None
    period_of_work_from: Optional[date] = None
    period_of_work_to: Optional[date] = None

class ProfileUserSchemas(BaseModel):
    photo_path: Optional[str] = None
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
    salary: Optional[float] = 0
    main_documents: Optional[MainDocumentsUsers] = None
    shipwrights_papers: Optional[ShipwrightsPapers] = None
    additional_documents: Optional[AdditionalDocuments] = None
    working_experience: Optional[WorkExperience] = None
    birth_date: Optional[date] = None
    main_documents: Optional[MainDocumentsUsers] = None
    additional_documents: Optional[AdditionalDocuments] = None
    shipwrights_papers: Optional[ShipwrightsPapers] = None
    notification_settings: Optional[UserNotification] = None
    working_experience_new: Optional[List[WorkExperienceNew]] = []
    media_files: Optional[List[str]] = None

