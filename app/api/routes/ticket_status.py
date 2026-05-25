from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.roles import get_role_name
from app.core.security_deps import get_current_user
from app.core.ticket_status_transitions import get_allowed_transitions
from app.crud.ticket_status_crud import ticket_status_crud
from app.db.session import get_db
from app.models.user import User
from app.schemas.ticket_status import TicketStatusRead

router = APIRouter(prefix="/ticket-statuses", tags=["ticket-statuses"])


@router.get("/", response_model=List[TicketStatusRead])
def list_ticket_statuses(
    role: Optional[str] = Query(
        default=None,
        description="Filtrar por rol (ADMIN, TECHNICIAN, CLIENT, etc.). "
        "Por defecto se usa el rol del usuario autenticado.",
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Lista estados visibles según rol para alimentar selects y filtros del frontend.
    """
    effective_role = role.upper() if role else get_role_name(current_user)
    return ticket_status_crud.list_visible_for_role(db, effective_role)


@router.get("/transitions/{current_status_code}", response_model=List[TicketStatusRead])
def list_valid_transitions(
    current_status_code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Lista los estados válidos a los que se puede transicionar desde el estado actual.
    Respeta las reglas de transición y el rol del usuario.
    """
    role = get_role_name(current_user)
    allowed_codes = get_allowed_transitions(current_status_code, role)

    # Obtener los objetos de estado para los códigos permitidos
    all_statuses = ticket_status_crud.list_active(db)
    return [s for s in all_statuses if s.code.upper() in allowed_codes]
