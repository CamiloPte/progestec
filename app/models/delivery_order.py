from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.mixins import PKMixin, TimestampStateMixin


class DeliveryOrder(Base, PKMixin, TimestampStateMixin):
    __tablename__ = "delivery_orders"

    ticket_id = Column(
        Integer,
        ForeignKey("tickets.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    courier_user_id = Column(
        Integer, ForeignKey("users.id", onupdate="CASCADE", ondelete="SET NULL"), index=True
    )

    code = Column(String(30), unique=True, nullable=False, index=True)
    pickup_at = Column(DateTime)
    delivered_at = Column(DateTime)
    proof_photo = Column(String(255))
    status = Column(
        String(20), nullable=False, default="PENDING"
    )  # PENDING | PICKED | DELIVERED | CANCELLED

    ticket = relationship("Ticket", back_populates="delivery_orders")
    courier = relationship("User", back_populates="delivery_orders")
