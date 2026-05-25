from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security_deps import get_current_user
from app.models.user import User
from app.schemas.expense import (
    ExpenseCreate,
    ExpenseRead,
    ExpenseCategoryCreate,
    ExpenseCategoryRead,
)
from app.schemas.finance import FinanceSummary
from app.services.finance_service import finance_service


router = APIRouter(prefix="/finances", tags=["Finances"])


# ========== DASHBOARD / SUMMARY ==========
@router.get("/summary", response_model=FinanceSummary)
def get_finance_summary(
    from_date: Optional[datetime] = Query(None),
    to_date: Optional[datetime] = Query(None),
    include_trends: bool = Query(True),
    months_back: int = Query(6, ge=1, le=24),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Obtiene resumen financiero completo.
    
    - **from_date**: Fecha de inicio del período
    - **to_date**: Fecha fin del período
    - **include_trends**: Incluir tendencias mensuales
    - **months_back**: Meses hacia atrás para tendencias (default 6)
    """
    return finance_service.get_summary(
        db,
        current_user=current_user,
        from_date=from_date,
        to_date=to_date,
        include_trends=include_trends,
        months_back=months_back,
    )


# ========== EXPENSE CATEGORIES ==========
@router.get("/expense-categories", response_model=List[ExpenseCategoryRead])
def list_expense_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lista todas las categorías de gastos."""
    return finance_service.list_categories(db, current_user=current_user)


@router.post(
    "/expense-categories",
    response_model=ExpenseCategoryRead,
    status_code=status.HTTP_201_CREATED,
)
def create_expense_category(
    payload: ExpenseCategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Crea una nueva categoría de gastos."""
    return finance_service.create_category(db, current_user=current_user, payload=payload)


# ========== EXPENSES ==========
@router.get("/expenses", response_model=List[ExpenseRead])
def list_expenses(
    category_id: Optional[int] = Query(None),
    from_date: Optional[datetime] = Query(None),
    to_date: Optional[datetime] = Query(None),
    payment_method: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Lista gastos con filtros opcionales.
    
    - **category_id**: Filtrar por categoría
    - **from_date**: Desde fecha
    - **to_date**: Hasta fecha
    - **payment_method**: CASH, CARD, TRANSFER, OTHER
    """
    return finance_service.list_expenses(
        db,
        current_user=current_user,
        category_id=category_id,
        from_date=from_date,
        to_date=to_date,
        payment_method=payment_method,
    )


@router.post(
    "/expenses",
    response_model=ExpenseRead,
    status_code=status.HTTP_201_CREATED,
)
def create_expense(
    payload: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Registra un nuevo gasto.
    
    Si se incluye part_id y quantity, automáticamente se actualiza
    el stock del repuesto (compra de inventario).
    """
    return finance_service.create_expense(db, current_user=current_user, payload=payload)


@router.get("/expenses/{expense_id}", response_model=ExpenseRead)
def get_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obtiene detalle de un gasto."""
    return finance_service.get_expense(db, current_user=current_user, expense_id=expense_id)


@router.delete("/expenses/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Elimina (soft delete) un gasto."""
    finance_service.delete_expense(db, current_user=current_user, expense_id=expense_id)
    return None
