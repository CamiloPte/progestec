from typing import Optional, List
from pydantic import BaseModel, EmailStr
from app.schemas.common import BaseSchema, TimestampSchema


class UserBase(BaseSchema):
    full_name: Optional[str] = None
    email: EmailStr
    phone: Optional[str] = None
    identification: Optional[str] = None
    identification_type: Optional[str] = None


class UserCreate(BaseSchema):
    full_name: str
    email: EmailStr
    password: str
    identification: str
    phone: str
    identification_type: Optional[str] = None
    role_id: int  # se podrá asignar al crear (ADMIN, TECH, CLIENT, etc.)


class QuickClientCreate(BaseSchema):
    """
    Para creación rápida de clientes desde flujo de tickets.
    """
    full_name: str
    email: EmailStr
    identification: str
    identification_type: Optional[str] = None
    phone: Optional[str] = None


class UserUpdate(BaseSchema):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    identification_type: Optional[str] = None
    role_id: Optional[int] = None


class UserReadMinimal(TimestampSchema):
    id: int
    full_name: Optional[str]
    email: EmailStr
    phone: Optional[str] = None
    identification_type: Optional[str] = None
    identification: Optional[str] = None
    role_id: int
    role_name: Optional[str] = None   # Este campo lo voy a necesitar para conectar con el frontend
    state: int
    must_change_password: bool = False
    modules: List[str] = []


class UserReadDetail(UserReadMinimal):
    """
    Aquí podríamos anidar role, atributos,
    y dispositivos si el endpoint lo requiere.
    """
    pass
