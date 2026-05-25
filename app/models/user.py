from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import Boolean
from app.db.base_class import Base
from app.models.mixins import TimestampStateMixin, PKMixin

class User(Base, PKMixin, TimestampStateMixin):
    __tablename__ = "users"

    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255))
    identification = Column(String(50), unique=True, nullable=False)
    identification_type = Column(String(10))
    phone = Column(String(20), unique=True)
    hashed_password = Column(String(255), nullable=False)
    must_change_password = Column(Boolean, nullable=False, default=False, server_default="0")

    role_id = Column(Integer, ForeignKey("roles.id", onupdate="CASCADE", ondelete="RESTRICT"), nullable=False, index=True)

    role = relationship("Role", back_populates="users")
    attribute_users = relationship("AttributeUser", back_populates="user", cascade="all,delete", passive_deletes=True)

    # ownership & assignments
    devices = relationship("Device", back_populates="owner", cascade="all,delete", passive_deletes=True)
    assigned_tickets = relationship("Ticket", back_populates="assignee", foreign_keys="Ticket.assignee_user_id")
    ticket_histories = relationship("TicketHistory", back_populates="user")
    delivery_orders = relationship("DeliveryOrder", back_populates="courier")
