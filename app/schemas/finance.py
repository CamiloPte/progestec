from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field


class PeriodMetrics(BaseModel):
    """Métricas de un período específico (mes, semana, etc.)"""
    period: str  # "2025-01", "2025-W47", etc.
    income: float
    expenses: float
    net: float


class CategoryExpenseSummary(BaseModel):
    """Resumen de gastos por categoría"""
    category_id: int
    category_name: str
    total: float
    count: int
    percentage: float


class TopClient(BaseModel):
    """Cliente con más ingresos"""
    client_id: int
    client_name: str
    total_billed: float
    invoices_count: int


class FinanceSummary(BaseModel):
    """Resumen financiero completo para el dashboard"""
    # Período de consulta
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    
    # Ingresos (pagos recibidos)
    total_invoiced: float = 0  # Total facturado
    total_collected: float = 0  # Total cobrado (pagos recibidos)
    total_pending: float = 0  # Saldo pendiente por cobrar
    
    # Contadores de facturas
    invoices_count: int = 0
    invoices_paid: int = 0
    invoices_pending: int = 0
    
    # Gastos
    total_expenses: float = 0
    expenses_count: int = 0
    expenses_by_category: List[CategoryExpenseSummary] = []
    
    # Margen/Ganancia
    gross_profit: float = 0  # Ingresos - Costo de repuestos
    net_profit: float = 0  # Ingresos cobrados - Gastos
    profit_margin: float = 0  # Porcentaje de margen
    
    # Costos de operación
    total_parts_cost: float = 0  # Costo de repuestos utilizados
    total_labor_cost: float = 0  # Mano de obra cobrada
    
    # Tendencias (últimos períodos)
    monthly_trend: List[PeriodMetrics] = []
    
    # Top clientes
    top_clients: List[TopClient] = []


class FinanceFilters(BaseModel):
    """Filtros para el resumen financiero"""
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    include_trends: bool = True
    months_back: int = Field(default=6, ge=1, le=24)
