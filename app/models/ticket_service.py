from sqlalchemy import Column, ForeignKey, Integer, Numeric, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.mixins import PKMixin, TimestampStateMixin


class TicketService(Base, PKMixin, TimestampStateMixin):
    __tablename__ = "ticket_services"
    __table_args__ = (UniqueConstraint("ticket_id", "service_id", name="uq_ticket_service"),)

    ticket_id = Column(
        Integer,
        ForeignKey("tickets.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    service_id = Column(
        Integer,
        ForeignKey("services.id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    qty = Column(Integer, nullable=False, default=1)
    unit_price_snapshot = Column(Numeric(12, 2), nullable=False)

    ticket = relationship("Ticket", back_populates="ticket_services")
    service = relationship("Service", back_populates="ticket_services")
