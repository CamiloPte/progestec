from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.mixins import PKMixin, TimestampStateMixin


class ClaimCode(Base, PKMixin, TimestampStateMixin):
    __tablename__ = "claim_codes"

    ticket_id = Column(
        Integer, ForeignKey("tickets.id", onupdate="CASCADE", ondelete="CASCADE"), index=True
    )
    device_id = Column(
        Integer, ForeignKey("devices.id", onupdate="CASCADE", ondelete="CASCADE"), index=True
    )

    code = Column(String(30), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime)
    used_at = Column(DateTime)

    ticket = relationship("Ticket", back_populates="claim_codes")
    device = relationship("Device")
