# app/core/jwt_utils.py

from jose import jwt, JWTError
from fastapi import HTTPException, status
from app.core.config import settings

ALGORITHM = "HS256"

def decode_access_token(token: str) -> dict:
    """
    Decodes the JWT and returns the payload.
    Raises 401 if invalid.
    Expected payload: {"sub": email, "role": role_name, "exp": ...}
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate token"
        )
