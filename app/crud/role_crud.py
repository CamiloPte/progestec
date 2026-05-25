from typing import Optional, Sequence
from sqlalchemy.orm import Session
from app.models.role import Role

class RoleCRUD:
    def get_by_name(self, db: Session, name: str) -> Optional[Role]:
        return (
            db.query(Role)
            .filter(Role.name == name, Role.state == 1)
            .first()
        )

    def create(self, db: Session, *, name: str, description: str = "") -> Role:
        obj = Role(
            name=name,
            description=description,
            state=1,
        )
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def list_active(self, db: Session) -> Sequence[Role]:
        return db.query(Role).filter(Role.state == 1).all()

role_crud = RoleCRUD()
