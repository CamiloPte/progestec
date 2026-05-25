from datetime import datetime
from typing import Optional

from app.schemas.common import BaseSchema, TimestampSchema


class InvoicePaymentBase(BaseSchema):
    amount: float
    payment_method: str
    reference: Optional[str] = None
    paid_at: Optional[datetime] = None


class InvoicePaymentCreate(InvoicePaymentBase):
    invoice_id: int


class InvoicePaymentCreateFromInvoice(InvoicePaymentBase):
    """Payload para registrar pago (invoice_id viene en el path)."""

    pass


class InvoicePaymentRead(TimestampSchema):
    id: int
    invoice_id: int
    amount: float
    payment_method: str
    reference: Optional[str] = None
    paid_at: datetime
    created_by_id: Optional[int] = None
    created_by_name: Optional[str] = None
    state: int
