from sqlalchemy import (
    Column,
    Integer,
    Numeric,
    String,
    ForeignKey,
    DateTime,
    Text,
    text,
)
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.mixins import TimestampStateMixin, PKMixin


class Invoice(Base, PKMixin, TimestampStateMixin):
    __tablename__ = "invoices"

    ticket_id = Column(
        Integer,
        ForeignKey("tickets.id", onupdate="CASCADE", ondelete="RESTRICT"),
        unique=True,
        nullable=False,
        index=True,
    )
    client_id = Column(
        Integer,
        ForeignKey("users.id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    invoice_number = Column(String(40), nullable=False, unique=True, index=True)
    issue_date = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    due_date = Column(DateTime)

    parts_cost = Column(Numeric(12, 2), nullable=False, server_default=text("0"))
    labor_cost = Column(Numeric(12, 2), nullable=False, server_default=text("0"))
    discount_amount = Column(Numeric(12, 2), nullable=False, server_default=text("0"))
    subtotal = Column(Numeric(12, 2), nullable=False, server_default=text("0"))
    tax_percentage = Column(Numeric(5, 2), nullable=False, server_default=text("0"))
    tax_amount = Column(Numeric(12, 2), nullable=False, server_default=text("0"))
    total = Column(Numeric(12, 2), nullable=False, server_default=text("0"))

    status = Column(String(20), nullable=False, server_default=text("'PENDING'"))
    created_by_id = Column(
        Integer,
        ForeignKey("users.id", onupdate="CASCADE", ondelete="SET NULL"),
        nullable=True,
    )
    paid_at = Column(DateTime)
    notes = Column(Text)

    ticket = relationship("Ticket", back_populates="invoice")
    client = relationship("User", foreign_keys=[client_id])
    creator = relationship("User", foreign_keys=[created_by_id])
    payments = relationship(
        "InvoicePayment",
        back_populates="invoice",
        cascade="all,delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )

