from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.roles import (
    ROLE_ADMIN,
    ROLE_ADVISOR,
    ROLE_CLIENT,
    ROLE_TECHNICIAN,
    get_role_name,
)
from app.crud.invoice_crud import invoice_crud
from app.crud.invoice_payment_crud import invoice_payment_crud
from app.crud.ticket_crud import ticket_crud
from app.models.invoice import Invoice
from app.models.invoice_payment import InvoicePayment
from app.models.ticket import Ticket
from app.models.user import User
from app.schemas.invoice import InvoiceCreateFromTicket, InvoiceRead
from app.schemas.invoice_payment import (
    InvoicePaymentCreate,
    InvoicePaymentRead,
)


class InvoiceService:
    STATUSES = ("DRAFT", "PENDING", "PAID", "CANCELLED")

    # ---------- helpers ----------
    def _ensure_can_create(self, user: User) -> None:
        if get_role_name(user) not in (ROLE_ADMIN, ROLE_ADVISOR):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo un administrador o asesor puede generar facturas",
            )

    def _ensure_can_register_payment(self, user: User) -> None:
        if get_role_name(user) not in (ROLE_ADMIN, ROLE_ADVISOR):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo un administrador o asesor puede registrar pagos",
            )

    def _assert_can_view_invoice(self, user: User, invoice: Invoice) -> None:
        role = get_role_name(user)
        if role in (ROLE_ADMIN, ROLE_ADVISOR):
            return
        if role == ROLE_TECHNICIAN:
            if not invoice.ticket or invoice.ticket.assignee_user_id != user.id:
                raise HTTPException(status_code=403, detail="Factura no disponible")
            return
        if role == ROLE_CLIENT:
            if invoice.client_id != user.id:
                raise HTTPException(status_code=403, detail="Factura no disponible")
            return
        raise HTTPException(status_code=403, detail="Rol sin acceso a facturas")

    def _sanitize_invoice_number(self, ticket: Ticket) -> str:
        base = ticket.tracking_code or f"TKT{ticket.id}"
        safe = "".join(ch for ch in base if ch.isalnum()).upper() or f"TKT{ticket.id}"
        date_part = datetime.utcnow().strftime("%Y%m%d")
        return f"INV-{date_part}-{safe}"

    def _sum_payments(self, invoice: Invoice) -> Decimal:
        return sum(
            Decimal(payment.amount or 0) for payment in invoice.payments if payment.state == 1
        )

    def _map_payment(self, payment: InvoicePayment) -> InvoicePaymentRead:
        creator_name = None
        if payment.created_by:
            creator_name = payment.created_by.full_name or payment.created_by.email

        return InvoicePaymentRead(
            id=payment.id,
            invoice_id=payment.invoice_id,
            amount=float(payment.amount),
            payment_method=payment.payment_method,
            reference=payment.reference,
            paid_at=payment.paid_at,
            created_by_id=payment.created_by_id,
            created_by_name=creator_name,
            state=payment.state,
            created_at=payment.created_at,
            updated_at=payment.updated_at,
        )

    def _map_invoice(self, invoice: Invoice) -> InvoiceRead:
        payments = [
            self._map_payment(payment) for payment in invoice.payments if payment.state == 1
        ]
        total_paid = self._sum_payments(invoice)
        outstanding = max(Decimal(invoice.total or 0) - total_paid, Decimal("0"))

        client_name = None
        if invoice.client:
            client_name = invoice.client.full_name or invoice.client.email

        tracking_code = invoice.ticket.tracking_code if invoice.ticket else None

        return InvoiceRead(
            id=invoice.id,
            invoice_number=invoice.invoice_number,
            ticket_id=invoice.ticket_id,
            ticket_tracking_code=tracking_code,
            client_id=invoice.client_id,
            client_name=client_name,
            issue_date=invoice.issue_date,
            due_date=invoice.due_date,
            parts_cost=float(invoice.parts_cost),
            labor_cost=float(invoice.labor_cost),
            discount_amount=float(invoice.discount_amount),
            subtotal=float(invoice.subtotal),
            tax_percentage=float(invoice.tax_percentage),
            tax_amount=float(invoice.tax_amount),
            total=float(invoice.total),
            status=invoice.status,
            paid_at=invoice.paid_at,
            notes=invoice.notes,
            created_at=invoice.created_at,
            updated_at=invoice.updated_at,
            total_paid=float(total_paid),
            outstanding_amount=float(outstanding),
            payments=payments,
        )

    def _calculate_parts_cost(self, ticket: Ticket) -> Decimal:
        if not ticket.ticket_parts:
            return Decimal("0")
        return sum(Decimal(tp.total_cost or 0) for tp in ticket.ticket_parts if tp.state == 1)

    def _apply_in_memory_filters(
        self,
        invoices: List[Invoice],
        *,
        status_list: Optional[List[str]] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        with_debt: Optional[bool] = None,
    ) -> List[Invoice]:
        filtered = invoices
        if status_list:
            allowed = {s.upper() for s in status_list}
            filtered = [inv for inv in filtered if inv.status.upper() in allowed]
        if from_date:
            filtered = [inv for inv in filtered if inv.issue_date >= from_date]
        if to_date:
            filtered = [inv for inv in filtered if inv.issue_date <= to_date]
        if with_debt:
            filtered = [
                inv for inv in filtered if (Decimal(inv.total or 0) - self._sum_payments(inv)) > 0
            ]
        return filtered

    # ---------- public API ----------
    def generate_invoice_for_ticket(
        self,
        db: Session,
        *,
        current_user: User,
        ticket_id: int,
        payload: InvoiceCreateFromTicket,
    ) -> InvoiceRead:
        self._ensure_can_create(current_user)

        existing = invoice_crud.get_by_ticket_id(db, ticket_id)
        if existing:
            raise HTTPException(status_code=400, detail="El ticket ya tiene una factura")

        ticket = ticket_crud.get_by_id(db, ticket_id)
        if not ticket or ticket.state != 1:
            raise HTTPException(status_code=404, detail="Ticket no encontrado")

        if not ticket.device or not ticket.device.owner:
            raise HTTPException(
                status_code=400,
                detail="El ticket no tiene un cliente asignado",
            )

        parts_cost = self._calculate_parts_cost(ticket)
        labor_cost = Decimal(str(payload.labor_cost or 0))
        discount = Decimal(str(payload.discount_amount or 0))
        tax_percentage = Decimal(str(payload.tax_percentage or 0))

        if labor_cost < 0 or discount < 0 or tax_percentage < 0:
            raise HTTPException(status_code=400, detail="Montos inválidos en la factura")

        subtotal = parts_cost + labor_cost - discount
        if subtotal < 0:
            raise HTTPException(
                status_code=400,
                detail="El descuento excede la suma de repuestos y mano de obra",
            )

        tax_amount = (subtotal * tax_percentage) / Decimal("100")
        total = subtotal + tax_amount

        invoice_data = {
            "ticket_id": ticket.id,
            "client_id": ticket.device.owner.id,
            "invoice_number": self._sanitize_invoice_number(ticket),
            "issue_date": payload.issue_date or datetime.utcnow(),
            "due_date": payload.due_date,
            "parts_cost": parts_cost,
            "labor_cost": labor_cost,
            "discount_amount": discount,
            "subtotal": subtotal,
            "tax_percentage": tax_percentage,
            "tax_amount": tax_amount,
            "total": total,
            "status": "PENDING",
            "created_by_id": current_user.id,
            "notes": payload.notes,
        }

        invoice = invoice_crud.create(db, invoice_data)
        db.commit()
        return self._map_invoice(self._get_invoice_or_404(db, invoice.id))

    def _get_invoice_or_404(self, db: Session, invoice_id: int) -> Invoice:
        invoice = invoice_crud.get(db, invoice_id)
        if not invoice or invoice.state != 1:
            raise HTTPException(status_code=404, detail="Factura no encontrada")
        return invoice

    def get_invoice(
        self,
        db: Session,
        *,
        current_user: User,
        invoice_id: int,
    ) -> InvoiceRead:
        invoice = self._get_invoice_or_404(db, invoice_id)
        self._assert_can_view_invoice(current_user, invoice)
        return self._map_invoice(invoice)

    def list_invoices(
        self,
        db: Session,
        *,
        current_user: User,
        status_list: Optional[List[str]] = None,
        client_id: Optional[int] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        with_debt: Optional[bool] = None,
    ) -> List[InvoiceRead]:
        role = get_role_name(current_user)
        if role in (ROLE_ADMIN, ROLE_ADVISOR):
            invoices = invoice_crud.list(
                db,
                status_list=status_list,
                client_id=client_id,
                from_date=from_date,
                to_date=to_date,
                with_debt=with_debt,
            )
        elif role == ROLE_TECHNICIAN:
            invoices = invoice_crud.list_for_technician(db, current_user.id)
            invoices = self._apply_in_memory_filters(
                invoices,
                status_list=status_list,
                from_date=from_date,
                to_date=to_date,
                with_debt=with_debt,
            )
        elif role == ROLE_CLIENT:
            invoices = invoice_crud.list(
                db,
                status_list=status_list,
                client_id=current_user.id,
                from_date=from_date,
                to_date=to_date,
                with_debt=with_debt,
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Rol sin acceso a facturas",
            )

        return [self._map_invoice(inv) for inv in invoices]

    def update_invoice(
        self,
        db: Session,
        *,
        current_user: User,
        invoice_id: int,
        payload,  # InvoiceUpdate
    ) -> InvoiceRead:
        """
        Actualiza una factura DRAFT. Permite agregar mano de obra, descuentos, etc.
        Si confirm=True, cambia el estado a PENDING.
        """
        self._ensure_can_create(current_user)  # Solo admin/asesor

        invoice = self._get_invoice_or_404(db, invoice_id)

        # Solo se pueden editar facturas en DRAFT
        if invoice.status.upper() != "DRAFT":
            raise HTTPException(
                status_code=400,
                detail="Solo se pueden editar facturas en estado borrador (DRAFT)",
            )

        # Obtener valores actuales o nuevos
        parts_cost = Decimal(str(invoice.parts_cost or 0))
        labor_cost = Decimal(
            str(payload.labor_cost if payload.labor_cost is not None else invoice.labor_cost or 0)
        )
        discount = Decimal(
            str(
                payload.discount_amount
                if payload.discount_amount is not None
                else invoice.discount_amount or 0
            )
        )
        tax_percentage = Decimal(
            str(
                payload.tax_percentage
                if payload.tax_percentage is not None
                else invoice.tax_percentage or 0
            )
        )

        if labor_cost < 0 or discount < 0 or tax_percentage < 0:
            raise HTTPException(status_code=400, detail="Montos inválidos")

        subtotal = parts_cost + labor_cost - discount
        if subtotal < 0:
            raise HTTPException(
                status_code=400,
                detail="El descuento excede la suma de repuestos y mano de obra",
            )

        tax_amount = (subtotal * tax_percentage) / Decimal("100")
        total = subtotal + tax_amount

        update_data = {
            "labor_cost": labor_cost,
            "discount_amount": discount,
            "subtotal": subtotal,
            "tax_percentage": tax_percentage,
            "tax_amount": tax_amount,
            "total": total,
        }

        if payload.due_date is not None:
            update_data["due_date"] = payload.due_date
        if payload.notes is not None:
            update_data["notes"] = payload.notes

        # Si confirm=True, cambiar a PENDING
        if payload.confirm:
            update_data["status"] = "PENDING"

        invoice_crud.update(db, invoice, update_data)
        db.commit()

        return self._map_invoice(self._get_invoice_or_404(db, invoice_id))

    def register_payment(
        self,
        db: Session,
        *,
        current_user: User,
        payload: InvoicePaymentCreate,
    ) -> InvoiceRead:
        self._ensure_can_register_payment(current_user)

        invoice = self._get_invoice_or_404(db, payload.invoice_id)

        amount = Decimal(str(payload.amount))
        if amount <= 0:
            raise HTTPException(status_code=400, detail="El monto debe ser positivo")

        total_paid = self._sum_payments(invoice)
        outstanding = Decimal(invoice.total or 0) - total_paid

        if amount > outstanding:
            raise HTTPException(
                status_code=400,
                detail="El pago excede el saldo pendiente",
            )

        payment_data = {
            "invoice_id": invoice.id,
            "amount": amount,
            "payment_method": payload.payment_method,
            "reference": payload.reference,
            "paid_at": payload.paid_at or datetime.utcnow(),
            "created_by_id": current_user.id,
        }
        invoice_payment_crud.create(db, payment_data)

        new_total_paid = total_paid + amount
        update_payload = {}
        if new_total_paid >= Decimal(invoice.total or 0):
            update_payload["status"] = "PAID"
            update_payload["paid_at"] = datetime.utcnow()
        elif new_total_paid > 0:
            update_payload["status"] = "PENDING"
            update_payload["paid_at"] = None

        if update_payload:
            invoice_crud.update(db, invoice, update_payload)

        db.commit()
        return self._map_invoice(self._get_invoice_or_404(db, invoice.id))

    def list_payments_for_invoice(
        self,
        db: Session,
        *,
        current_user: User,
        invoice_id: int,
    ) -> List[InvoicePaymentRead]:
        invoice = self._get_invoice_or_404(db, invoice_id)
        self._assert_can_view_invoice(current_user, invoice)
        active = [payment for payment in invoice.payments if payment.state == 1]
        ordered = sorted(
            active,
            key=lambda p: p.paid_at or p.created_at or datetime.min,
            reverse=True,
        )
        return [self._map_payment(payment) for payment in ordered]


invoice_service = InvoiceService()
