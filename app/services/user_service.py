# app/services/user_service.py

from typing import List, Optional, Tuple
import secrets
import asyncio
import logging

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import (UserCreate,UserUpdate,UserReadMinimal,UserReadDetail,)
from app.crud.user_crud import user_crud
from app.crud.role_crud import role_crud
from app.core.roles import (ROLE_ADMIN,ROLE_ADVISOR,ROLE_TECHNICIAN,ROLE_CLIENT,ROLE_COURIER,get_role_name,)
from app.core.config import settings


logger = logging.getLogger(__name__)


class UserService:
    """
    Capa de lógica de negocio para usuarios.
    Se apoya en user_crud para hablar con la DB.
    """

    # ----------------- helpers de permisos -----------------
    def _ensure_admin(self, current_user: User) -> None:
        role = get_role_name(current_user)
        if role != ROLE_ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only ADMIN can perform this action",
            )

    def _ensure_admin_or_advisor(self, current_user: User) -> None:
        role = get_role_name(current_user)
        if role not in (ROLE_ADMIN, ROLE_ADVISOR):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only ADMIN or ADVISOR can perform this action",
            )

    # ----------------- mapping helpers -----------------
    def _to_minimal(self, u: User) -> UserReadMinimal:
        """
        Convierte ORM a UserReadMinimal usando model_validate y completa campos derivados.
        """
        minimal = UserReadMinimal.model_validate(u, from_attributes=True)
        minimal.role_name = u.role.name if u.role else None
        return minimal

    def _to_detail(self, u: User) -> UserReadDetail:
        """
        Usa el mismo mapeo minimal y lo expande a detalle.
        """
        base = self._to_minimal(u)
        return UserReadDetail(**base.model_dump())

    # ----------------- operaciones principales -----------------
    def list_users(
        self,
        db: Session,
        *,
        current_user: User,
        role: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[UserReadMinimal]:
        """
        Listado general de usuarios (solo ADMIN).

        - role: filtra por nombre de rol (ADMIN, TECHNICIAN, CLIENT, etc.).
        - search: busca por nombre completo o email (contiene).
        """
        self._ensure_admin(current_user)

        users: List[User] = db.query(User).filter(User.state == 1).all()

        if role:
            role_upper = role.upper()
            users = [
                u
                for u in users
                if u.role is not None and u.role.name.upper() == role_upper
            ]

        if search:
            q = search.lower().strip()
            if q:
                users = [
                    u
                    for u in users
                    if (u.full_name and q in u.full_name.lower())
                    or (u.email and q in u.email.lower())
                ]

        return [self._to_minimal(u) for u in users]

    def get_user_detail(
        self,
        db: Session,
        *,
        current_user: User,
        user_id: int,
    ) -> UserReadDetail:
        """
        Detalle de usuario (solo ADMIN por ahora).
        """
        self._ensure_admin(current_user)

        u = db.query(User).filter(User.id == user_id, User.state == 1).first()
        if not u:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        return self._to_detail(u)

    def create_user(
        self,
        db: Session,
        *,
        current_user: User,
        data: UserCreate,
    ) -> UserReadDetail:
        """
        Crear usuario (solo ADMIN).
        Se apoya en user_crud.create_user para manejar el hash de password, etc.
        """
        self._ensure_admin(current_user)

        existing = user_crud.get_by_email(db, data.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        created = user_crud.create_user(
            db,
            email=data.email,
            password=data.password,
            full_name=data.full_name,
            identification=data.identification,
            identification_type=data.identification_type,
            phone=data.phone,
            role_id=data.role_id,
        )

        return self._to_detail(created)

    def update_user(
        self,
        db: Session,
        *,
        current_user: User,
        user_id: int,
        data: UserUpdate,
    ) -> UserReadDetail:
        """
        Actualizar datos básicos de un usuario (solo ADMIN en esta fase).

        UserUpdate permite cambiar:
        - full_name
        - phone
        - identification_type
        - role_id (aunque también hay un endpoint específico para role).
        """
        self._ensure_admin(current_user)

        u: Optional[User] = db.query(User).filter(User.id == user_id).first()
        if not u or u.state != 1:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        data_dict = data.model_dump(exclude_unset=True)

        if "full_name" in data_dict:
            u.full_name = data_dict["full_name"]
        if "phone" in data_dict:
            u.phone = data_dict["phone"]
        if "identification_type" in data_dict:
            u.identification_type = data_dict["identification_type"]
        if "role_id" in data_dict and data_dict["role_id"] is not None:
            u.role_id = data_dict["role_id"]

        db.add(u)
        db.commit()
        db.refresh(u)

        return self._to_detail(u)

    def change_user_role(
        self,
        db: Session,
        *,
        current_user: User,
        user_id: int,
        role_id: int,
    ) -> UserReadDetail:
        """
        Cambiar el rol de un usuario (solo ADMIN).
        """
        self._ensure_admin(current_user)

        u: Optional[User] = db.query(User).filter(User.id == user_id).first()
        if not u or u.state != 1:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        u.role_id = role_id
        db.add(u)
        db.commit()
        db.refresh(u)

        return self._to_detail(u)

    def change_user_state(
        self,
        db: Session,
        *,
        current_user: User,
        user_id: int,
        state: int,
    ) -> UserReadDetail:
        """
        Activar / desactivar usuario (soft delete).
        - state: normalmente 1 (activo) o 0 (inactivo).
        """
        self._ensure_admin(current_user)

        u: Optional[User] = db.query(User).filter(User.id == user_id).first()
        if not u:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        if state not in (0, 1):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid state, must be 0 or 1",
            )

        u.state = state
        db.add(u)
        db.commit()
        db.refresh(u)

        return self._to_detail(u)

    # ----------------- creación rápida de cliente -----------------
    def quick_create_client(
        self,
        db: Session,
        *,
        current_user: User,
        full_name: str,
        email: str,
        identification: str,
        identification_type: Optional[str],
        phone: Optional[str],
        tracking_code: Optional[str] = None,
    ) -> Tuple[UserReadDetail, bool]:
        """
        Crea un cliente rápido con contraseña aleatoria y must_change_password=True.
        Reutiliza cliente activo si ya existe con el mismo email.
        Solo ADMIN / ADVISOR.
        
        Returns:
            Tuple[UserReadDetail, bool]: (usuario, es_nuevo)
            - es_nuevo=True si se creó un nuevo usuario
            - es_nuevo=False si ya existía
        """
        self._ensure_admin_or_advisor(current_user)

        existing = user_crud.get_by_email(db, email)
        if existing:
            if existing.state != 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Client exists but is inactive",
                )
            return self._to_detail(existing), False

        client_role = role_crud.get_by_name(db, ROLE_CLIENT)
        if not client_role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CLIENT role not found. Run bootstrap.",
            )

        # Generar contraseña temporal segura
        random_password = secrets.token_urlsafe(8)  # 8 caracteres legibles

        created = user_crud.create_user(
            db,
            email=email,
            password=random_password,
            full_name=full_name,
            identification=identification,
            identification_type=identification_type,
            phone=phone or "",
            role_id=client_role.id,
            must_change_password=True,
        )

        # Enviar email de bienvenida con credenciales
        self._send_welcome_email(
            email=email,
            client_name=full_name,
            temp_password=random_password,
            tracking_code=tracking_code,
        )

        return self._to_detail(created), True
    
    def _send_welcome_email(
        self,
        email: str,
        client_name: str,
        temp_password: str,
        tracking_code: Optional[str] = None,
    ) -> None:
        """
        Envía email de bienvenida con credenciales al nuevo cliente.
        Se ejecuta de forma asíncrona para no bloquear.
        """
        try:
            from app.services.email_service import email_service
            
            portal_url = f"{settings.FRONTEND_URL}/client"
            
            # Ejecutar en loop async
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(
                    email_service.send_welcome_email(
                        to_email=email,
                        client_name=client_name,
                        temp_password=temp_password,
                        portal_url=portal_url,
                        tracking_code=tracking_code,
                    )
                )
            finally:
                loop.close()
                
        except Exception as e:
            # Log error pero no fallar la creación del usuario
            logger.error(f"Error sending welcome email to {email}: {e}")

    # ----------------- listas especiales (combos) -----------------
    def list_technicians(
        self,
        db: Session,
        *,
        current_user: User,
    ) -> List[UserReadMinimal]:
        """
        Técnicos activos para combos (crear/editar ticket, filtros, etc.).

        Solo ADMIN / ADVISOR.
        """
        self._ensure_admin_or_advisor(current_user)

        users = db.query(User).filter(User.state == 1).all()
        technicians = [
            u
            for u in users
            if u.role is not None and u.role.name == ROLE_TECHNICIAN
        ]

        return [self._to_minimal(u) for u in technicians]

    def list_clients(
        self,
        db: Session,
        *,
        current_user: User,
    ) -> List[UserReadMinimal]:
        """
        Clientes activos para combos (crear dispositivos/tickets, etc.).

        Solo ADMIN / ADVISOR.
        """
        self._ensure_admin_or_advisor(current_user)

        users = db.query(User).filter(User.state == 1).all()
        clients = [
            u for u in users if u.role is not None and u.role.name == ROLE_CLIENT
        ]

        return [self._to_minimal(u) for u in clients]


user_service = UserService()
