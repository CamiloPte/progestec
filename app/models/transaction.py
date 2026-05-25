from sqlalchemy import Column, Integer, Numeric, String, ForeignKey, DateTime, text
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from app.models.mixins import TimestampStateMixin, PKMixin

class Transaction(Base, PKMixin, TimestampStateMixin):
    __tablename__ = "transactions"

    invoice_id = Column(Integer, ForeignKey("invoices.id", onupdate="CASCADE", ondelete="SET NULL"), index=True)
    type = Column(String(10), nullable=False)    # INCOME | EXPENSE
    amount = Column(Numeric(12, 2), nullable=False)
    method = Column(String(20), nullable=False)  # CASH | CARD | TRANSFER | OTHER
    created_by = Column(Integer, ForeignKey("users.id", onupdate="CASCADE", ondelete="SET NULL"))
    created_at = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))

    invoice = relationship("Invoice", back_populates="transactions")
