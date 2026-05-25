from typing import Optional
from pydantic import BaseModel
from app.schemas.common import BaseSchema, TimestampSchema


class ModuleBase(BaseSchema):
    name: str
    description: Optional[str] = None


class ModuleCreate(ModuleBase):
    pass


class ModuleUpdate(BaseSchema):
    name: Optional[str] = None
    description: Optional[str] = None
    state: Optional[int] = None


class ModuleReadMinimal(TimestampSchema):
    id: int
    name: str
    state: int


class ModuleReadDetail(ModuleReadMinimal):
    description: Optional[str]
