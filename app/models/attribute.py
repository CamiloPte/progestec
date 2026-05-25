from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from app.models.mixins import TimestampStateMixin, PKMixin

class Attribute(Base, PKMixin, TimestampStateMixin):
    __tablename__ = "attributes"

    name = Column(String(100), nullable=False)
    description = Column(String(255))

    attribute_users = relationship("AttributeUser", back_populates="attribute", cascade="all,delete", passive_deletes=True)
