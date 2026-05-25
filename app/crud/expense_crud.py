from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models.expense import Expense, ExpenseCategory


class ExpenseCategoryCRUD:
    def create(self, db: Session, data: Dict[str, Any]) -> ExpenseCategory:
        category = ExpenseCategory(**data)
        db.add(category)
        db.flush()
        return category

    def update(
        self, db: Session, category: ExpenseCategory, data: Dict[str, Any]
    ) -> ExpenseCategory:
        for field, value in data.items():
            setattr(category, field, value)
        db.flush()
        return category

    def get(self, db: Session, category_id: int) -> Optional[ExpenseCategory]:
        return (
            db.query(ExpenseCategory)
            .filter(ExpenseCategory.id == category_id, ExpenseCategory.state == 1)
            .first()
        )

    def get_by_name(self, db: Session, name: str) -> Optional[ExpenseCategory]:
        return (
            db.query(ExpenseCategory)
            .filter(ExpenseCategory.name == name, ExpenseCategory.state == 1)
            .first()
        )

    def list(self, db: Session) -> Sequence[ExpenseCategory]:
        return (
            db.query(ExpenseCategory)
            .filter(ExpenseCategory.state == 1)
            .order_by(ExpenseCategory.name)
            .all()
        )


class ExpenseCRUD:
    def create(self, db: Session, data: Dict[str, Any]) -> Expense:
        expense = Expense(**data)
        db.add(expense)
        db.flush()
        return expense

    def update(self, db: Session, expense: Expense, data: Dict[str, Any]) -> Expense:
        for field, value in data.items():
            setattr(expense, field, value)
        db.flush()
        return expense

    def get(self, db: Session, expense_id: int) -> Optional[Expense]:
        return (
            db.query(Expense)
            .options(
                joinedload(Expense.category),
                joinedload(Expense.part),
                joinedload(Expense.creator),
            )
            .filter(Expense.id == expense_id, Expense.state == 1)
            .first()
        )

    def list(
        self,
        db: Session,
        *,
        category_id: Optional[int] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        payment_method: Optional[str] = None,
        part_id: Optional[int] = None,
    ) -> Sequence[Expense]:
        query = (
            db.query(Expense)
            .options(
                joinedload(Expense.category),
                joinedload(Expense.part),
                joinedload(Expense.creator),
            )
            .filter(Expense.state == 1)
        )

        if category_id:
            query = query.filter(Expense.category_id == category_id)

        if from_date:
            query = query.filter(Expense.expense_date >= from_date)
        if to_date:
            query = query.filter(Expense.expense_date <= to_date)

        if payment_method:
            query = query.filter(Expense.payment_method == payment_method.upper())

        if part_id:
            query = query.filter(Expense.part_id == part_id)

        return query.order_by(Expense.expense_date.desc()).all()

    def sum_by_period(
        self,
        db: Session,
        *,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
    ) -> float:
        """Suma total de gastos en un período."""
        query = db.query(func.coalesce(func.sum(Expense.amount), 0)).filter(Expense.state == 1)

        if from_date:
            query = query.filter(Expense.expense_date >= from_date)
        if to_date:
            query = query.filter(Expense.expense_date <= to_date)

        result = query.scalar()
        return float(result) if result else 0.0

    def sum_by_category(
        self,
        db: Session,
        *,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """Suma de gastos agrupados por categoría."""
        query = (
            db.query(
                ExpenseCategory.id.label("category_id"),
                ExpenseCategory.name.label("category_name"),
                func.coalesce(func.sum(Expense.amount), 0).label("total"),
                func.count(Expense.id).label("count"),
            )
            .join(Expense, Expense.category_id == ExpenseCategory.id)
            .filter(Expense.state == 1, ExpenseCategory.state == 1)
            .group_by(ExpenseCategory.id, ExpenseCategory.name)
        )

        if from_date:
            query = query.filter(Expense.expense_date >= from_date)
        if to_date:
            query = query.filter(Expense.expense_date <= to_date)

        results = query.all()
        return [
            {
                "category_id": r.category_id,
                "category_name": r.category_name,
                "total": float(r.total),
                "count": r.count,
            }
            for r in results
        ]

    def monthly_totals(
        self,
        db: Session,
        *,
        months_back: int = 6,
    ) -> List[Dict[str, Any]]:
        """Totales mensuales de gastos para gráficos de tendencia."""
        from datetime import datetime

        from dateutil.relativedelta import relativedelta

        end_date = datetime.utcnow()
        start_date = end_date - relativedelta(months=months_back)

        query = (
            db.query(
                func.date_format(Expense.expense_date, "%Y-%m").label("period"),
                func.coalesce(func.sum(Expense.amount), 0).label("total"),
            )
            .filter(
                Expense.state == 1,
                Expense.expense_date >= start_date,
                Expense.expense_date <= end_date,
            )
            .group_by(func.date_format(Expense.expense_date, "%Y-%m"))
            .order_by(func.date_format(Expense.expense_date, "%Y-%m"))
        )

        results = query.all()
        return [{"period": r.period, "expenses": float(r.total)} for r in results]


expense_category_crud = ExpenseCategoryCRUD()
expense_crud = ExpenseCRUD()
