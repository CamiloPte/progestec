from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.mixins import PKMixin, TimestampStateMixin


class TicketStatus(Base, PKMixin, TimestampStateMixin):
    __tablename__ = "ticket_status"

    code = Column(
        String(50), unique=True, nullable=False
    )  # RECEIVED, ASSIGNED, DIAGNOSIS, REPAIR, WAITING_PART, REPAIRED, READY, IN_TRANSIT, DELIVERED, CLOSED
    name = Column(String(80), nullable=False)
    order = Column(Integer, nullable=False, default=1)

    tickets = relationship("Ticket", back_populates="status")
    histories = relationship("TicketHistory", back_populates="status")
