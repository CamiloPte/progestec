# Relación entre tickets y repuestos: qué parte se usó, cuánta, a qué costo y quién la agregó.
from sqlalchemy import Column, ForeignKey, Integer, Numeric, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.mixins import PKMixin, TimestampStateMixin


class TicketPart(Base, PKMixin, TimestampStateMixin):
    __tablename__ = "ticket_parts"
    __table_args__ = (
        # Un mismo repuesto solo aparece una vez por ticket, se acumula en qty
        UniqueConstraint("ticket_id", "part_id", name="uq_ticket_part"),
    )

    # Ticket al que pertenece esta línea
    ticket_id = Column(
        Integer,
        ForeignKey("tickets.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Repuesto utilizado
    part_id = Column(
        Integer,
        ForeignKey("parts.id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    # Cantidad de unidades del repuesto usadas en el ticket
    qty = Column(Integer, nullable=False, default=1)

    # Precio unitario "congelado" en el momento de uso (no se altera si luego cambia en inventario)
    unit_price_snapshot = Column(Numeric(12, 2), nullable=False)

    # Costo total de esta línea (qty * unit_price_snapshot) para facilitar reportes financieros
    total_cost = Column(Numeric(12, 2), nullable=False)

    # (Opcional pero muy útil) Usuario que agregó esta línea de repuesto al ticket
    created_by_id = Column(
        Integer,
        ForeignKey("users.id", onupdate="CASCADE", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Relaciones ORM
    ticket = relationship("Ticket", back_populates="ticket_parts")
    part = relationship("Part", back_populates="ticket_parts")
    created_by = relationship("User", lazy="joined")
