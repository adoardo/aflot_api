import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from mongoengine import (Document, EmailField, IntField, StringField, DateTimeField, BooleanField, DateField,
                         EmbeddedDocument, EmbeddedDocumentField, ListField, ImageField, FloatField, FileField)
from mongoengine.fields import ObjectIdField
from beanie import PydanticObjectId
import os
import requests
from dotenv import load_dotenv

from typing import Literal, Union

import logging
def get_module_logger(mod_name):
    """
    To use this, do logger = get_module_logger(__name__)
    """
    logger = logging.getLogger(mod_name)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s [%(name)-12s] %(levelname)-8s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    return logger

load_dotenv()

class Auth(Document):
    resumeID = ObjectIdField()
    email = EmailField(unique=True)
    first_name = StringField(verbose_name="Имя")
    last_name = StringField()
    patronymic = StringField()
    inn = IntField()
    phone_number = StringField(unique=True)
    hashed_password = StringField()
    role = StringField()
    is_active = BooleanField()
    is_superuser = BooleanField()
    is_verified = BooleanField()
    last_login = DateTimeField()
    date_joined = DateTimeField()
    salt = StringField()
    token = StringField()
    telegram_id = StringField()
    vk_id = StringField()
    is_vk = BooleanField()
    is_tg = BooleanField()

class Salary(EmbeddedDocument):
    From = StringField()
    To = StringField()

class Vacancy(Document):
    position = StringField(verbose_name="Позиция")
    salary = Salary
    date_of_departure = DateField()
    contract_duration = StringField()
    vessel_name = StringField()
    imo = StringField()
    ship_type = StringField()
    year_built = IntField()
    contact_person = StringField()
    email = EmailField()
    dwt = IntField()
    kw = IntField()
    length = IntField()
    width = IntField()
    phone1 = StringField()
    phone2 = StringField()
    responses = ListField(ObjectIdField())
    job_offers = ListField(ObjectIdField())
    is_publish = BooleanField(default=False)
    is_active = BooleanField(default=False)


class BlackList(EmbeddedDocument):
    id = ObjectIdField()


class Favorites(EmbeddedDocument):
    id = ObjectIdField()


class FavoritesCompany(EmbeddedDocument):
    id = ObjectIdField()


class FavoritesVacancies(EmbeddedDocument):
    id = ObjectIdField()


class NotificationSettings(EmbeddedDocument):
    send_email = BooleanField()
    send_sms = BooleanField()
    send_telegram = BooleanField()
    mailing_notification = BooleanField()


class MainDocumentsUsers(EmbeddedDocument):
    foreign_passport = DateField()
    seafarers_ID_card = StringField()
    diploma = DateField()
    initial_safety_training = StringField()
    designated_safeguarding_responsibilities = StringField()
    dinghy_and_raft_specialist = StringField()
    fighting_fire_with_an_expanded_program = StringField()
    providing_first_aid = StringField()
    prevention_of_marine_pollution = StringField()
    tanker_certificate = StringField()
    occupational_health_and_safety = StringField()
    medical_commission = StringField()


class ShipwrightsPapers(EmbeddedDocument):
    gmssb = DateField()
    eknis = StringField()
    rlt = DateField()
    sarp = StringField()


class AdditionalDocuments(EmbeddedDocument):
    isolation_breathing_apparatus = DateField()
    naval_training = StringField()
    transportation_safety = DateField()
    tanker_certificate = StringField()


class WorkExperience(EmbeddedDocument):
    shipowner = StringField()
    type_of_vessel = StringField()
    ships_name = StringField()
    position = StringField()
    period_of_work_from = DateField()
    period_of_work_to = DateField()


class History(EmbeddedDocument):
    id = ObjectIdField()
    product = StringField()
    datetime = DateTimeField()
    sum = FloatField()
    method_of_payment = StringField()
    check = StringField()

class WorkExperienceNew(EmbeddedDocument):
    shipowner = StringField()
    type_of_vessel = StringField()
    ships_name = StringField()
    position = StringField()
    period_of_work_from = DateField()
    period_of_work_to = DateField()



class UserModel(Document):
    email = EmailField(unique=True)
    phone_number = StringField(unique=True)
    first_name = StringField()
    last_name = StringField()
    patronymic = StringField()
    photo = ImageField()
    photo_path = StringField()
    country = StringField()
    region = StringField()
    city = StringField()
    birth_date = DateField(default=None)
    telegram = StringField()
    positions = ListField(StringField())
    worked = ListField(StringField())
    status = StringField()
    balance = FloatField()
    autofill = BooleanField()
    payment_history = ListField(EmbeddedDocumentField(History))
    favorites_company = ListField(EmbeddedDocumentField(FavoritesCompany))
    favorites_vacancies = ListField(EmbeddedDocumentField(FavoritesVacancies))
    notification_settings = EmbeddedDocumentField(NotificationSettings)
    main_documents = EmbeddedDocumentField(MainDocumentsUsers)
    shipwrights_papers = EmbeddedDocumentField(ShipwrightsPapers)
    additional_documents = EmbeddedDocumentField(AdditionalDocuments)
    working_experience = EmbeddedDocumentField(WorkExperience)
    responses = ListField(ObjectIdField())
    offers = ListField(ObjectIdField())
    working_experience_new = ListField(EmbeddedDocumentField(WorkExperienceNew))
    view_count = FloatField()
    media_files = ListField(StringField())

    def save(self, *args, **kwargs):
        self.photo.read()

        BUCKET_NAME = os.getenv('BUCKET_NAME')
        if self.photo:

            access_key, secret_key = self.get_s3_credentials_for_user()

            client_s3 = boto3.client(
                's3',
                endpoint_url="https://storage.clo.ru/s3-user-e5a009-default-bucket",
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
            )

            object_id = PydanticObjectId()
            folder_name = f"news_{object_id}/photo/"
            file_key = f"{folder_name}{object_id}.jpg"

            try:
                self.photo.seek(0)
                client_s3.upload_fileobj(
                    self.photo,
                    str(BUCKET_NAME),
                    file_key,
                    ExtraArgs={'ACL': 'public-read'}
                )
            except (NoCredentialsError, PartialCredentialsError) as e:

                raise RuntimeError(f"S3 credentials are invalid or not provided: {e}")

            self.photo_path = f"https://{BUCKET_NAME}.storage.clo.ru/{BUCKET_NAME}/{file_key}"

        elif self.photo_path:
            # self.delete_photo_from_s3(self.photo_path)
            self.photo_path = None
        super(UserModel, self).save(*args, **kwargs)

    def get_user_s3_for_user(self):

        PROJECT_ID = os.getenv('PROJECT_ID')
        TOKEN = os.getenv('TOKEN_S3')

        url = f"https://api.clo.ru/v2/projects/{PROJECT_ID}/s3/users"

        header = {'Content-Type': 'application/json', 'Authorization': f'Bearer {TOKEN}'}

        r = requests.get(url, headers=header)

        if r.status_code != 200:
            return r.json()

        parse = r.json()

        return parse['result'][0]['id']

    def get_s3_credentials_for_user(self):
        object_id = self.get_user_s3_for_user()
        TOKEN = os.getenv('TOKEN_S3')

        url = f"https://api.clo.ru/v2/s3/users/{object_id}/credentials"

        header = {'Content-Type': 'application/json', 'Authorization': f'Bearer {TOKEN}'}

        r = requests.get(url=url, headers=header)

        access_key, secret_key = r.json()['result']['access_key'], r.json()['result']['secret_key']

        return access_key, secret_key


class CompanyModel(Document):
    email = StringField()
    phone_number = StringField(unique=True)
    phone1 = StringField()
    phone2 = StringField()
    first_name = StringField()
    last_name = StringField()
    patronymic = StringField()
    f_i_o = StringField()
    photo = ImageField()
    photo_path = StringField()
    telegram = StringField()
    company_name = StringField()
    company_inn = StringField(unique=True)
    company_address = StringField()
    autofill = BooleanField(default=False)
    payment_history = ListField(EmbeddedDocumentField(History))
    balance = FloatField(default=0.0)
    vessel = ListField(StringField())
    favorites_resume = ListField(ObjectIdField())
    black_list_resume = ListField(ObjectIdField())
    vacancies = ListField(ObjectIdField())
    notification_settings = EmbeddedDocumentField(NotificationSettings)
    count_publications = IntField()

    def save(self, *args, **kwargs):
        self.photo.read()

        BUCKET_NAME = os.getenv('BUCKET_NAME')
        if self.photo:

            access_key, secret_key = self.get_s3_credentials_for_company()

            client_s3 = boto3.client(
                's3',
                endpoint_url="https://storage.clo.ru/s3-user-e5a009-default-bucket",
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
            )

            object_id = PydanticObjectId()
            folder_name = f"news_{object_id}/photo/"
            file_key = f"{folder_name}{object_id}.jpg"

            try:
                self.photo.seek(0)
                client_s3.upload_fileobj(
                    self.photo,
                    str(BUCKET_NAME),
                    file_key,
                    ExtraArgs={'ACL': 'public-read'}
                )
            except (NoCredentialsError, PartialCredentialsError) as e:

                raise RuntimeError(f"S3 credentials are invalid or not provided: {e}")

            self.photo_path = f"https://{BUCKET_NAME}.storage.clo.ru/{BUCKET_NAME}/{file_key}"

        elif self.photo_path:
            # self.delete_photo_from_s3(self.photo_path)
            self.photo_path = None
        super(CompanyModel, self).save(*args, **kwargs)

    def get_user_s3_for_company(self):

        PROJECT_ID = os.getenv('PROJECT_ID')
        TOKEN = os.getenv('TOKEN_S3')

        url = f"https://api.clo.ru/v2/projects/{PROJECT_ID}/s3/users"

        header = {'Content-Type': 'application/json', 'Authorization': f'Bearer {TOKEN}'}

        r = requests.get(url, headers=header)

        if r.status_code != 200:
            return r.json()

        parse = r.json()

        return parse['result'][0]['id']

    def get_s3_credentials_for_company(self):
        object_id = self.get_user_s3_for_company()
        TOKEN = os.getenv('TOKEN_S3')

        url = f"https://api.clo.ru/v2/s3/users/{object_id}/credentials"

        header = {'Content-Type': 'application/json', 'Authorization': f'Bearer {TOKEN}'}

        r = requests.get(url=url, headers=header)

        access_key, secret_key = r.json()['result']['access_key'], r.json()['result']['secret_key']

        return access_key, secret_key

class Contact(Document):
    email = EmailField(unique=True)
    phone_number = StringField()
    whatsapp = StringField()
    inn = IntField(unique=True)
    legal_address = StringField()
    requisites = StringField()


class NewsModel(Document):
    title = StringField()
    content = StringField()
    created_at = DateField()
    photo = ImageField()
    photo_path = StringField()
    view_count = IntField()

    def save(self, *args, **kwargs):
        self.photo.read()

        BUCKET_NAME = os.getenv('BUCKET_NAME')
        if self.photo:

            access_key, secret_key = self.get_s3_credentials_for_news()

            client_s3 = boto3.client(
                's3',
                endpoint_url="https://storage.clo.ru/s3-user-e5a009-default-bucket",
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
            )

            object_id = PydanticObjectId()
            folder_name = f"news_{object_id}/photo/"
            file_key = f"{folder_name}{object_id}.jpg"

            try:
                self.photo.seek(0)
                client_s3.upload_fileobj(
                    self.photo,
                    str(BUCKET_NAME),
                    file_key,
                    ExtraArgs={'ACL': 'public-read'}
                )
            except (NoCredentialsError, PartialCredentialsError) as e:

                raise RuntimeError(f"S3 credentials are invalid or not provided: {e}")

            self.photo_path = f"https://{BUCKET_NAME}.storage.clo.ru/{BUCKET_NAME}/{file_key}"

        elif self.photo_path:
            # self.delete_photo_from_s3(self.photo_path)
            self.photo_path = None
        super(NewsModel, self).save(*args, **kwargs)

    def get_user_s3_for_news(self):

        PROJECT_ID = os.getenv('PROJECT_ID')
        TOKEN = os.getenv('TOKEN_S3')

        url = f"https://api.clo.ru/v2/projects/{PROJECT_ID}/s3/users"

        header = {'Content-Type': 'application/json', 'Authorization': f'Bearer {TOKEN}'}

        r = requests.get(url, headers=header)

        if r.status_code != 200:
            return r.json()

        parse = r.json()

        return parse['result'][0]['id']

    def get_s3_credentials_for_news(self):
        object_id = self.get_user_s3_for_news()
        TOKEN = os.getenv('TOKEN_S3')

        url = f"https://api.clo.ru/v2/s3/users/{object_id}/credentials"

        header = {'Content-Type': 'application/json', 'Authorization': f'Bearer {TOKEN}'}

        r = requests.get(url=url, headers=header)
        print(r.json(), flush=True)
        #get_module_logger("__main__").info("HELLO WORLD!")

        access_key, secret_key = r.json()['result']['access_key'], r.json()['result']['secret_key']

        return access_key, secret_key


class RealHistory(Document):
    title = StringField()
    content = StringField()


class SwimsTariffs(Document):
    status = StringField()
    period = StringField()
    cost = IntField()


class ListDescriptionTariffs(EmbeddedDocument):
    number = IntField()
    description = StringField()


class DescriptionTariffs(Document):
    title = StringField()
    description_list = ListField(EmbeddedDocumentField(ListDescriptionTariffs))


class Tariffs(EmbeddedDocument):
    title = StringField()
    count_publications = IntField()
    count_possibilities = IntField()
    price = IntField()


class CompanyTariffs(Document):
    description = ListField(EmbeddedDocumentField(Tariffs))


class Navy(Document):
    vessel_name = StringField()
    imo = StringField()
    ship_type = StringField()
    year_built = StringField()
    dwt = StringField()
    kw = StringField()
    length = StringField()
    width = StringField()
    is_active = BooleanField()


class SettingsGlobal(Document):
    option_name = StringField()
    option_slug = StringField()
    option_values = ListField(StringField())
