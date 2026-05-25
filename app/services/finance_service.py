from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Dict, Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from dateutil.relativedelta import relativedelta

from app.core.roles import ROLE_ADMIN, ROLE_ADVISOR, get_role_name
from app.crud.expense_crud import expense_crud, expense_category_crud
from app.crud.invoice_crud import invoice_crud
from app.crud.invoice_payment_crud import invoice_payment_crud
from app.models.expense import Expense, ExpenseCategory
from app.models.invoice import Invoice
from app.models.invoice_payment import InvoicePayment
from app.models.user import User
from app.schemas.expense import (
    ExpenseCreate,
    ExpenseRead,
    ExpenseCategoryCreate,
    ExpenseCategoryRead,
)
from app.schemas.finance import (
    FinanceSummary,
    CategoryExpenseSummary,
    PeriodMetrics,
    TopClient,
)


class FinanceService:
    """Servicio de lógica de negocio para finanzas."""

    ALLOWED_ROLES = (ROLE_ADMIN, ROLE_ADVISOR)

    # ---------- Permisos ----------
    def _ensure_finance_access(self, user: User) -> None:
        if get_role_name(user) not in self.ALLOWED_ROLES:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acceso denegado al módulo financiero",
            )

    # ---------- Mappers ----------
    def _map_expense(self, expense: Expense) -> ExpenseRead:
        category_name = expense.category.name if expense.category else None
        part_name = expense.part.name if expense.part else None
        creator_name = None
        if expense.creator:
            creator_name = expense.creator.full_name or expense.creator.email

        return ExpenseRead(
            id=expense.id,
            category_id=expense.category_id,
            category_name=category_name,
            description=expense.description,
            amount=float(expense.amount),
            payment_method=expense.payment_method,
            reference=expense.reference,
            expense_date=expense.expense_date,
            part_id=expense.part_id,
            part_name=part_name,
            quantity=expense.quantity,
            supplier_name=expense.supplier_name,
            supplier_rut=expense.supplier_rut,
            notes=expense.notes,
            created_by_id=expense.created_by_id,
            created_by_name=creator_name,
            state=expense.state,
            created_at=expense.created_at,
            updated_at=expense.updated_at,
        )

    def _map_category(self, category: ExpenseCategory) -> ExpenseCategoryRead:
        return ExpenseCategoryRead(
            id=category.id,
            name=category.name,
            description=category.description,
            icon=category.icon,
            state=category.state,
            created_at=category.created_at,
            updated_at=category.updated_at,
        )

    # ---------- Categorías ----------
    def list_categories(self, db: Session, *, current_user: User) -> List[ExpenseCategoryRead]:
        self._ensure_finance_access(current_user)
        categories = expense_category_crud.list(db)
        return [self._map_category(cat) for cat in categories]

    def create_category(
        self, db: Session, *, current_user: User, payload: ExpenseCategoryCreate
    ) -> ExpenseCategoryRead:
        self._ensure_finance_access(current_user)

        existing = expense_category_crud.get_by_name(db, payload.name)
        if existing:
            raise HTTPException(status_code=400, detail="Ya existe una categoría con ese nombre")

        category = expense_category_crud.create(db, payload.model_dump())
        db.commit()
        return self._map_category(category)

    # ---------- Gastos ----------
    def create_expense(
        self, db: Session, *, current_user: User, payload: ExpenseCreate
    ) -> ExpenseRead:
        self._ensure_finance_access(current_user)

        # Validar categoría
        category = expense_category_crud.get(db, payload.category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Categoría no encontrada")

        expense_data = payload.model_dump()
        expense_data["created_by_id"] = current_user.id
        if not expense_data.get("expense_date"):
            expense_data["expense_date"] = datetime.utcnow()

        expense = expense_crud.create(db, expense_data)

        # Si es compra de inventario, actualizar stock
        if payload.part_id and payload.quantity:
            from app.crud.part_crud import part_crud
            from app.crud.part_movement_crud import part_movement_crud

            part = part_crud.get(db, payload.part_id)
            if part:
                # Registrar movimiento de entrada
                movement_data = {
                    "part_id": part.id,
                    "movement_type": "PURCHASE",
                    "quantity": payload.quantity,
                    "reference": f"EXPENSE-{expense.id}",
                    "notes": f"Compra: {payload.description}",
                    "created_by_id": current_user.id,
                }
                part_movement_crud.create(db, movement_data)

                # Actualizar stock
                new_stock = (part.stock_current or 0) + payload.quantity
                part_crud.update(db, part, {"stock_current": new_stock})

        db.commit()
        return self._map_expense(expense_crud.get(db, expense.id))

    def get_expense(
        self, db: Session, *, current_user: User, expense_id: int
    ) -> ExpenseRead:
        self._ensure_finance_access(current_user)

        expense = expense_crud.get(db, expense_id)
        if not expense:
            raise HTTPException(status_code=404, detail="Gasto no encontrado")

        return self._map_expense(expense)

    def list_expenses(
        self,
        db: Session,
        *,
        current_user: User,
        category_id: Optional[int] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        payment_method: Optional[str] = None,
    ) -> List[ExpenseRead]:
        self._ensure_finance_access(current_user)

        expenses = expense_crud.list(
            db,
            category_id=category_id,
            from_date=from_date,
            to_date=to_date,
            payment_method=payment_method,
        )
        return [self._map_expense(exp) for exp in expenses]

    def delete_expense(
        self, db: Session, *, current_user: User, expense_id: int
    ) -> None:
        self._ensure_finance_access(current_user)

        expense = expense_crud.get(db, expense_id)
        if not expense:
            raise HTTPException(status_code=404, detail="Gasto no encontrado")

        # Soft delete
        expense_crud.update(db, expense, {"state": 0})
        db.commit()

    # ---------- Resumen Financiero ----------
    def get_summary(
        self,
        db: Session,
        *,
        current_user: User,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        include_trends: bool = True,
        months_back: int = 6,
    ) -> FinanceSummary:
        self._ensure_finance_access(current_user)

        # Configurar fechas por defecto (último mes si no se especifica)
        if not to_date:
            to_date = datetime.utcnow()
        if not from_date:
            from_date = to_date - relativedelta(months=1)

        # Asegurar que to_date incluya todo el día
        if to_date.hour == 0 and to_date.minute == 0 and to_date.second == 0:
            to_date = to_date.replace(hour=23, minute=59, second=59)

        # ========== INGRESOS (Facturas y Pagos) ==========
        invoices = invoice_crud.list(db, from_date=from_date, to_date=to_date)

        total_invoiced = sum(float(inv.total or 0) for inv in invoices)
        total_parts_cost = sum(float(inv.parts_cost or 0) for inv in invoices)
        total_labor_cost = sum(float(inv.labor_cost or 0) for inv in invoices)

        invoices_paid = sum(1 for inv in invoices if inv.status == "PAID")
        invoices_pending = sum(1 for inv in invoices if inv.status == "PENDING")

        # Calcular pagos recibidos
        total_collected = 0.0
        for inv in invoices:
            for payment in inv.payments:
                if payment.state == 1:
                    total_collected += float(payment.amount or 0)

        total_pending = total_invoiced - total_collected

        # ========== GASTOS ==========
        total_expenses = expense_crud.sum_by_period(db, from_date=from_date, to_date=to_date)
        expenses_list = expense_crud.list(db, from_date=from_date, to_date=to_date)
        expenses_count = len(expenses_list)

        # Gastos por categoría
        expenses_by_cat_raw = expense_crud.sum_by_category(db, from_date=from_date, to_date=to_date)
        expenses_by_category = []
        for cat_data in expenses_by_cat_raw:
            percentage = (cat_data["total"] / total_expenses * 100) if total_expenses > 0 else 0
            expenses_by_category.append(
                CategoryExpenseSummary(
                    category_id=cat_data["category_id"],
                    category_name=cat_data["category_name"],
                    total=cat_data["total"],
                    count=cat_data["count"],
                    percentage=round(percentage, 2),
                )
            )

        # ========== MÁRGENES ==========
        gross_profit = total_invoiced - total_parts_cost
        net_profit = total_collected - total_expenses
        profit_margin = (net_profit / total_collected * 100) if total_collected > 0 else 0

        # ========== TENDENCIAS MENSUALES ==========
        monthly_trend = []
        if include_trends:
            monthly_trend = self._calculate_monthly_trends(db, months_back=months_back)

        # ========== TOP CLIENTES ==========
        top_clients = self._get_top_clients(db, from_date=from_date, to_date=to_date, limit=5)

        return FinanceSummary(
            from_date=from_date,
            to_date=to_date,
            total_invoiced=round(total_invoiced, 2),
            total_collected=round(total_collected, 2),
            total_pending=round(total_pending, 2),
            invoices_count=len(invoices),
            invoices_paid=invoices_paid,
            invoices_pending=invoices_pending,
            total_expenses=round(total_expenses, 2),
            expenses_count=expenses_count,
            expenses_by_category=expenses_by_category,
            gross_profit=round(gross_profit, 2),
            net_profit=round(net_profit, 2),
            profit_margin=round(profit_margin, 2),
            total_parts_cost=round(total_parts_cost, 2),
            total_labor_cost=round(total_labor_cost, 2),
            monthly_trend=monthly_trend,
            top_clients=top_clients,
        )

    def _calculate_monthly_trends(
        self, db: Session, *, months_back: int = 6
    ) -> List[PeriodMetrics]:
        """Calcula ingresos y gastos por mes para gráficos de tendencia."""
        end_date = datetime.utcnow()
        trends = []

        for i in range(months_back - 1, -1, -1):
            month_start = (end_date - relativedelta(months=i)).replace(
                day=1, hour=0, minute=0, second=0, microsecond=0
            )
            month_end = (month_start + relativedelta(months=1)) - relativedelta(seconds=1)

            # Ingresos del mes (pagos recibidos)
            income_query = (
                db.query(func.coalesce(func.sum(InvoicePayment.amount), 0))
                .filter(
                    InvoicePayment.state == 1,
                    InvoicePayment.paid_at >= month_start,
                    InvoicePayment.paid_at <= month_end,
                )
            )
            income = float(income_query.scalar() or 0)

            # Gastos del mes
            expenses = expense_crud.sum_by_period(db, from_date=month_start, to_date=month_end)

            period_str = month_start.strftime("%Y-%m")
            trends.append(
                PeriodMetrics(
                    period=period_str,
                    income=round(income, 2),
                    expenses=round(expenses, 2),
                    net=round(income - expenses, 2),
                )
            )

        return trends

    def _get_top_clients(
        self,
        db: Session,
        *,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        limit: int = 5,
    ) -> List[TopClient]:
        """Obtiene los clientes con más ingresos."""
        query = (
            db.query(
                Invoice.client_id,
                func.coalesce(func.sum(Invoice.total), 0).label("total_billed"),
                func.count(Invoice.id).label("invoices_count"),
            )
            .filter(Invoice.state == 1)
        )

        # Aplicar filtros ANTES de group_by, order_by y limit
        if from_date:
            query = query.filter(Invoice.issue_date >= from_date)
        if to_date:
            query = query.filter(Invoice.issue_date <= to_date)

        # Ahora aplicar group_by, order_by y limit
        query = (
            query
            .group_by(Invoice.client_id)
            .order_by(func.sum(Invoice.total).desc())
            .limit(limit)
        )

        results = query.all()

        top_clients = []
        for r in results:
            # Obtener nombre del cliente
            from app.crud.user_crud import user_crud
            client = user_crud.get_by_id(db, r.client_id)
            client_name = "Cliente desconocido"
            if client:
                client_name = client.full_name or client.email

            top_clients.append(
                TopClient(
                    client_id=r.client_id,
                    client_name=client_name,
                    total_billed=float(r.total_billed),
                    invoices_count=r.invoices_count,
                )
            )

        return top_clients


finance_service = FinanceService()
