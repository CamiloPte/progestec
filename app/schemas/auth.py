from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    must_change_password: bool = False


class TokenPayload(BaseModel):
    """
    Payload del JWT (decodificado)
    """
    sub: str  # email del usuario
    role: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    identification: str
    phone: Optional[str] = None
    role_id: int  # Asignar rol al registrar temporalmente


class SetPasswordRequest(BaseModel):
    new_password: str

class UserCreatedResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role_id: int
    state: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
