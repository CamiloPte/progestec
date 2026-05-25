from typing import Optional
from datetime import datetime
from app.schemas.common import BaseSchema, TimestampSchema

class TicketIssueBase(BaseSchema):
    ticket_id: int
    type: str            # REPORTED | DISCOVERED
    title: str           # Ej: "No enciende", "Pantalla rota", "Batería inflada"
    description: Optional[str] = None


class TicketIssueCreate(TicketIssueBase):
    discovered_at: Optional[datetime] = None
    discovered_by: Optional[int] = None
    is_primary: Optional[int] = None  # 1/0


class TicketIssueUpdate(BaseSchema):
    description: Optional[str] = None
    resolved_at: Optional[datetime] = None
    is_primary: Optional[int] = None
    state: Optional[int] = None


class TicketIssueRead(TimestampSchema):
    id: int
    ticket_id: int
    type: str
    title: str
    description: Optional[str] = None
    discovered_at: Optional[datetime] = None
    discovered_by: Optional[int] = None
    resolved_at: Optional[datetime] = None
    is_primary: Optional[int] = None
    state: int
