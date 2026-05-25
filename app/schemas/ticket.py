# app/schemas/ticket.py
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import EmailStr

from app.schemas.common import BaseSchema, TimestampSchema
from app.schemas.device import DeviceReadMinimal
from app.schemas.ticket_attachment import TicketAttachmentRead
from app.schemas.ticket_history import TicketHistoryRead
from app.schemas.ticket_issue import TicketIssueRead
from app.schemas.ticket_status import TicketStatusRead


class TicketBase(BaseSchema):
    device_id: int
    failure_desc: str  # Debe ser una descripción del problema reportado
    assignee_user_id: Optional[int] = None  # técnico asignado
    status_id: int = 1  # estado inicial: RECEIVED
    diagnosis: Optional[str] = None
    cost_estimate: Optional[Decimal] = None
    approved_by_owner: Optional[int] = None  # 1/0


class TicketCreate(TicketBase):
    tracking_code: str  # PGT-XXXX
    intake_at: Optional[datetime] = None


class TicketUpdate(BaseSchema):
    assignee_user_id: Optional[int] = None
    status_id: Optional[int] = None
    diagnosis: Optional[str] = None
    cost_estimate: Optional[Decimal] = None
    approved_by_owner: Optional[int] = None
    ready_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    state: Optional[int] = None
    history_note: Optional[str] = None


class TicketOwnerInfo(BaseSchema):
    id: int
    full_name: Optional[str] = None
    email: EmailStr
    phone: Optional[str] = None
    identification: Optional[str] = None
    identification_type: Optional[str] = None
    address: Optional[str] = None


class TicketReadMinimal(TimestampSchema):
    """
    Para listados. Ligero.
    """

    id: int
    tracking_code: str

    # datos básicos
    device_id: int
    assignee_user_id: Optional[int] = None
    status_id: int
    status_code: Optional[str] = None
    status_name: Optional[str] = None

    # NUEVO: listo para la tabla del front
    device_label: Optional[str] = None  # ej: "iPhone 11 – No carga"
    assignee_name: Optional[str] = None  # nombre del técnico

    state: int


class TicketReadDetail(TimestampSchema):
    """
    Para detalle. Completo/anidado.
    """

    id: int
    tracking_code: str

    # estado actual
    status: TicketStatusRead

    # técnico asignado
    assignee_user_id: Optional[int] = None
    assignee_name: Optional[str] = None  # NUEVO

    # dispositivo
    device: DeviceReadMinimal
    device_label: Optional[str] = None  # NUEVO
    owner: Optional[TicketOwnerInfo] = None

    # descripción / diagnóstico
    failure_desc: str
    diagnosis: Optional[str] = None
    cost_estimate: Optional[Decimal] = None
    approved_by_owner: Optional[int] = None

    # hitos temporales
    intake_at: Optional[datetime] = None
    ready_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None

    # histórico y problemas encontrados
    issues: List[TicketIssueRead] = []
    history: List[TicketHistoryRead] = []
    attachments: List[TicketAttachmentRead] = []

    state: int
