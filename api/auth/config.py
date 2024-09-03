import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
import secrets
from fastapi import Depends, HTTPException
from api.auth.auth import AuthServices
from fastapi.security import OAuth2PasswordBearer
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from passlib.hash import pbkdf2_sha256
from typing import Optional
from bson import ObjectId

load_dotenv()

SECRET_KEY = secrets.token_hex(64)
ALGORITHM = 'HS256'

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/token", auto_error=False)
EXPIRATION_TIME = timedelta(minutes=30)
REFRESH_TOKEN_LIFETIME = timedelta(hours=24)


def generate_salt():
    return rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    ).public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )


def hash_password(password: str, salt: bytes):
    hashed_password = pbkdf2_sha256.hash(password, salt=salt, rounds=100000)
    return hashed_password


def generate_jwt_token(data: dict):
    expiration_access = datetime.utcnow() + EXPIRATION_TIME
    access_data = data.copy()
    access_data.update({"iat": datetime.utcnow(), "exp": expiration_access})

    access_token = jwt.encode(access_data, SECRET_KEY, algorithm=ALGORITHM)

    expiration_refresh = datetime.utcnow() + REFRESH_TOKEN_LIFETIME
    refresh_data = data.copy()
    refresh_data.update({"iat": datetime.utcnow(), "exp": expiration_refresh})

    refresh_token = jwt.encode(refresh_data, SECRET_KEY, algorithm=ALGORITHM)

    return {"access_token": access_token, "refresh_token": refresh_token, "info": data}


def verify_jwt_token(token: str):
    try:
        decoded_data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decoded_data
    except jwt.PyJWTError:
        return None


def convert_objectid_to_str(data, schema=None):
    if isinstance(data, dict):
        return {k: str(v) if isinstance(v, ObjectId) else v for k, v in data.items()}
    elif isinstance(data, list):
        return [str(item) if isinstance(item, ObjectId) else item for item in data]
    elif isinstance(data, schema):
        return str(data)
    else:
        return data


async def get_current_user(token: Optional[str] = Depends(oauth2_scheme)):
    if token is None:
        return None

    service = AuthServices()
    decoded_data = verify_jwt_token(token)

    if not decoded_data:
        raise HTTPException(status_code=400, detail="Invalid token")

    user = await service.find_user(decoded_data['sub'])
    if user:
        return user
    else:
        raise HTTPException(status_code=400, detail="User not found")
