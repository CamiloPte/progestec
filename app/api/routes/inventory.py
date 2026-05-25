from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status, Response
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security_deps import get_current_user
from app.schemas.part import (
    PartRead,
    PartDetailRead,
    PartMovementRead,
    PartMovementCreate,
    InventorySummary,
    PartCreate,
    PartUpdate,
)
from app.services.part_service import part_service


router = APIRouter(prefix="/inventory", tags=["Inventory"])


def serialize_part(part) -> PartRead:
    return PartRead(
        id=part.id,
        name=part.name,
        sku=part.sku,
        unit_price=float(part.unit_price),
        category=part.category,
        manufacturer=part.manufacturer,
        compatible_models=part.compatible_models,
        preferred_vendor=part.preferred_vendor,
        notes=part.notes,
        stock_current=part.stock_current,
        stock_min=part.stock_min,
        requires_approval=part.requires_approval,
        state=part.state,
        created_at=part.created_at,
        updated_at=part.updated_at,
        last_movement_at=getattr(part, "last_movement_at", None),
    )


@router.get("/summary", response_model=InventorySummary)
def get_inventory_summary(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return part_service.get_summary(db, user=current_user)


@router.get("/parts", response_model=List[PartRead])
def list_parts(
    search: Optional[str] = Query(None, description="Nombre o SKU"),
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None, description="in_stock | low | critical"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    parts = part_service.list_parts(
        db,
        user=current_user,
        search=search,
        category=category,
        status=status,
    )
    return parts


@router.get("/parts/{part_id}", response_model=PartDetailRead)
def get_part_detail(
    part_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    part = part_service.get_part(db, user=current_user, part_id=part_id)
    movements = part_service.list_movements(db, user=current_user, part_id=part_id, limit=10)
    movement_items: List[PartMovementRead] = []
    for movement in movements:
        movement_items.append(
            PartMovementRead(
                id=movement.id,
                movement_type=movement.movement_type,
                quantity=movement.quantity,
                document_ref=movement.document_ref,
                movement_at=movement.movement_at,
                responsible_user_id=movement.responsible_user_id,
                responsible_name=getattr(movement.responsible, "full_name", None),
                notes=movement.notes,
                state=movement.state,
                created_at=movement.created_at,
                updated_at=movement.updated_at,
            )
        )

    return PartDetailRead(
        id=part.id,
        name=part.name,
        sku=part.sku,
        unit_price=float(part.unit_price),
        category=part.category,
        manufacturer=part.manufacturer,
        compatible_models=part.compatible_models,
        preferred_vendor=part.preferred_vendor,
        notes=part.notes,
        stock_current=part.stock_current,
        stock_min=part.stock_min,
        requires_approval=part.requires_approval,
        state=part.state,
        created_at=part.created_at,
        updated_at=part.updated_at,
        last_movement_at=getattr(part, "last_movement_at", None),
        movements=movement_items,
    )


@router.get("/parts/{part_id}/movements", response_model=List[PartMovementRead])
def list_part_movements(
    part_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    movements = part_service.list_movements(db, user=current_user, part_id=part_id, limit=None)
    result: List[PartMovementRead] = []
    for movement in movements:
        result.append(
            PartMovementRead(
                id=movement.id,
                movement_type=movement.movement_type,
                quantity=movement.quantity,
                document_ref=movement.document_ref,
                movement_at=movement.movement_at,
                responsible_user_id=movement.responsible_user_id,
                responsible_name=getattr(movement.responsible, "full_name", None),
                notes=movement.notes,
                state=movement.state,
                created_at=movement.created_at,
                updated_at=movement.updated_at,
            )
        )
    return result


@router.post("/parts/{part_id}/movements", response_model=PartRead)
def create_part_movement(
    part_id: int,
    payload: PartMovementCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    part = part_service.register_movement(db, user=current_user, part_id=part_id, payload=payload)
    return serialize_part(part)


@router.post("/parts", response_model=PartRead, status_code=status.HTTP_201_CREATED)
def create_part(
    payload: PartCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    part = part_service.create_part(db, user=current_user, payload=payload)
    return serialize_part(part)


@router.put("/parts/{part_id}", response_model=PartRead)
def update_part(
    part_id: int,
    payload: PartUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    part = part_service.update_part(db, user=current_user, part_id=part_id, payload=payload)
    return serialize_part(part)


@router.delete("/parts/{part_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_part(
    part_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    part_service.delete_part(db, user=current_user, part_id=part_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
