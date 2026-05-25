from typing import Any, Dict, List

from sqlalchemy.orm import Session

from app.models.invoice_payment import InvoicePayment


class InvoicePaymentCRUD:
    def create(self, db: Session, data: Dict[str, Any]) -> InvoicePayment:
        payment = InvoicePayment(**data)
        db.add(payment)
        db.flush()
        return payment

    def list_by_invoice(self, db: Session, invoice_id: int) -> List[InvoicePayment]:
        return (
            db.query(InvoicePayment)
            .filter(InvoicePayment.invoice_id == invoice_id, InvoicePayment.state == 1)
            .order_by(InvoicePayment.paid_at.desc())
            .all()
        )


invoice_payment_crud = InvoicePaymentCRUD()
