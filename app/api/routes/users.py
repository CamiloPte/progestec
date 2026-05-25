# app/api/routes/users.py

from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.security_deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import (
    QuickClientCreate,
    UserCreate,
    UserReadDetail,
    UserReadMinimal,
    UserUpdate,
)
from app.services.user_service import user_service

router = APIRouter(prefix="/users", tags=["users"])


class ChangeRoleRequest(BaseModel):
    role_id: int


class ChangeStateRequest(BaseModel):
    state: int  # 0 / 1


@router.get("/technicians", response_model=List[UserReadMinimal])
def list_technicians(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Técnicos activos para combos (crear/editar ticket, filtros, etc.).
    Solo ADMIN / ADVISOR.
    """
    return user_service.list_technicians(db, current_user=current_user)


@router.get("/clients", response_model=List[UserReadMinimal])
def list_clients(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Clientes activos para combos (crear dispositivos/tickets, etc.).
    Solo ADMIN / ADVISOR.
    """
    return user_service.list_clients(db, current_user=current_user)


@router.get("/", response_model=List[UserReadMinimal])
def list_users(
    role: Optional[str] = Query(
        default=None,
        description="Filtrar por nombre de rol (ADMIN, TECHNICIAN, CLIENT, etc.)",
    ),
    search: Optional[str] = Query(
        default=None,
        description="Buscar por nombre completo o email (contiene)",
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Listado general de usuarios (solo ADMIN por ahora).
    Ideal para la vista de 'Gestión de Usuarios'.
    """
    return user_service.list_users(
        db,
        current_user=current_user,
        role=role,
        search=search,
    )


@router.get("/{user_id}", response_model=UserReadDetail)
def get_user_detail(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Detalle de usuario (solo ADMIN).
    """
    return user_service.get_user_detail(
        db,
        current_user=current_user,
        user_id=user_id,
    )


@router.post("/", response_model=UserReadDetail, status_code=201)
def create_user(
    data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Crear usuario (solo ADMIN).
    Equivalente “correcto” a lo que hacíamos con /auth/register para pruebas.
    """
    return user_service.create_user(
        db,
        current_user=current_user,
        data=data,
    )


@router.put("/{user_id}", response_model=UserReadDetail)
def update_user(
    user_id: int,
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Actualizar datos básicos de un usuario (solo ADMIN).
    """
    return user_service.update_user(
        db,
        current_user=current_user,
        user_id=user_id,
        data=data,
    )


@router.patch("/{user_id}/role", response_model=UserReadDetail)
def change_user_role(
    user_id: int,
    payload: ChangeRoleRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Cambiar rol de un usuario (solo ADMIN).
    Útil para la UI de Gestión de Usuarios (columna 'Rol').
    """
    return user_service.change_user_role(
        db,
        current_user=current_user,
        user_id=user_id,
        role_id=payload.role_id,
    )


@router.patch("/{user_id}/state", response_model=UserReadDetail)
def change_user_state(
    user_id: int,
    payload: ChangeStateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Activar / desactivar usuario (soft delete). Solo ADMIN.

    - state = 1 -> activo
    - state = 0 -> inactivo
    """
    return user_service.change_user_state(
        db,
        current_user=current_user,
        user_id=user_id,
        state=payload.state,
    )


@router.post("/clients/quick", response_model=UserReadDetail, status_code=201)
def quick_create_client(
    data: QuickClientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Creación rápida de un CLIENT (password aleatoria + must_change_password=True).
    Reutiliza cliente activo si ya existe.
    Si es un cliente nuevo, se le envía email con sus credenciales.
    Solo ADMIN / ADVISOR.
    """
    user_detail, is_new = user_service.quick_create_client(
        db,
        current_user=current_user,
        full_name=data.full_name,
        email=data.email,
        identification=data.identification,
        identification_type=data.identification_type,
        phone=data.phone,
    )
    return user_detail
