# app/schemas/ticket_part.py
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import Field

from app.schemas.common import BaseSchema


class TicketPartBase(BaseSchema):
    part_id: int = Field(..., description="ID del repuesto utilizado")
    qty: int = Field(..., gt=0, description="Cantidad de unidades usadas")


class TicketPartCreate(TicketPartBase):
    """
    Payload para agregar/registrar uso de un repuesto en un ticket.

    unit_price_snapshot:
      - Si se envía, se usa ese valor.
      - Si viene vacío, se toma el unit_price actual de Part.
    """

    unit_price_snapshot: Optional[Decimal] = Field(
        default=None,
        description="Precio unitario al momento del uso (opcional, se congela)",
    )
    movement_at: Optional[datetime] = Field(
        default=None,
        description="Fecha/hora del movimiento de inventario",
    )
    notes: Optional[str] = Field(
        default=None,
        description="Notas del uso del repuesto (ej: 'Cambio de pantalla')",
    )


class TicketPartRead(BaseSchema):
    id: int
    ticket_id: int
    part_id: int
    qty: int
    unit_price_snapshot: Decimal
    total_cost: Decimal
    created_by_id: Optional[int]
    created_at: datetime
    state: int

    # Campos derivados para el front
    part_name: Optional[str] = None
    part_sku: Optional[str] = None
