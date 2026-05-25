from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from app.models.mixins import TimestampStateMixin, PKMixin

class Role(Base, PKMixin, TimestampStateMixin):
    __tablename__ = "roles"

    name = Column(String(50), unique=True, nullable=False)  # ADMIN, TECHNICIAN, ADVISOR, COURIER, CLIENT
    description = Column(String(255))

    users = relationship("User", back_populates="role", cascade="all,delete", passive_deletes=True)
    module_roles = relationship("ModuleRole", back_populates="role", cascade="all,delete", passive_deletes=True)
