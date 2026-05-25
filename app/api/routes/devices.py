# app/api/routes/device.py
from typing import List

from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security_deps import get_current_user
from app.models.user import User
from app.schemas.device import (
    DeviceCreate,
    DeviceReadDetail,
    DeviceReadMinimal,
)
from app.services.device_service import device_service

router = APIRouter(tags=["devices"])


@router.post("/devices", response_model=DeviceReadDetail)
def create_device(
    data: DeviceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Crear dispositivo para un cliente (solo ADMIN/ADVISOR).
    """
    return device_service.create_device(
        db,
        current_user=current_user,
        data=data,
    )


@router.get("/devices", response_model=List[DeviceReadMinimal])
def list_devices(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Listado general de dispositivos:

    - ADMIN / ADVISOR / TECHNICIAN: todos los devices activos.
    - CLIENT: solo sus devices.
    """
    return device_service.list_devices(
        db,
        current_user=current_user,
    )


@router.get("/devices/{device_id}", response_model=DeviceReadDetail)
def get_device(
    device_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Detalle de un dispositivo, con validación por rol.
    """
    return device_service.get_device(
        db,
        current_user=current_user,
        device_id=device_id,
    )


@router.get("/my/devices", response_model=List[DeviceReadMinimal])
def list_my_devices(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Dispositivos del usuario logueado (pensado para CLIENT).

    - Solo CLIENT puede usar este endpoint en esta fase.
    """
    return device_service.list_devices_for_current_user(
        db,
        current_user=current_user,
    )


@router.get("/clients/{client_id}/devices", response_model=List[DeviceReadMinimal])
def list_devices_by_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Dispositivos de un cliente específico.

    - Solo ADMIN / ADVISOR.
    """
    return device_service.list_devices_by_client(
        db,
        current_user=current_user,
        client_id=client_id,
    )


@router.post("/devices/quick", response_model=DeviceReadDetail, status_code=201)
async def quick_create_device(
    owner_user_id: int = Form(...),
    type: str = Form(...),
    brand: str = Form(...),
    model: str = Form(...),
    serial: str | None = Form(None),
    imei: str | None = Form(None),
    notes: str | None = Form(None),
    intake_photo: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Creación rápida de dispositivo (ADMIN/ADVISOR) con foto opcional.
    """
    return device_service.quick_create_device(
        db,
        current_user=current_user,
        owner_user_id=owner_user_id,
        type=type,
        brand=brand,
        model=model,
        serial=serial,
        imei=imei,
        notes=notes,
        intake_photo_file=intake_photo,
    )
