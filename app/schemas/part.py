from typing import Optional, Dict
from datetime import datetime

from app.schemas.common import BaseSchema, TimestampSchema


class PartBase(BaseSchema):
    name: str
    sku: Optional[str] = None
    unit_price: float
    category: Optional[str] = None
    manufacturer: Optional[str] = None
    compatible_models: Optional[str] = None
    preferred_vendor: Optional[str] = None
    notes: Optional[str] = None
    stock_current: int = 0
    stock_min: int = 0
    requires_approval: bool = False


class PartCreate(PartBase):
    pass


class PartUpdate(BaseSchema):
    name: Optional[str] = None
    sku: Optional[str] = None
    unit_price: Optional[float] = None
    category: Optional[str] = None
    manufacturer: Optional[str] = None
    compatible_models: Optional[str] = None
    preferred_vendor: Optional[str] = None
    notes: Optional[str] = None
    stock_current: Optional[int] = None
    stock_min: Optional[int] = None
    requires_approval: Optional[bool] = None
    state: Optional[int] = None


class PartRead(TimestampSchema):
    id: int
    name: str
    sku: Optional[str] = None
    unit_price: float
    category: Optional[str] = None
    manufacturer: Optional[str] = None
    compatible_models: Optional[str] = None
    preferred_vendor: Optional[str] = None
    notes: Optional[str] = None
    stock_current: int
    stock_min: int
    requires_approval: bool
    state: int
    last_movement_at: Optional[datetime] = None


class PartMovementCreate(BaseSchema):
    movement_type: str  # IN / OUT
    quantity: int
    document_ref: Optional[str] = None
    movement_at: Optional[datetime] = None
    notes: Optional[str] = None


class PartMovementRead(TimestampSchema):
    id: int
    movement_type: str
    quantity: int
    document_ref: Optional[str] = None
    movement_at: datetime
    responsible_user_id: Optional[int] = None
    responsible_name: Optional[str] = None
    notes: Optional[str] = None


class InventorySummary(BaseSchema):
    total_stock: int
    low_stock_alerts: int
    movements_today: int
    critical_parts: int
    stock_by_category: Dict[str, int]


class PartDetailRead(PartRead):
    movements: list[PartMovementRead] = []
