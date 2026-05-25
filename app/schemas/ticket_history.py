from datetime import datetime
from typing import Optional

from app.schemas.common import BaseSchema


class TicketHistoryBase(BaseSchema):
    ticket_id: int
    status_id: int
    user_id: Optional[int] = None
    note: Optional[str] = None


class TicketHistoryCreate(TicketHistoryBase):
    pass


class TicketHistoryRead(BaseSchema):
    id: int
    ticket_id: int
    status_id: int
    user_id: Optional[int] = None
    note: Optional[str] = None
    created_at: datetime
    state: int
    status_name: Optional[str] = None
    status_code: Optional[str] = None
    user_name: Optional[str] = None
