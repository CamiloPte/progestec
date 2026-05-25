from typing import Optional
from datetime import datetime
from decimal import Decimal
from app.schemas.common import BaseSchema, TimestampSchema

class TransactionBase(BaseSchema):
    invoice_id: Optional[int] = None
    type: str             # INCOME | EXPENSE
    amount: Decimal
    method: str           # CASH | CARD | TRANSFER | OTHER
    created_by: Optional[int] = None


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseSchema):
    type: Optional[str] = None
    amount: Optional[Decimal] = None
    method: Optional[str] = None
    state: Optional[int] = None


class TransactionRead(TimestampSchema):
    id: int
    invoice_id: Optional[int] = None
    type: str
    amount: Decimal
    method: str
    created_by: Optional[int] = None
    state: int
