from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence

import sqlalchemy as sa
from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload

from app.models.device import Device
from app.models.invoice import Invoice
from app.models.invoice_payment import InvoicePayment
from app.models.ticket import Ticket


class InvoiceCRUD:
    def create(self, db: Session, data: Dict[str, Any]) -> Invoice:
        invoice = Invoice(**data)
        db.add(invoice)
        db.flush()
        return invoice

    def update(self, db: Session, invoice: Invoice, data: Dict[str, Any]) -> Invoice:
        for field, value in data.items():
            setattr(invoice, field, value)
        db.flush()
        return invoice

    def get(self, db: Session, invoice_id: int) -> Optional[Invoice]:
        return (
            db.query(Invoice)
            .options(
                selectinload(Invoice.ticket).selectinload(Ticket.device).selectinload(Device.owner),
                selectinload(Invoice.payments),
            )
            .filter(Invoice.id == invoice_id, Invoice.state == 1)
            .first()
        )

    def get_by_ticket_id(self, db: Session, ticket_id: int) -> Optional[Invoice]:
        return db.query(Invoice).filter(Invoice.ticket_id == ticket_id, Invoice.state == 1).first()

    def list(
        self,
        db: Session,
        *,
        status_list: Optional[List[str]] = None,
        client_id: Optional[int] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        with_debt: Optional[bool] = None,
    ) -> Sequence[Invoice]:
        query = (
            db.query(Invoice)
            .options(
                selectinload(Invoice.ticket).selectinload(Ticket.device).selectinload(Device.owner),
                selectinload(Invoice.payments),
            )
            .filter(Invoice.state == 1)
        )

        if status_list:
            upper = [s.upper() for s in status_list]
            query = query.filter(Invoice.status.in_(upper))

        if client_id:
            query = query.filter(Invoice.client_id == client_id)

        if from_date:
            query = query.filter(Invoice.issue_date >= from_date)
        if to_date:
            query = query.filter(Invoice.issue_date <= to_date)

        if with_debt:
            payments_total = (
                sa.select(func.coalesce(func.sum(InvoicePayment.amount), 0))
                .where(InvoicePayment.invoice_id == Invoice.id)
                .correlate(Invoice)
                .scalar_subquery()
            )
            query = query.filter((Invoice.total - payments_total) > 0)

        return query.order_by(Invoice.issue_date.desc()).all()

    def list_for_technician(self, db: Session, technician_id: int) -> Sequence[Invoice]:
        return (
            db.query(Invoice)
            .join(Invoice.ticket)
            .filter(Invoice.state == 1, Ticket.assignee_user_id == technician_id)
            .options(
                selectinload(Invoice.ticket).selectinload(Ticket.device).selectinload(Device.owner),
                selectinload(Invoice.payments),
            )
            .order_by(Invoice.issue_date.desc())
            .all()
        )


invoice_crud = InvoiceCRUD()
