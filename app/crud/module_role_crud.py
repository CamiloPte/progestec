from typing import Optional, Sequence
from sqlalchemy.orm import Session

from app.models.module_role import ModuleRole
from app.models.module import Module


class ModuleRoleCRUD:
    def list_modules_by_role(self, db: Session, role_id: int) -> Sequence[ModuleRole]:
        return (
            db.query(ModuleRole)
            .join(Module, Module.id == ModuleRole.module_id)
            .filter(
                ModuleRole.role_id == role_id,
                ModuleRole.state == 1,
                Module.state == 1,
            )
            .order_by(Module.name)
            .all()
        )

    def get_by_role_and_module(
        self, db: Session, role_id: int, module_id: int
    ) -> Optional[ModuleRole]:
        return (
            db.query(ModuleRole)
            .filter(
                ModuleRole.role_id == role_id,
                ModuleRole.module_id == module_id,
            )
            .first()
        )

    def create(
        self,
        db: Session,
        *,
        role_id: int,
        module_id: int,
        description: str | None = None,
    ) -> ModuleRole:
        obj = ModuleRole(
            role_id=role_id,
            module_id=module_id,
            description=description,
            state=1,
        )
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj


module_role_crud = ModuleRoleCRUD()
