# app/services/dashboard_service.py

from collections import defaultdict
from datetime import datetime
from decimal import Decimal
from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.roles import (
    ROLE_ADMIN,
    ROLE_ADVISOR,
    ROLE_CLIENT,
    ROLE_TECHNICIAN,
    get_role_name,
)
from app.crud.ticket_crud import ticket_crud
from app.models.device import Device
from app.models.invoice import Invoice
from app.models.ticket import Ticket
from app.models.user import User
from app.schemas.dashboard import (
    ClientDashboardSummary,
    ClientDeviceSummary,
    ClientInvoiceSummary,
    ClientNotification,
    ClientTicketSummary,
    DashboardSummary,
    TicketStatusCount,
)
from app.schemas.ticket import TicketReadMinimal


class DashboardService:
    def _ensure_can_view_dashboard(self, current_user: User) -> None:
        """
        En esta fase:
        - ADMIN / ADVISOR / TECHNICIAN pueden ver el dashboard.
        - CLIENT / COURIER no.
        """
        role = get_role_name(current_user)
        if role not in (ROLE_ADMIN, ROLE_ADVISOR, ROLE_TECHNICIAN):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Role not allowed to view dashboard summary",
            )

    def _build_device_label(self, t) -> str | None:
        if not getattr(t, "device", None):
            return None
        pieces = []
        if t.device.brand:
            pieces.append(t.device.brand)
        if t.device.model:
            pieces.append(t.device.model)
        base_label = " ".join(pieces).strip()
        if t.failure_desc:
            short_failure = (
                t.failure_desc[:60] + "…" if len(t.failure_desc) > 60 else t.failure_desc
            )
            return f"{base_label} – {short_failure}" if base_label else short_failure
        return base_label or f"Dispositivo #{t.device_id}"

    def _to_ticket_minimal(self, t) -> TicketReadMinimal:
        """
        Mapeo a TicketReadMinimal usando model_validate y completando derivados.
        """
        minimal = TicketReadMinimal.model_validate(t, from_attributes=True)
        minimal.device_label = self._build_device_label(t)
        minimal.assignee_name = (
            t.assignee.full_name or t.assignee.email if getattr(t, "assignee", None) else None
        )
        minimal.status_code = t.status.code if getattr(t, "status", None) else None
        minimal.status_name = t.status.name if getattr(t, "status", None) else None
        return minimal

    def get_summary(self, db: Session, *, current_user: User) -> DashboardSummary:
        """
        Resumen general de tickets para el dashboard.

        - ADMIN / ADVISOR: ven todos los tickets activos.
        - TECHNICIAN: ve solo sus tickets asignados.
        """

        self._ensure_can_view_dashboard(current_user)
        role = get_role_name(current_user)

        # 1) Obtener tickets base desde el CRUD
        tickets = ticket_crud.list_all_active(db)

        # 2) Filtrar según rol
        if role == ROLE_TECHNICIAN:
            tickets = [t for t in tickets if t.assignee_user_id == current_user.id]

        # 3) Métricas básicas
        total = len(tickets)

        # Consideramos "cerrado" un ticket que tenga closed_at NO nulo
        closed_tickets = [t for t in tickets if getattr(t, "closed_at", None) is not None]
        closed_count = len(closed_tickets)

        # Abiertos = activos sin closed_at
        open_tickets = [t for t in tickets if getattr(t, "closed_at", None) is None]
        open_count = len(open_tickets)

        # "En progreso" = aquellos abiertos cuyo status es alguno de estos códigos
        in_progress_codes = {"DIAGNOSING", "IN_PROGRESS"}
        in_progress_count = 0
        for t in open_tickets:
            code = t.status.code.upper() if t.status and t.status.code else None
            if code in in_progress_codes:
                in_progress_count += 1

        # 4) Conteo por status
        status_map: dict[str, TicketStatusCount] = {}
        counter = defaultdict(int)

        for t in tickets:
            code = t.status.code if t.status and t.status.code else "UNKNOWN"
            name = t.status.name if t.status and t.status.name else "Sin estado"
            counter[code] += 1
            if code not in status_map:
                status_map[code] = TicketStatusCount(
                    status_code=code,
                    status_name=name,
                    count=0,
                )

        for code, c in counter.items():
            status_map[code].count = c

        by_status = list(status_map.values())

        # 5) Tickets recientes (últimos 5 por created_at)
        sorted_tickets = sorted(
            tickets,
            key=lambda t: t.created_at or datetime.min,
            reverse=True,
        )
        recent_db_tickets = sorted_tickets[:5]
        recent_tickets: List[TicketReadMinimal] = [
            self._to_ticket_minimal(t) for t in recent_db_tickets
        ]

        return DashboardSummary(
            total_tickets=total,
            open_tickets=open_count,
            in_progress_tickets=in_progress_count,
            closed_tickets=closed_count,
            by_status=by_status,
            recent_tickets=recent_tickets,
        )

    # ==================== DASHBOARD CLIENTE ====================

    def _get_status_color(self, status_code: str) -> str:
        """Retorna el color asociado a un estado para UI."""
        color_map = {
            "RECEIVED": "#3498db",  # Azul
            "DIAGNOSING": "#9b59b6",  # Púrpura
            "WAITING_APPROVAL": "#f39c12",  # Naranja
            "APPROVED": "#27ae60",  # Verde
            "IN_PROGRESS": "#2980b9",  # Azul oscuro
            "READY": "#2ecc71",  # Verde claro
            "DELIVERED": "#1abc9c",  # Turquesa
            "CLOSED": "#95a5a6",  # Gris
            "CANCELLED": "#e74c3c",  # Rojo
        }
        return color_map.get(status_code.upper(), "#7f8c8d")

    def _get_progress_percent(self, status_code: str) -> int:
        """Retorna el progreso del ticket (0-100) según su estado."""
        progress_map = {
            "RECEIVED": 10,
            "DIAGNOSING": 25,
            "WAITING_APPROVAL": 35,
            "APPROVED": 45,
            "IN_PROGRESS": 60,
            "READY": 85,
            "DELIVERED": 95,
            "CLOSED": 100,
            "CANCELLED": 100,
        }
        return progress_map.get(status_code.upper(), 0)

    def _build_client_ticket_summary(self, ticket: Ticket) -> ClientTicketSummary:
        """Convierte un ticket a resumen para cliente."""
        status_code = ticket.status.code if ticket.status else "UNKNOWN"
        status_name = ticket.status.name if ticket.status else "Sin estado"

        # Construir label del dispositivo
        device_label = "Dispositivo"
        if ticket.device:
            parts = []
            if ticket.device.brand:
                parts.append(ticket.device.brand)
            if ticket.device.model:
                parts.append(ticket.device.model)
            device_label = " ".join(parts) if parts else f"Dispositivo #{ticket.device_id}"

        # Determinar si necesita aprobación
        needs_approval = (
            status_code.upper() == "WAITING_APPROVAL" and ticket.approved_by_owner is None
        )

        return ClientTicketSummary(
            id=ticket.id,
            tracking_code=ticket.tracking_code,
            device_label=device_label,
            status_code=status_code,
            status_name=status_name,
            status_color=self._get_status_color(status_code),
            progress_percent=self._get_progress_percent(status_code),
            failure_desc=ticket.failure_desc or "",
            cost_estimate=ticket.cost_estimate,
            approved_by_owner=ticket.approved_by_owner,
            needs_approval=needs_approval,
            intake_at=ticket.intake_at,
            ready_at=ticket.ready_at,
            delivered_at=ticket.delivered_at,
        )

    def _build_client_device_summary(self, device: Device, db: Session) -> ClientDeviceSummary:
        """Convierte un dispositivo a resumen para cliente."""
        # Contar tickets de este dispositivo
        tickets = (
            db.query(Ticket)
            .filter(Ticket.device_id == device.id, Ticket.state == 1)
            .order_by(Ticket.created_at.desc())
            .all()
        )

        last_service_date = None
        last_service_status = None
        if tickets:
            last_ticket = tickets[0]
            last_service_date = last_ticket.created_at
            last_service_status = last_ticket.status.name if last_ticket.status else None

        return ClientDeviceSummary(
            id=device.id,
            type=device.type,
            brand=device.brand,
            model=device.model,
            serial=device.serial,
            tickets_count=len(tickets),
            last_service_date=last_service_date,
            last_service_status=last_service_status,
        )

    def _build_client_invoice_summary(self, invoice: Invoice) -> ClientInvoiceSummary:
        """Convierte una factura a resumen para cliente."""
        # Calcular pagado y pendiente
        paid = (
            sum(p.amount for p in invoice.payments if p.state == 1)
            if invoice.payments
            else Decimal("0")
        )
        pending = (invoice.total or Decimal("0")) - paid

        ticket_code = None
        if invoice.ticket:
            ticket_code = invoice.ticket.tracking_code

        return ClientInvoiceSummary(
            id=invoice.id,
            invoice_number=invoice.invoice_number,
            issue_date=invoice.issue_date,
            total=invoice.total or Decimal("0"),
            status=invoice.status,
            paid_amount=paid,
            pending_amount=max(pending, Decimal("0")),
            ticket_tracking_code=ticket_code,
        )

    def get_client_summary(self, db: Session, *, current_user: User) -> ClientDashboardSummary:
        """
        Dashboard personalizado para clientes.
        Solo usuarios con rol CLIENT pueden acceder.
        """
        role = get_role_name(current_user)
        if role != ROLE_CLIENT:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo clientes pueden acceder a este dashboard",
            )

        notifications: List[ClientNotification] = []
        now = datetime.utcnow()

        # 1) Obtener dispositivos del cliente
        devices = (
            db.query(Device)
            .filter(Device.owner_user_id == current_user.id, Device.state == 1)
            .all()
        )
        device_ids = [d.id for d in devices]

        # 2) Obtener tickets de esos dispositivos
        tickets = []
        if device_ids:
            tickets = (
                db.query(Ticket)
                .filter(Ticket.device_id.in_(device_ids), Ticket.state == 1)
                .order_by(Ticket.created_at.desc())
                .all()
            )

        # Tickets activos (no cerrados ni cancelados)
        active_codes = {
            "RECEIVED",
            "DIAGNOSING",
            "WAITING_APPROVAL",
            "APPROVED",
            "IN_PROGRESS",
            "READY",
        }
        active_tickets = [t for t in tickets if t.status and t.status.code.upper() in active_codes]

        # Tickets esperando aprobación
        pending_approvals = [
            t
            for t in active_tickets
            if t.status
            and t.status.code.upper() == "WAITING_APPROVAL"
            and t.approved_by_owner is None
        ]

        # Generar notificaciones de aprobación pendiente
        for t in pending_approvals:
            notifications.append(
                ClientNotification(
                    type="approval_pending",
                    icon="⚠️",
                    title="Presupuesto pendiente de aprobar",
                    message=f"Tu equipo {t.device.brand} {t.device.model} tiene un presupuesto de ${t.cost_estimate or 0:,.0f}",
                    action_url=f"/client/tickets/{t.id}",
                    created_at=t.updated_at or now,
                )
            )

        # Tickets listos para recoger
        ready_tickets = [t for t in active_tickets if t.status and t.status.code.upper() == "READY"]
        for t in ready_tickets:
            notifications.append(
                ClientNotification(
                    type="ready_pickup",
                    icon="✅",
                    title="¡Tu equipo está listo!",
                    message=f"Tu {t.device.brand} {t.device.model} está listo para recoger",
                    action_url=f"/client/tickets/{t.id}",
                    created_at=t.updated_at or now,
                )
            )

        # 3) Obtener facturas del cliente
        invoices = (
            db.query(Invoice)
            .filter(Invoice.client_id == current_user.id, Invoice.state == 1)
            .order_by(Invoice.issue_date.desc())
            .all()
        )

        # Facturas pendientes de pago
        pending_invoices = [inv for inv in invoices if inv.status in ("PENDING", "PARTIAL")]

        for inv in pending_invoices[:3]:  # Máximo 3 notificaciones de facturas
            paid = (
                sum(p.amount for p in inv.payments if p.state == 1)
                if inv.payments
                else Decimal("0")
            )
            pending = (inv.total or Decimal("0")) - paid
            if pending > 0:
                notifications.append(
                    ClientNotification(
                        type="invoice_pending",
                        icon="💰",
                        title="Factura pendiente de pago",
                        message=f"Factura {inv.invoice_number} - Pendiente: ${pending:,.0f}",
                        action_url=f"/client/invoices/{inv.id}",
                        created_at=inv.issue_date or now,
                    )
                )

        # Ordenar notificaciones por fecha (más recientes primero)
        notifications.sort(key=lambda n: n.created_at, reverse=True)

        # 4) Construir resúmenes
        # Incluir TODOS los tickets para que el cliente pueda filtrar (activos y completados)
        ticket_summaries = [self._build_client_ticket_summary(t) for t in tickets]
        device_summaries = [self._build_client_device_summary(d, db) for d in devices]
        invoice_summaries = [
            self._build_client_invoice_summary(inv) for inv in pending_invoices[:5]
        ]

        return ClientDashboardSummary(
            client_name=current_user.full_name or current_user.email,
            active_tickets=len(active_tickets),
            devices_count=len(devices),
            pending_invoices=len(pending_invoices),
            pending_approvals=len(pending_approvals),
            notifications=notifications[:5],  # Máximo 5 notificaciones
            tickets=ticket_summaries,  # Todos los tickets para filtrado en frontend
            devices=device_summaries,
            invoices=invoice_summaries,
        )


dashboard_service = DashboardService()
