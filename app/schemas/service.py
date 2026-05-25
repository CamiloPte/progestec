from typing import Optional
from app.schemas.common import BaseSchema, TimestampSchema

class ServiceBase(BaseSchema):
    name: str
    base_price: float


class ServiceCreate(ServiceBase):
    pass


class ServiceUpdate(BaseSchema):
    name: Optional[str] = None
    base_price: Optional[float] = None
    state: Optional[int] = None


class ServiceRead(TimestampSchema):
    id: int
    name: str
    base_price: float
    state: int
