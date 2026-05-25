from typing import Optional

from app.schemas.common import BaseSchema, TimestampSchema


class TicketAttachmentCreate(BaseSchema):
    ticket_id: int
    history_id: Optional[int] = None
    attachment_type: str
    original_name: str
    stored_name: str
    file_url: str
    mime_type: Optional[str] = None
    file_size: Optional[int] = None
    note: Optional[str] = None
    uploaded_by: Optional[int] = None


class TicketAttachmentRead(TimestampSchema):
    id: int
    ticket_id: int
    history_id: Optional[int] = None
    attachment_type: str
    original_name: str
    stored_name: str
    file_url: str
    mime_type: Optional[str] = None
    file_size: Optional[int] = None
    note: Optional[str] = None
    uploaded_by: Optional[int] = None
    state: Optional[int] = None
