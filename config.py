import os
from dotenv import load_dotenv
from pydantic import BaseConfig

load_dotenv()

AUTH0_CLIENT_ID = os.getenv("AUTH0_CLIENT_ID", "your-auth0-client-id")
AUTH0_CLIENT_SECRET = os.getenv("AUTH0_CLIENT_SECRET", "your-auth0-client-secret")
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN", "your-auth0-domain")

class Settings(BaseConfig):
    mongo_username = os.getenv("DB_USERNAME")
    mongo_password = os.getenv("DB_PASSWORD")
    mongo_host = os.getenv("DB_HOST")
    mongo_port = os.getenv("DB_PORT")

settings = Settings()
