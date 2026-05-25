# app/api/routes/dashboard.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security_deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.dashboard import ClientDashboardSummary, DashboardSummary
from app.services.dashboard_service import dashboard_service

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Resumen de tickets para el dashboard.

    - ADMIN / ADVISOR: resumen global.
    - TECHNICIAN: resumen de sus tickets asignados.
    """
    return dashboard_service.get_summary(db, current_user=current_user)


@router.get("/client", response_model=ClientDashboardSummary)
def get_client_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Dashboard personalizado para clientes.

    Incluye:
    - Notificaciones importantes (equipos listos, presupuestos pendientes)
    - Tickets activos con progreso visual
    - Dispositivos registrados
    - Facturas pendientes de pago
    """
    return dashboard_service.get_client_summary(db, current_user=current_user)
