from datetime import date, datetime
from schemas.auth.auth import Optional
from models.db import db
from pydantic import BaseModel, EmailStr, Field
from typing import List
from beanie import PydanticObjectId, Indexed, Document


class WorkExperienceNew(BaseModel):
    shipowner: Optional[str] = None
    type_of_vessel: Optional[str] = None
    ships_name: Optional[str] = None
    position: Optional[str] = None
    period_of_work_from: Optional[date] = None
    period_of_work_to: Optional[date] = None


class NotificationSettings(BaseModel):
    send_email: bool = False
    send_sms: bool = False
    send_telegram: bool = False
    mailing_notification: bool = False


class History(BaseModel):
    id: Optional[PydanticObjectId] = None
    product: Optional[str] = None
    datetime: Optional[datetime] = None
    sum: Optional[float] = None
    method_of_payment: Optional[str] = None
    check: Optional[str] = None


class FavoritesCompany(BaseModel):
    id: PydanticObjectId

class BlackList(BaseModel):
    sailor_id: PydanticObjectId
    created_at: datetime = datetime.now()
    comment: Optional[str]

class FavoritesVacancies(BaseModel):
    id: PydanticObjectId


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


class user_model(Document):
    __database__ = db

    id: PydanticObjectId = Field(None, alias="_id")
    email: Indexed(EmailStr, unique=True)
    phone_number: Indexed(str, unique=True)
    first_name: str
    last_name: str
    patronymic: Optional[str] = None
    photo_path: Optional[str] = None
    country: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    birth_date: Optional[date] = None
    telegram: Optional[str] = None
    positions: Optional[List[str]] = None
    worked: Optional[List[str]] = None
    status: Optional[str] = None
    salary: Optional[float] = 0
    balance: Optional[float] = 0
    autofill: Optional[bool] = False
    payment_history: Optional[List[History]] = None
    favorite_companies: Optional[List[PydanticObjectId]] = Field(default_factory=list)
    favorite_vacancies: Optional[List[PydanticObjectId]] = Field(default_factory=list)
    notification_settings: NotificationSettings
    main_documents: Optional[MainDocumentsUsers] = None
    shipwrights_papers: Optional[ShipwrightsPapers] = None
    additional_documents: Optional[AdditionalDocuments] = None
    working_experience: Optional[WorkExperience] = None
    responses: Optional[List[PydanticObjectId]] = Field(default_factory=list)
    offers: Optional[List[PydanticObjectId]] = None
    working_experience_new: Optional[List[WorkExperienceNew]] = []
    media_files: Optional[List[str]] = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

    def process_item_list(positions: List[str]):
        pass

    async def create_default(self):
        self.main_documents = MainDocumentsUsers(
            foreign_passport=None,
            seafarers_ID_card=None,
            diploma=None,
            initial_safety_training=None,
            designated_safeguarding_responsibilities=None,
            dinghy_and_raft_specialist=None,
            fighting_fire_with_an_expanded_program=None,
            providing_first_aid=None,
            prevention_of_marine_pollution=None,
            tanker_certificate=None,
            occupational_health_and_safety=None,
            medical_commission=None,
        )

        self.shipwrights_papers = ShipwrightsPapers(
            gmssb=None,
            eknis=None,
            rlt=None,
            sarp=None,
        )

        self.additional_documents = AdditionalDocuments(
            isolation_breathing_apparatus=None,
            naval_training=None,
            transportation_safety=None,
            tanker_certificate=None,
        )



class company_model(Document):
    __database__ = db

    id: PydanticObjectId = Field(None, alias="_id")
    email: Optional[str]
    phone_number: Optional[str] = None
    phone1: Optional[str] = None
    phone2: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    patronymic: Optional[str] = None
    f_i_o: Optional[str] = None
    photo_path: Optional[str] = None
    telegram: Optional[str] = None
    company_name: Optional[str] = None
    company_inn: Indexed(str, unique=True)
    company_address: Optional[str] = None
    autofill: Optional[bool] = False
    payment_history: Optional[List[History]] = None
    balance: Optional[float] = 0
    vessel: Optional[List[PydanticObjectId]] = []
    favorites_resume: Optional[List[PydanticObjectId]] = None
    black_list: Optional[List[BlackList]] = None
    vacancies: Optional[List[PydanticObjectId]] = None
    notification_settings: NotificationSettings
    count_publications: int = Field(default=0)
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()