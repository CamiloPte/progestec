from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.mixins import PKMixin, TimestampStateMixin


class Device(Base, PKMixin, TimestampStateMixin):
    __tablename__ = "devices"

    owner_user_id = Column(
        Integer,
        ForeignKey("users.id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    type = Column(String(20), nullable=False)  # PHONE | LAPTOP | TABLET | OTHER
    brand = Column(String(50), nullable=False)
    model = Column(String(100), nullable=False)
    serial = Column(String(100), index=True)
    imei = Column(String(30), index=True)
    intake_photo = Column(String(255))
    notes = Column(String(1000))

    # Referencias opcionales al catálogo externo (Express + Supabase)
    catalog_manufacturer_id = Column(Integer, nullable=True, index=True)
    catalog_model_id = Column(Integer, nullable=True, index=True)
    catalog_variant_id = Column(Integer, nullable=True, index=True)

    owner = relationship("User", back_populates="devices")
    tickets = relationship(
        "Ticket", back_populates="device", cascade="all,delete", passive_deletes=True
    )
