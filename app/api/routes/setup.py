from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.bootstrap_service import bootstrap_service
from app.core.security_deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/setup", tags=["setup"])

@router.post("/bootstrap")
def run_bootstrap(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Seguridad: solo ADMIN puede correr esto
    role_name = current_user.role.name if current_user.role else None
    if role_name != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only ADMIN can run bootstrap",
        )

    result = bootstrap_service.bootstrap(db)
    return {
        "message": "bootstrap ok",
        "result": result
    }
