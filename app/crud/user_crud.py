from typing import Optional
from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import get_password_hash


class UserCRUD:
    def get_by_id(self, db: Session, user_id: int) -> Optional[User]:
        return (
            db.query(User)
            .filter(User.id == user_id, User.state == 1)
            .first()
        )

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        return (
            db.query(User)
            .filter(User.email == email, User.state == 1)
            .first()
        )
    def get_all(self, db: Session) -> list[User]:
        return db.query(User).filter(User.state == 1).all()
    

    def create_user(
        self,
        db: Session,
        *,
        email: str,
        password: str,
        full_name: str,
        identification: str,
        phone: str,
        role_id: int,
        identification_type: str | None = None,
        must_change_password: bool = False,
    ) -> User:
        user = User(
            email=email,
            hashed_password=get_password_hash(password),
            full_name=full_name,
            identification=identification,
            identification_type=identification_type,
            phone=phone,
            role_id=role_id,
            must_change_password=must_change_password,
            state=1,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def update_password(
        self,
        db: Session,
        user: User,
        *,
        new_password: str,
        must_change_password: bool = False,
    ) -> User:
        user.hashed_password = get_password_hash(new_password)
        user.must_change_password = must_change_password
        db.add(user)
        db.commit()
        db.refresh(user)
        return user


user_crud = UserCRUD()
