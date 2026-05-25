from typing import Optional
from app.schemas.common import BaseSchema, TimestampSchema


class ModuleRoleBase(BaseSchema):
    role_id: int
    module_id: int
    description: Optional[str] = None


class ModuleRoleCreate(ModuleRoleBase):
    pass


class ModuleRoleUpdate(BaseSchema):
    description: Optional[str] = None
    state: Optional[int] = None


class ModuleRoleRead(TimestampSchema):
    id: int
    role_id: int
    module_id: int
    description: Optional[str]
    state: int
