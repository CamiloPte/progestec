from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy import text
from app.db.base_class import Base
from app.models.mixins import TimestampStateMixin, PKMixin

class Ticket(Base, PKMixin, TimestampStateMixin):
    __tablename__ = "tickets"

    device_id = Column(Integer, ForeignKey("devices.id", onupdate="CASCADE", ondelete="RESTRICT"), nullable=False, index=True)
    assignee_user_id = Column(Integer, ForeignKey("users.id", onupdate="CASCADE", ondelete="SET NULL"), index=True)
    status_id = Column(Integer, ForeignKey("ticket_status.id", onupdate="CASCADE", ondelete="RESTRICT"), nullable=False, index=True)

    failure_desc = Column(String(2000), nullable=False)
    diagnosis = Column(String(4000))
    cost_estimate = Column(Numeric(12, 2))
    approved_by_owner = Column(Integer)  # 1/0 (bool), puedes cambiar a TINYINT en schemas si prefieres

    intake_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    ready_at = Column(DateTime)
    delivered_at = Column(DateTime)
    closed_at = Column(DateTime)

    tracking_code = Column(String(30), unique=True, nullable=False, index=True)

    device = relationship("Device", back_populates="tickets")
    assignee = relationship("User", back_populates="assigned_tickets")
    status = relationship("TicketStatus", back_populates="tickets")

    history = relationship("TicketHistory", back_populates="ticket", cascade="all,delete", passive_deletes=True)
    issues = relationship("TicketIssue", back_populates="ticket", cascade="all,delete", passive_deletes=True)
    ticket_services = relationship("TicketService", back_populates="ticket", cascade="all,delete", passive_deletes=True)
    ticket_parts = relationship("TicketPart",back_populates="ticket",lazy="selectin",cascade="all, delete-orphan",)
    invoice = relationship("Invoice", back_populates="ticket", uselist=False)
    delivery_orders = relationship("DeliveryOrder", back_populates="ticket", cascade="all,delete", passive_deletes=True)
    claim_codes = relationship("ClaimCode", back_populates="ticket", cascade="all,delete", passive_deletes=True)
    attachments = relationship("TicketAttachment", back_populates="ticket", cascade="all,delete", passive_deletes=True)
