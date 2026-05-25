# app/schemas/dashboard.py
from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel
from app.schemas.ticket import TicketReadMinimal


class TicketStatusCount(BaseModel):
    status_code: str
    status_name: Optional[str] = None
    count: int


class DashboardSummary(BaseModel):
    total_tickets: int
    open_tickets: int
    in_progress_tickets: int
    closed_tickets: int
    by_status: List[TicketStatusCount]
    recent_tickets: List[TicketReadMinimal]


# ---------- CLIENTE DASHBOARD ----------

class ClientTicketSummary(BaseModel):
    """Resumen de un ticket para el cliente."""
    id: int
    tracking_code: str
    device_label: str
    status_code: str
    status_name: str
    status_color: str  # Para UI: verde, amarillo, rojo, etc.
    progress_percent: int  # 0-100 para barra de progreso
    failure_desc: str
    cost_estimate: Optional[Decimal] = None
    approved_by_owner: Optional[int] = None
    needs_approval: bool = False  # True si está esperando aprobación
    intake_at: Optional[datetime] = None
    ready_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None


class ClientDeviceSummary(BaseModel):
    """Resumen de dispositivo para el cliente."""
    id: int
    type: str
    brand: str
    model: str
    serial: Optional[str] = None
    tickets_count: int = 0
    last_service_date: Optional[datetime] = None
    last_service_status: Optional[str] = None


class ClientInvoiceSummary(BaseModel):
    """Resumen de factura para el cliente."""
    id: int
    invoice_number: str
    issue_date: datetime
    total: Decimal
    status: str
    paid_amount: Decimal = Decimal("0")
    pending_amount: Decimal = Decimal("0")
    ticket_tracking_code: Optional[str] = None


class ClientNotification(BaseModel):
    """Notificación/alerta para el cliente."""
    type: str  # 'approval_pending', 'ready_pickup', 'invoice_pending', 'info'
    icon: str  # Emoji o icono
    title: str
    message: str
    action_url: Optional[str] = None
    created_at: datetime


class ClientDashboardSummary(BaseModel):
    """Dashboard completo del cliente."""
    # Bienvenida
    client_name: str
    
    # Contadores
    active_tickets: int
    devices_count: int
    pending_invoices: int
    pending_approvals: int
    
    # Notificaciones importantes
    notifications: List[ClientNotification]
    
    # Tickets activos (resumen)
    tickets: List[ClientTicketSummary]
    
    # Dispositivos del cliente
    devices: List[ClientDeviceSummary]
    
    # Facturas pendientes
    invoices: List[ClientInvoiceSummary]
