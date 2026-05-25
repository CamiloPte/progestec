from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, text
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.mixins import PKMixin, TimestampStateMixin


class TicketHistory(Base, PKMixin, TimestampStateMixin):
    __tablename__ = "ticket_history"

    ticket_id = Column(
        Integer,
        ForeignKey("tickets.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status_id = Column(
        Integer,
        ForeignKey("ticket_status.id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    user_id = Column(
        Integer, ForeignKey("users.id", onupdate="CASCADE", ondelete="SET NULL"), index=True
    )

    note = Column(String(2000))
    created_at = Column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )  # histórico inmutable

    ticket = relationship("Ticket", back_populates="history")
    status = relationship("TicketStatus", back_populates="histories")
    user = relationship("User", back_populates="ticket_histories")
    attachments = relationship(
        "TicketAttachment", back_populates="history", cascade="all,delete", passive_deletes=True
    )
