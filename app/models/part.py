from sqlalchemy import Column, String, Numeric, Integer, Text, Boolean
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from app.models.mixins import TimestampStateMixin, PKMixin

class Part(Base, PKMixin, TimestampStateMixin):
    __tablename__ = "parts"

    name = Column(String(150), nullable=False)
    sku = Column(String(100), index=True, unique=True)
    unit_price = Column(Numeric(12, 2), nullable=False)

    category = Column(String(100))
    manufacturer = Column(String(100))
    compatible_models = Column(Text)
    preferred_vendor = Column(String(150))
    notes = Column(Text)
    stock_current = Column(Integer, nullable=False, default=0)
    stock_min = Column(Integer, nullable=False, default=0)
    requires_approval = Column(Boolean, nullable=False, default=False)

    ticket_parts = relationship("TicketPart",back_populates="part",lazy="selectin",)
    movements = relationship("PartMovement",back_populates="part",cascade="all,delete",passive_deletes=True,)
    expenses = relationship("Expense", back_populates="part")
