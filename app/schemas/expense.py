from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import Field

from app.schemas.common import BaseSchema, TimestampSchema


# ---------- ExpenseCategory Schemas ----------
class ExpenseCategoryBase(BaseSchema):
    name: str = Field(..., max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    icon: Optional[str] = Field(None, max_length=50)


class ExpenseCategoryCreate(ExpenseCategoryBase):
    pass


class ExpenseCategoryUpdate(BaseSchema):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    icon: Optional[str] = Field(None, max_length=50)
    state: Optional[int] = None


class ExpenseCategoryRead(TimestampSchema):
    id: int
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    state: int


# ---------- Expense Schemas ----------
class ExpenseBase(BaseSchema):
    category_id: int
    description: str = Field(..., max_length=255)
    amount: Decimal = Field(..., gt=0)
    payment_method: str = Field(..., max_length=30)
    reference: Optional[str] = Field(None, max_length=100)
    expense_date: Optional[datetime] = None
    part_id: Optional[int] = None
    quantity: Optional[int] = Field(None, ge=1)
    supplier_name: Optional[str] = Field(None, max_length=150)
    supplier_rut: Optional[str] = Field(None, max_length=20)
    notes: Optional[str] = None


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseUpdate(BaseSchema):
    category_id: Optional[int] = None
    description: Optional[str] = Field(None, max_length=255)
    amount: Optional[Decimal] = Field(None, gt=0)
    payment_method: Optional[str] = Field(None, max_length=30)
    reference: Optional[str] = Field(None, max_length=100)
    expense_date: Optional[datetime] = None
    part_id: Optional[int] = None
    quantity: Optional[int] = Field(None, ge=1)
    supplier_name: Optional[str] = Field(None, max_length=150)
    supplier_rut: Optional[str] = Field(None, max_length=20)
    notes: Optional[str] = None
    state: Optional[int] = None


class ExpenseRead(TimestampSchema):
    id: int
    category_id: int
    category_name: Optional[str] = None
    description: str
    amount: float
    payment_method: str
    reference: Optional[str] = None
    expense_date: datetime
    part_id: Optional[int] = None
    part_name: Optional[str] = None
    quantity: Optional[int] = None
    supplier_name: Optional[str] = None
    supplier_rut: Optional[str] = None
    notes: Optional[str] = None
    created_by_id: Optional[int] = None
    created_by_name: Optional[str] = None
    state: int
