from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.mixins import PKMixin, TimestampStateMixin


class TicketIssue(Base, PKMixin, TimestampStateMixin):
    __tablename__ = "ticket_issues"

    ticket_id = Column(
        Integer,
        ForeignKey("tickets.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    type = Column(String(20), nullable=False)  # REPORTED | DISCOVERED
    title = Column(String(120), nullable=False)
    description = Column(String(2000))
    discovered_at = Column(DateTime)
    discovered_by = Column(Integer, ForeignKey("users.id", onupdate="CASCADE", ondelete="SET NULL"))
    resolved_at = Column(DateTime)
    is_primary = Column(Integer)  # 1/0

    ticket = relationship("Ticket", back_populates="issues")
