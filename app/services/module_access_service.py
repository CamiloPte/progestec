from typing import List

from sqlalchemy.orm import Session

from app.crud.module_role_crud import module_role_crud
from app.models.user import User


class ModuleAccessService:
    def list_modules_for_user(self, db: Session, user: User) -> List[str]:
        if not user.role_id:
            return []
        module_roles = module_role_crud.list_modules_by_role(db, user.role_id)
        modules = []
        for module_role in module_roles:
            if module_role.module and module_role.module.name:
                modules.append(module_role.module.name)
        return modules


module_access_service = ModuleAccessService()
