from datetime import datetime
from typing import Optional

from app.schemas.common import BaseSchema, TimestampSchema


class DeliveryOrderBase(BaseSchema):
    ticket_id: int
    courier_user_id: Optional[int] = None
    code: str  # código único de entrega/recogida
    status: str  # PENDING | PICKED | DELIVERED | CANCELLED


class DeliveryOrderCreate(DeliveryOrderBase):
    pickup_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    proof_photo: Optional[str] = None


class DeliveryOrderUpdate(BaseSchema):
    courier_user_id: Optional[int] = None
    status: Optional[str] = None
    pickup_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    proof_photo: Optional[str] = None
    state: Optional[int] = None


class DeliveryOrderRead(TimestampSchema):
    id: int
    ticket_id: int
    courier_user_id: Optional[int] = None
    code: str
    status: str
    pickup_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    proof_photo: Optional[str] = None
    state: int
