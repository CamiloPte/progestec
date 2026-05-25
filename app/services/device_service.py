from pathlib import Path
from typing import List, Optional
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.roles import (
    DEVICE_CREATORS,
    ROLE_ADMIN,
    ROLE_ADVISOR,
    ROLE_CLIENT,
    ROLE_TECHNICIAN,
    get_role_name,
)
from app.crud.device_crud import device_crud
from app.crud.user_crud import user_crud
from app.models.device import Device
from app.models.user import User
from app.schemas.device import (
    DeviceCreate,
    DeviceOwnerInline,
    DeviceReadDetail,
    DeviceReadMinimal,
)


class DeviceService:
    #
    # CREAR DISPOSITIVO
    #
    def create_device(
        self,
        db: Session,
        *,
        current_user: User,
        data: DeviceCreate,
    ) -> DeviceReadDetail:
        """
        Reglas:
        - Solo ADMIN o ADVISOR pueden registrar equipos (recepción / mostrador).
        - owner_user_id debe existir, estar activo y ser CLIENT.
        """

        role_name = get_role_name(current_user)
        if role_name not in DEVICE_CREATORS:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not allowed to register devices",
            )

        owner = user_crud.get_by_id(db, data.owner_user_id)
        if not owner or owner.state != 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Owner not found or inactive",
            )

        if not owner.role or owner.role.name != ROLE_CLIENT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Owner must have CLIENT role",
            )

        device_obj = device_crud.create(
            db,
            owner_user_id=data.owner_user_id,
            type=data.type,
            brand=data.brand,
            model=data.model,
            serial=data.serial,
            imei=data.imei,
            intake_photo=data.intake_photo,
            notes=data.notes,
            catalog_manufacturer_id=data.catalog_manufacturer_id,
            catalog_model_id=data.catalog_model_id,
            catalog_variant_id=data.catalog_variant_id,
        )

        return self._to_detail_schema(device_obj, owner)

    #
    # CREAR DISPOSITIVO RÁPIDO (con foto opcional)
    #
    def quick_create_device(
        self,
        db: Session,
        *,
        current_user: User,
        owner_user_id: int,
        type: str,
        brand: str,
        model: str,
        serial: Optional[str] = None,
        imei: Optional[str] = None,
        notes: Optional[str] = None,
        intake_photo_file: Optional[UploadFile] = None,
        catalog_manufacturer_id: Optional[int] = None,
        catalog_model_id: Optional[int] = None,
        catalog_variant_id: Optional[int] = None,
    ) -> DeviceReadDetail:
        """
        Creación rápida de dispositivo (ADMIN/ADVISOR) con foto opcional.
        """
        role_name = get_role_name(current_user)
        if role_name not in (ROLE_ADMIN, ROLE_ADVISOR):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not allowed to quick-create devices",
            )

        owner = user_crud.get_by_id(db, owner_user_id)
        if not owner or owner.state != 1 or not owner.role or owner.role.name != ROLE_CLIENT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Owner must be an active CLIENT",
            )

        device_obj = device_crud.create(
            db,
            owner_user_id=owner_user_id,
            type=type,
            brand=brand,
            model=model,
            serial=serial,
            imei=imei,
            intake_photo=None,
            notes=notes,
            catalog_manufacturer_id=catalog_manufacturer_id,
            catalog_model_id=catalog_model_id,
            catalog_variant_id=catalog_variant_id,
        )

        if intake_photo_file:
            file_url = self._save_intake_photo(device_obj.id, intake_photo_file)
            device_obj.intake_photo = file_url
            db.add(device_obj)
            db.commit()
            db.refresh(device_obj)

        return self._to_detail_schema(device_obj, owner)

    #
    # OBTENER UN DISPOSITIVO
    #
    def get_device(
        self,
        db: Session,
        *,
        current_user: User,
        device_id: int,
    ) -> DeviceReadDetail:
        """
        Reglas de visibilidad:
        - ADMIN / ADVISOR pueden ver cualquier device.
        - CLIENT solo puede ver sus propios devices.
        - TECHNICIAN podrá ver (lo afinaremos mejor en Fase 2 con tickets asignados).
          Por ahora TECHNICIAN puede ver todo.
        - COURIER u otros roles aún no tienen acceso en Fase 1.
        """

        d = device_crud.get_active(db, device_id)
        if not d:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Device not found",
            )

        role_name = get_role_name(current_user)

        # ADMIN / ADVISOR / TECHNICIAN -> permitido ver todo el device
        if role_name in (ROLE_ADMIN, ROLE_ADVISOR, ROLE_TECHNICIAN):
            owner = user_crud.get_by_id(db, d.owner_user_id)
            return self._to_detail_schema(d, owner)

        # CLIENT -> sólo si es dueño
        if role_name == ROLE_CLIENT:
            if d.owner_user_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can't view this device",
                )
            # el owner en este caso es el propio current_user
            return self._to_detail_schema(d, current_user)

        # COURIER u otros roles desconocidos
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to view this device",
        )

    #
    # LISTAR DISPOSITIVOS (GENERAL)
    #
    def list_devices(
        self,
        db: Session,
        *,
        current_user: User,
    ) -> List[DeviceReadMinimal]:
        """
        Listado general de dispositivos:

        - ADMIN / ADVISOR / TECHNICIAN: ven todos los devices activos.
        - CLIENT: ve solo sus devices (owner_user_id = current_user.id).
        - Otros roles: 403.
        """
        role_name = get_role_name(current_user)

        query = db.query(Device).filter(Device.state == 1)

        if role_name in (ROLE_ADMIN, ROLE_ADVISOR, ROLE_TECHNICIAN):
            devices = query.all()
        elif role_name == ROLE_CLIENT:
            devices = query.filter(Device.owner_user_id == current_user.id).all()
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not allowed to list devices",
            )

        return [self._to_minimal_schema(d) for d in devices]

    #
    # LISTAR DISPOSITIVOS DEL USUARIO LOGUEADO (CLIENT)
    #
    def list_devices_for_current_user(
        self,
        db: Session,
        *,
        current_user: User,
    ) -> List[DeviceReadMinimal]:
        """
        Dispositivos del usuario logueado.

        - Pensado para endpoint /my/devices.
        - En Fase 1 tiene sentido principalmente para CLIENT:
          el cliente ve sus propios equipos registrados.
        """
        role_name = get_role_name(current_user)

        if role_name != ROLE_CLIENT:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only CLIENT can list /my/devices in this phase",
            )

        devices = (
            db.query(Device)
            .filter(Device.state == 1, Device.owner_user_id == current_user.id)
            .all()
        )

        return [self._to_minimal_schema(d) for d in devices]

    #
    # LISTAR DISPOSITIVOS POR CLIENTE (ADMIN/ADVISOR)
    #
    def list_devices_by_client(
        self,
        db: Session,
        *,
        current_user: User,
        client_id: int,
    ) -> List[DeviceReadMinimal]:
        """
        Dispositivos de un cliente específico.

        Reglas:
        - Solo ADMIN / ADVISOR.
        - client_id debe ser un usuario activo con rol CLIENT.
        """
        role_name = get_role_name(current_user)
        if role_name not in (ROLE_ADMIN, ROLE_ADVISOR):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only ADMIN or ADVISOR can list devices by client",
            )

        client = user_crud.get_by_id(db, client_id)
        if not client or client.state != 1 or not client.role or client.role.name != ROLE_CLIENT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Client not found, inactive or not a CLIENT",
            )

        devices = (
            db.query(Device).filter(Device.state == 1, Device.owner_user_id == client_id).all()
        )

        return [self._to_minimal_schema(d) for d in devices]

    #
    # Helpers para mapear ORM -> Schemas de respuesta
    #
    def _to_owner_inline(self, owner: Optional[User]) -> Optional[DeviceOwnerInline]:
        if not owner:
            return None
        return DeviceOwnerInline(
            id=owner.id,
            full_name=owner.full_name,
            phone=owner.phone,
        )

    def _to_minimal_schema(self, device_obj: Device) -> DeviceReadMinimal:
        """
        Convierte ORM -> DeviceReadMinimal con model_validate.
        """
        return DeviceReadMinimal.model_validate(device_obj, from_attributes=True)

    def _to_detail_schema(
        self,
        device_obj: Device,
        owner: Optional[User],
    ) -> DeviceReadDetail:
        """
        Convierte ORM -> DeviceReadDetail con model_validate y completa owner inline.
        """
        detail = DeviceReadDetail.model_validate(device_obj, from_attributes=True)
        detail.owner = self._to_owner_inline(owner)
        return detail

    def _save_intake_photo(self, device_id: int, file: UploadFile) -> str:
        media_root = Path(settings.MEDIA_ROOT)
        storage_dir = media_root / "devices" / str(device_id)
        storage_dir.mkdir(parents=True, exist_ok=True)

        unique_name = f"{uuid4().hex}_{file.filename}"
        destination = storage_dir / unique_name
        with destination.open("wb") as buffer:
            buffer.write(file.file.read())

        relative_path = destination.relative_to(media_root)
        return f"{settings.MEDIA_URL.rstrip('/')}/{relative_path.as_posix()}"


device_service = DeviceService()
