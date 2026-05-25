from typing import Optional
from app.schemas.common import BaseSchema, TimestampSchema

class TicketStatusBase(BaseSchema):
    code: str       # RECEIVED, ASSIGNED, REPAIR, READY, etc.
    name: str
    order: int


class TicketStatusCreate(TicketStatusBase):
    pass


class TicketStatusUpdate(BaseSchema):
    code: Optional[str] = None
    name: Optional[str] = None
    order: Optional[int] = None
    state: Optional[int] = None


class TicketStatusRead(TimestampSchema):
    id: int
    code: str
    name: str
    order: int
    state: int
