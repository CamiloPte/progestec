from typing import Sequence

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.models.part_movement import PartMovement


class PartMovementCRUD:
    def create(
        self,
        db: Session,
        *,
        part_id: int,
        movement_type: str,
        quantity: int,
        document_ref: str | None,
        movement_at,
        responsible_user_id: int | None,
        notes: str | None,
    ) -> PartMovement:
        obj = PartMovement(
            part_id=part_id,
            movement_type=movement_type,
            quantity=quantity,
            document_ref=document_ref,
            movement_at=movement_at,
            responsible_user_id=responsible_user_id,
            notes=notes,
        )
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def list_by_part(
        self, db: Session, part_id: int, *, limit: int | None = None
    ) -> Sequence[PartMovement]:
        query = (
            db.query(PartMovement)
            .filter(PartMovement.part_id == part_id)
            .order_by(desc(PartMovement.movement_at))
        )
        if limit:
            query = query.limit(limit)
        return query.all()


part_movement_crud = PartMovementCRUD()
