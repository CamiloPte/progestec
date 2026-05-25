from typing import Any, Dict, Optional, Sequence

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.part import Part


class PartCRUD:
    def list(
        self,
        db: Session,
        *,
        search: Optional[str] = None,
        category: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Sequence[Part]:
        query = db.query(Part).filter(Part.state == 1)

        if search:
            term = f"%{search.lower()}%"
            query = query.filter(func.lower(Part.name).like(term) | func.lower(Part.sku).like(term))

        if category:
            query = query.filter(func.lower(Part.category) == category.lower())

        if status:
            status = status.lower()
            if status == "in_stock":
                query = query.filter(Part.stock_current > Part.stock_min)
            elif status == "low":
                query = query.filter(Part.stock_current <= Part.stock_min, Part.stock_current > 0)
            elif status == "critical":
                query = query.filter(Part.stock_current <= 0)

        return query.order_by(Part.name.asc()).all()

    def get(self, db: Session, part_id: int) -> Optional[Part]:
        return db.query(Part).filter(Part.id == part_id, Part.state == 1).first()

    def get_by_sku(self, db: Session, sku: str) -> Optional[Part]:
        return db.query(Part).filter(Part.sku == sku, Part.state == 1).first()

    def create(
        self,
        db: Session,
        *,
        data: Dict[str, Any],
    ) -> Part:
        obj = Part(**data)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def update(self, db: Session, part: Part, *, data: Dict[str, Any]) -> Part:
        for field, value in data.items():
            setattr(part, field, value)
        db.add(part)
        db.commit()
        db.refresh(part)
        return part

    def soft_delete(self, db: Session, part: Part) -> None:
        part.state = 0
        db.add(part)
        db.commit()

    def update_stock(self, db: Session, part: Part, *, new_stock: int) -> Part:
        part.stock_current = new_stock
        db.add(part)
        db.commit()
        db.refresh(part)
        return part


part_crud = PartCRUD()
