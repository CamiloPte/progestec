from sqlalchemy import Column, Numeric, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.mixins import PKMixin, TimestampStateMixin


class Service(Base, PKMixin, TimestampStateMixin):
    __tablename__ = "services"

    name = Column(String(120), unique=True, nullable=False)
    base_price = Column(Numeric(12, 2), nullable=False)

    ticket_services = relationship("TicketService", back_populates="service")
