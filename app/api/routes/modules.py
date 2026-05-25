from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.roles import ROLE_ADMIN
from app.core.security_deps import get_current_user
from app.crud.module_crud import module_crud
from app.db.session import get_db
from app.models.user import User
from app.schemas.module import ModuleReadDetail
from app.services.module_access_service import module_access_service

router = APIRouter(prefix="/modules", tags=["modules"])


@router.get("/", response_model=List[ModuleReadDetail])
def list_modules(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role is None or current_user.role.name != ROLE_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only ADMIN can list all modules",
        )
    modules = module_crud.list_active(db)
    return [
        ModuleReadDetail(
            id=m.id,
            name=m.name,
            description=m.description,
            state=m.state,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )
        for m in modules
    ]


@router.get("/me", response_model=List[str])
def list_my_modules(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return module_access_service.list_modules_for_user(db, current_user)
