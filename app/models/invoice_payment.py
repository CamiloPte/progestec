from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String, text
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.mixins import PKMixin, TimestampStateMixin


class InvoicePayment(Base, PKMixin, TimestampStateMixin):
    __tablename__ = "invoice_payments"

    invoice_id = Column(
        Integer,
        ForeignKey("invoices.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    amount = Column(Numeric(12, 2), nullable=False)
    payment_method = Column(String(30), nullable=False)
    reference = Column(String(100))
    paid_at = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    created_by_id = Column(
        Integer,
        ForeignKey("users.id", onupdate="CASCADE", ondelete="SET NULL"),
        nullable=True,
    )

    invoice = relationship("Invoice", back_populates="payments")
    created_by = relationship("User")
