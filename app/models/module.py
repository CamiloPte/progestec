from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from app.models.mixins import TimestampStateMixin, PKMixin

class Module(Base, PKMixin, TimestampStateMixin):
    __tablename__ = "modules"

    name = Column(String(100), unique=True, nullable=False)   # users, tickets, inventory, finance, reports
    description = Column(String(255))

    module_roles = relationship("ModuleRole", back_populates="module", cascade="all,delete", passive_deletes=True)
