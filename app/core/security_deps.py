# app/core/security_deps.py

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.jwt_utils import decode_access_token
from app.core.security import OAUTH2_SCHEME
from app.db.session import get_db
from app.models.user import User


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(OAUTH2_SCHEME),
) -> User:
    """
    - Read JWT from Authorization header.
    - Decode.
    - Fetch user from DB.
    - Validate active.
    - Return SQLAlchemy User object.
    """

    payload = decode_access_token(token)
    email = payload.get("sub")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing subject",
        )

    db_user = db.query(User).filter(User.email == email, User.state == 1).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive or not found",
        )

    return db_user
