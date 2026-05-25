from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime, func
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.mixins import PKMixin, TimestampStateMixin


class PartMovement(Base, PKMixin, TimestampStateMixin):
    __tablename__ = "part_movements"

    part_id = Column(Integer, ForeignKey("parts.id", ondelete="CASCADE"), nullable=False)
    movement_type = Column(String(20), nullable=False)  # IN, OUT
    quantity = Column(Integer, nullable=False)
    document_ref = Column(String(100))
    movement_at = Column(DateTime, nullable=False, server_default=func.now())
    responsible_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    notes = Column(Text)

    part = relationship("Part", back_populates="movements")
    responsible = relationship("User")
