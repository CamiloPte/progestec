from sqlalchemy import Column, Integer, DateTime, text
from sqlalchemy.orm import declared_attr
from sqlalchemy.dialects.mysql import TINYINT

class TimestampStateMixin:
    # 1 = activo, 0 = inactivo (soft delete)
    state = Column(TINYINT(1), nullable=False, server_default=text("1"))
    created_at = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        server_onupdate=text("CURRENT_TIMESTAMP")
    )

class PKMixin:
    id = Column(Integer, primary_key=True, index=True)
