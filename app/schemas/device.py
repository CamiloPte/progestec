# app/schemas/device.py
from typing import Optional

from app.schemas.common import BaseSchema, TimestampSchema


class DeviceBase(BaseSchema):
    owner_user_id: int
    type: str  # PHONE | LAPTOP | TABLET | OTHER
    brand: str
    model: str
    serial: Optional[str] = None
    imei: Optional[str] = None
    intake_photo: Optional[str] = None
    notes: Optional[str] = None

    # IDs del catálogo externo (opcional)
    catalog_manufacturer_id: Optional[int] = None
    catalog_model_id: Optional[int] = None
    catalog_variant_id: Optional[int] = None


class DeviceCreate(DeviceBase):
    pass


class DeviceUpdate(BaseSchema):
    type: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    serial: Optional[str] = None
    imei: Optional[str] = None
    intake_photo: Optional[str] = None
    notes: Optional[str] = None
    owner_user_id: Optional[int] = None
    state: Optional[int] = None

    catalog_manufacturer_id: Optional[int] = None
    catalog_model_id: Optional[int] = None
    catalog_variant_id: Optional[int] = None


class DeviceReadMinimal(TimestampSchema):
    id: int
    owner_user_id: int
    type: str
    brand: str
    model: str
    serial: Optional[str] = None
    imei: Optional[str] = None
    state: int

    catalog_manufacturer_id: Optional[int] = None
    catalog_model_id: Optional[int] = None
    catalog_variant_id: Optional[int] = None


class DeviceOwnerInline(BaseSchema):
    """
    Pequeño resumen del dueño del dispositivo
    para usar en detalles.
    """

    id: int
    full_name: str | None = None
    phone: str | None = None


class DeviceReadDetail(DeviceReadMinimal):
    owner: Optional[DeviceOwnerInline] = None
    notes: Optional[str] = None
    intake_photo: Optional[str] = None
