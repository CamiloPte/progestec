from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.roles import ROLE_ADMIN, get_role_name
from app.core.security import create_access_token, verify_password
from app.core.security_deps import get_current_user
from app.crud.user_crud import user_crud
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    SetPasswordRequest,
    Token,
    UserCreatedResponse,
)
from app.schemas.common import MessageResponse
from app.schemas.user import UserReadMinimal
from app.services.module_access_service import module_access_service

router = APIRouter(prefix="/auth", tags=["auth"])


# 1. Registro manual para pruebas
@router.post("/register", response_model=UserCreatedResponse)
def register_user(
    data: RegisterRequest,
    db: Session = Depends(get_db),
):
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
        phone=data.phone or "",
        role_id=data.role_id,
        identification_type=None,
    )

    return UserCreatedResponse(
        id=created.id,
        full_name=created.full_name,
        email=created.email,
        role_id=created.role_id,
        state=created.state,
        created_at=created.created_at,
        updated_at=created.updated_at,
    )


# 2. Login JSON para front/mobile
@router.post("/login", response_model=Token)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    """
    Login pensado para front web / mobile.
    Body esperado (JSON):
    {
        "email": "admin@example.com",
        "password": "123456"
    }

    Retorna el token y must_change_password para forzar cambio de contraseña
    en clientes nuevos.
    """
    db_user = user_crud.get_by_email(db, data.email)
    if not db_user or db_user.state != 1:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    if not verify_password(data.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    token = create_access_token(
        {
            "sub": db_user.email,
            "role": db_user.role.name if db_user.role else None,
        }
    )

    return Token(
        access_token=token,
        token_type="bearer",
        must_change_password=db_user.must_change_password,
    )


# 3. Login estilo OAuth2PasswordBearer para Swagger (/auth/token)
@router.post("/token", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Login pensado para Swagger / OAuth2PasswordBearer.
    Recibe form-data con:
    username=<email>
    password=<password>
    """
    # OJO: OAuth2PasswordRequestForm usa "username", no "email"
    db_user = user_crud.get_by_email(db, form_data.username)
    if not db_user or db_user.state != 1:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    if not verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    token = create_access_token(
        {
            "sub": db_user.email,
            "role": db_user.role.name if db_user.role else None,
        }
    )

    return Token(
        access_token=token,
        token_type="bearer",
        must_change_password=db_user.must_change_password,
    )


# 4. /auth/me protegido por el token
@router.get("/me", response_model=UserReadMinimal)
def me(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    modules = module_access_service.list_modules_for_user(db, current_user)
    return UserReadMinimal(
        id=current_user.id,
        full_name=current_user.full_name,
        email=current_user.email,
        phone=current_user.phone,
        identification=current_user.identification,
        identification_type=current_user.identification_type,
        role_id=current_user.role_id,
        role_name=current_user.role.name if current_user.role else None,
        state=current_user.state,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
        modules=modules,
        must_change_password=current_user.must_change_password,
    )


# 5. list all users (for testing) -> SOLO ADMIN
@router.get("/users", response_model=list[UserReadMinimal])
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if get_role_name(current_user) != ROLE_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only ADMIN can list all users",
        )

    users = user_crud.get_all(db)
    return [
        UserReadMinimal(
            id=user.id,
            full_name=user.full_name,
            email=user.email,
            phone=user.phone,
            identification=user.identification,
            identification_type=user.identification_type,
            role_id=user.role_id,
            role_name=user.role.name if user.role else None,
            state=user.state,
            created_at=user.created_at,
            updated_at=user.updated_at,
            must_change_password=user.must_change_password,
        )
        for user in users
    ]


@router.post("/set-password", response_model=MessageResponse)
def set_password(
    data: SetPasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Permite que el usuario autenticado cambie su contraseña y apaga must_change_password.
    Pensado para el flujo de clientes invitados.
    """
    if not data.new_password or len(data.new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must have at least 6 characters",
        )

    user_crud.update_password(
        db,
        current_user,
        new_password=data.new_password,
        must_change_password=False,
    )

    return MessageResponse(message="Password updated successfully")
