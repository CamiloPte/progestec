from typing import Optional, Sequence

from sqlalchemy.orm import Session

from app.core.ticket_status_visibility import (
    get_allowed_status_codes_for_role,
)
from app.models.ticket_status import TicketStatus


class TicketStatusCRUD:
    def get_by_id(self, db: Session, status_id: int) -> Optional[TicketStatus]:
        return (
            db.query(TicketStatus)
            .filter(TicketStatus.id == status_id, TicketStatus.state == 1)
            .first()
        )

    def get_by_code(self, db: Session, code: str) -> Optional[TicketStatus]:
        return (
            db.query(TicketStatus)
            .filter(TicketStatus.code == code, TicketStatus.state == 1)
            .first()
        )

    def create(self, db: Session, *, code: str, name: str, order: int) -> TicketStatus:
        obj = TicketStatus(
            code=code,
            name=name,
            order=order,
            state=1,
        )
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def list_active(self, db: Session) -> Sequence[TicketStatus]:
        return (
            db.query(TicketStatus)
            .filter(TicketStatus.state == 1)
            .order_by(TicketStatus.order)
            .all()
        )

    def list_visible_for_role(
        self, db: Session, role_name: Optional[str]
    ) -> Sequence[TicketStatus]:
        query = db.query(TicketStatus).filter(TicketStatus.state == 1)
        allowed_codes = get_allowed_status_codes_for_role(role_name)
        if allowed_codes is not None:
            query = query.filter(TicketStatus.code.in_(allowed_codes))
        return query.order_by(TicketStatus.order).all()


ticket_status_crud = TicketStatusCRUD()
