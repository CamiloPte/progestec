from typing import Sequence, Optional
from sqlalchemy.orm import Session

from app.models.ticket_attachment import TicketAttachment
from app.schemas.ticket_attachment import TicketAttachmentCreate

class TicketAttachmentCRUD:
    def list_for_ticket(self, db: Session, ticket_id: int) -> Sequence[TicketAttachment]:
        return (
            db.query(TicketAttachment)
            .filter(TicketAttachment.ticket_id == ticket_id, TicketAttachment.state == 1)
            .order_by(TicketAttachment.created_at.desc())
            .all()
        )

    def create(self, db: Session, data: TicketAttachmentCreate) -> TicketAttachment:
        obj = TicketAttachment(**data.model_dump())
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def get_by_id(self, db: Session, attachment_id: int) -> Optional[TicketAttachment]:
        return (
            db.query(TicketAttachment)
            .filter(TicketAttachment.id == attachment_id)
            .first()
        )

    def soft_delete(self, db: Session, attachment: TicketAttachment) -> None:
        attachment.state = 0
        db.commit()


ticket_attachment_crud = TicketAttachmentCRUD()
