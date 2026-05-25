from datetime import datetime
from typing import Optional

from app.schemas.common import BaseSchema, TimestampSchema


# claim code lo usaremos en general para los codigos de retiro de dispositivos o tickets
class ClaimCodeBase(BaseSchema):
    code: str
    ticket_id: Optional[int] = None
    device_id: Optional[int] = None


class ClaimCodeCreate(ClaimCodeBase):
    expires_at: Optional[datetime] = None


class ClaimCodeUpdate(BaseSchema):
    used_at: Optional[datetime] = None
    state: Optional[int] = None


class ClaimCodeRead(TimestampSchema):
    id: int
    code: str
    ticket_id: Optional[int] = None
    device_id: Optional[int] = None
    expires_at: Optional[datetime] = None
    used_at: Optional[datetime] = None
    state: int
