from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session, joinedload

from app.models.device import Device
from app.models.ticket import Ticket
from app.models.ticket_history import TicketHistory
from app.schemas.ticket import TicketCreate, TicketUpdate
from app.schemas.ticket_history import TicketHistoryCreate


class TicketCRUD:
    def get_by_id(self, db: Session, ticket_id: int) -> Optional[Ticket]:
        return (
            db.query(Ticket)
            .options(
                joinedload(Ticket.status),
                joinedload(Ticket.device).joinedload(Device.owner),
                joinedload(Ticket.issues),
                joinedload(Ticket.history).joinedload(TicketHistory.user),
                joinedload(Ticket.history).joinedload(TicketHistory.status),
                joinedload(Ticket.attachments),
            )
            .filter(Ticket.id == ticket_id, Ticket.state == 1)
            .first()
        )

    def list_all_active(self, db: Session) -> List[Ticket]:
        return (
            db.query(Ticket)
            .options(
                joinedload(Ticket.device),
                joinedload(Ticket.assignee),
                joinedload(Ticket.status),
            )
            .filter(Ticket.state == 1)
            .all()
        )

    def list_by_assignee(self, db: Session, user_id: int) -> List[Ticket]:
        return (
            db.query(Ticket)
            .join(Ticket.status)
            .filter(Ticket.state == 1, Ticket.assignee_user_id == user_id)
            .all()
        )

    def list_by_owner(self, db: Session, owner_user_id: int) -> List[Ticket]:
        return (
            db.query(Ticket)
            .join(Ticket.device)
            .options(
                joinedload(Ticket.device),
                joinedload(Ticket.assignee),
                joinedload(Ticket.status),
            )
            .filter(
                Ticket.state == 1,
                Device.owner_user_id == owner_user_id,
            )
            .all()
        )

    def create(self, db: Session, data: TicketCreate) -> Ticket:
        obj = Ticket(
            device_id=data.device_id,
            assignee_user_id=data.assignee_user_id,
            status_id=data.status_id,
            failure_desc=data.failure_desc,
            diagnosis=data.diagnosis,
            cost_estimate=data.cost_estimate,
            approved_by_owner=data.approved_by_owner,
            intake_at=data.intake_at or datetime.utcnow(),
            tracking_code=data.tracking_code,
            state=1,
        )
        db.add(obj)
        db.flush()  # tenemos obj.id antes del commit final
        return obj

    def update(self, db: Session, ticket: Ticket, data: TicketUpdate) -> Ticket:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(ticket, field, value)
        db.flush()
        return ticket

    def add_history(self, db: Session, data: TicketHistoryCreate) -> TicketHistory:
        history = TicketHistory(
            ticket_id=data.ticket_id,
            status_id=data.status_id,
            user_id=data.user_id,
            note=data.note,
            state=1,
        )
        db.add(history)
        db.flush()
        return history

    def commit(self, db: Session, obj):
        db.commit()
        db.refresh(obj)
        return obj


ticket_crud = TicketCRUD()
