from typing import Optional

from app.schemas.common import BaseSchema, TimestampSchema


class RoleBase(BaseSchema):
    name: str
    description: Optional[str] = None


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseSchema):
    name: Optional[str] = None
    description: Optional[str] = None
    state: Optional[int] = None


class RoleReadMinimal(TimestampSchema):
    id: int
    name: str
    state: int


class RoleReadDetail(RoleReadMinimal):
    description: Optional[str] = None
