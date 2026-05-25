# app/core/security.py

from datetime import datetime, timedelta

from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm="HS256")


# Swagger usará ESTE flujo para autenticarse automáticamente.
# tokenUrl debe apuntar al endpoint que acepta username/password en form-data,
# que vamos a crear abajo como /auth/token
OAUTH2_SCHEME = OAuth2PasswordBearer(tokenUrl="/auth/token")
