from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from app.models.mixins import TimestampStateMixin, PKMixin

class AttributeUser(Base, PKMixin, TimestampStateMixin):
    __tablename__ = "attribute_users"

    user_id = Column(Integer, ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False, index=True)
    attribute_id = Column(Integer, ForeignKey("attributes.id", onupdate="CASCADE", ondelete="RESTRICT"), nullable=False, index=True)
    type = Column(String(50))      # Text | Number | Boolean | Date (libre)
    value = Column(String(255))

    user = relationship("User", back_populates="attribute_users")
    attribute = relationship("Attribute", back_populates="attribute_users")
