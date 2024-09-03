import os
from dotenv import load_dotenv
from pydantic import BaseConfig

load_dotenv()


class Settings(BaseConfig):
    mongo_username = os.getenv("DB_USERNAME")
    mongo_password = os.getenv("DB_PASSWORD")
    mongo_host = os.getenv("DB_HOST")
    mongo_port = os.getenv("DB_PORT")


settings = Settings()
