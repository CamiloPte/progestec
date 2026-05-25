from typing import Optional, Sequence

from sqlalchemy.orm import Session

from app.models.device import Device


class DeviceCRUD:
    def create(
        self,
        db: Session,
        *,
        owner_user_id: int,
        type: str,
        brand: str,
        model: str,
        serial: Optional[str],
        imei: Optional[str],
        intake_photo: Optional[str],
        notes: Optional[str],
        catalog_manufacturer_id: Optional[int] = None,
        catalog_model_id: Optional[int] = None,
        catalog_variant_id: Optional[int] = None,
    ) -> Device:
        obj = Device(
            owner_user_id=owner_user_id,
            type=type,
            brand=brand,
            model=model,
            serial=serial,
            imei=imei,
            intake_photo=intake_photo,
            notes=notes,
            catalog_manufacturer_id=catalog_manufacturer_id,
            catalog_model_id=catalog_model_id,
            catalog_variant_id=catalog_variant_id,
            state=1,  # activo por defecto
        )
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def get_active(self, db: Session, device_id: int) -> Optional[Device]:
        return db.query(Device).filter(Device.id == device_id, Device.state == 1).first()

    def list_by_owner(self, db: Session, owner_user_id: int) -> Sequence[Device]:
        return (
            db.query(Device).filter(Device.owner_user_id == owner_user_id, Device.state == 1).all()
        )


device_crud = DeviceCRUD()
