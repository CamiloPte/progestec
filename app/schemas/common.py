from typing import Optional, List, Generic, TypeVar
from pydantic import BaseModel
from datetime import datetime

T = TypeVar("T")


class BaseSchema(BaseModel):
    """
    Base para heredar configuración global
    """
    model_config = {
        "from_attributes": True  # Reemplaza orm_mode=True en Pydantic V2
    }


class MessageResponse(BaseSchema):
    """
    Respuesta estándar para mensajes
    """
    message: str


class IdResponse(BaseSchema):
    """
    Respuesta estándar cuando se crea un recurso
    """
    id: int
    message: Optional[str] = None


class ErrorResponse(BaseSchema):
    """
    Respuesta estándar para errores controlados
    """
    detail: str


class Pagination(BaseSchema):
    """
    Para respuestas paginadas en listados
    """
    total: int
    page: int
    size: int


class PaginatedResponse(BaseSchema, Generic[T]):
    """
    Lista + metadatos
    """
    items: List[T]
    pagination: Pagination


class TimestampSchema(BaseSchema):
    """
    Fechas estándar en ISO8601
    """
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
