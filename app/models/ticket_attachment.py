from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.mixins import TimestampStateMixin, PKMixin

class TicketAttachment(Base, PKMixin, TimestampStateMixin):
    __tablename__ = "ticket_attachments"

    ticket_id = Column(
        Integer,
        ForeignKey("tickets.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    history_id = Column(
        Integer,
        ForeignKey("ticket_history.id", onupdate="CASCADE", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    uploaded_by = Column(
        Integer,
        ForeignKey("users.id", onupdate="CASCADE", ondelete="SET NULL"),
        nullable=True,
    )

    attachment_type = Column(String(50), nullable=False)  # diagnosis | budget | status
    original_name = Column(String(255), nullable=False)
    stored_name = Column(String(255), nullable=False)
    mime_type = Column(String(100), nullable=True)
    file_size = Column(Integer, nullable=True)
    file_url = Column(String(500), nullable=False)
    note = Column(String(1000), nullable=True)

    ticket = relationship("Ticket", back_populates="attachments")
    history = relationship("TicketHistory", back_populates="attachments")
    uploader = relationship("User")
