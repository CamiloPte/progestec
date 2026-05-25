from typing import Optional, Sequence
from sqlalchemy.orm import Session

from app.models.module import Module


class ModuleCRUD:
    def get_by_name(self, db: Session, name: str) -> Optional[Module]:
        return (
            db.query(Module)
            .filter(Module.name == name, Module.state == 1)
            .first()
        )

    def create(self, db: Session, *, name: str, description: str | None = None) -> Module:
        obj = Module(name=name, description=description, state=1)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def list_active(self, db: Session) -> Sequence[Module]:
        return (
            db.query(Module)
            .filter(Module.state == 1)
            .order_by(Module.name)
            .all()
        )


module_crud = ModuleCRUD()
