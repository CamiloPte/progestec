from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.mixins import PKMixin, TimestampStateMixin


# esta tabla es para asignar que modulos puede ver cada rol
class ModuleRole(Base, PKMixin, TimestampStateMixin):
    __tablename__ = "module_roles"
    __table_args__ = (UniqueConstraint("role_id", "module_id", name="uq_role_module"),)

    role_id = Column(
        Integer,
        ForeignKey("roles.id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    module_id = Column(
        Integer,
        ForeignKey("modules.id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    description = Column(String(255))

    role = relationship("Role", back_populates="module_roles")
    module = relationship("Module", back_populates="module_roles")
