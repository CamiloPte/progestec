from datetime import datetime
from typing import List, Optional

from app.schemas.common import BaseSchema, TimestampSchema
from app.schemas.invoice_payment import InvoicePaymentRead


class InvoiceBase(BaseSchema):
    ticket_id: int
    labor_cost: float = 0
    discount_amount: float = 0
    tax_percentage: float = 0
    due_date: Optional[datetime] = None
    notes: Optional[str] = None


class InvoiceCreate(InvoiceBase):
    issue_date: Optional[datetime] = None


class InvoiceCreateFromTicket(BaseSchema):
    """Payload para crear factura desde un ticket (ticket_id viene en el path)."""

    labor_cost: float = 0
    discount_amount: float = 0
    tax_percentage: float = 0
    due_date: Optional[datetime] = None
    notes: Optional[str] = None
    issue_date: Optional[datetime] = None


class InvoiceUpdate(BaseSchema):
    """Payload para actualizar una factura DRAFT (agregar mano de obra, etc.)."""

    labor_cost: Optional[float] = None
    discount_amount: Optional[float] = None
    tax_percentage: Optional[float] = None
    due_date: Optional[datetime] = None
    notes: Optional[str] = None
    confirm: bool = False  # Si es True, cambia el estado de DRAFT a PENDING


class InvoiceRead(TimestampSchema):
    id: int
    invoice_number: str
    ticket_id: int
    ticket_tracking_code: Optional[str] = None
    client_id: int
    client_name: Optional[str] = None
    issue_date: datetime
    due_date: Optional[datetime] = None
    parts_cost: float
    labor_cost: float
    discount_amount: float
    subtotal: float
    tax_percentage: float
    tax_amount: float
    total: float
    status: str
    paid_at: Optional[datetime] = None
    notes: Optional[str] = None
    total_paid: float
    outstanding_amount: float
    payments: List[InvoicePaymentRead] = []
