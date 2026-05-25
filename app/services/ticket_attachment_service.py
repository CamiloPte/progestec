from pathlib import Path
from typing import Optional
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.crud.ticket_attachment_crud import ticket_attachment_crud
from app.models.ticket import Ticket
from app.models.ticket_attachment import TicketAttachment
from app.schemas.ticket_attachment import TicketAttachmentCreate


class TicketAttachmentService:
    """Gestiona la lógica de almacenamiento local de archivos adjuntos."""

    def save_attachment(
        self,
        db: Session,
        *,
        ticket: Ticket,
        file: UploadFile,
        attachment_type: str,
        uploaded_by: Optional[int],
        note: Optional[str] = None,
        history_id: Optional[int] = None,
    ) -> TicketAttachment:
        media_root = Path(settings.MEDIA_ROOT)
        storage_dir = media_root / "tickets" / str(ticket.id)
        storage_dir.mkdir(parents=True, exist_ok=True)

        unique_name = f"{uuid4().hex}_{file.filename}"
        destination = storage_dir / unique_name

        with destination.open("wb") as buffer:
            buffer.write(file.file.read())

        relative_path = destination.relative_to(media_root)
        file_url = f"{settings.MEDIA_URL.rstrip('/')}/{relative_path.as_posix()}"

        payload = TicketAttachmentCreate(
            ticket_id=ticket.id,
            history_id=history_id,
            attachment_type=attachment_type,
            original_name=file.filename,
            stored_name=unique_name,
            file_url=file_url,
            mime_type=file.content_type,
            file_size=getattr(file, "size", None),
            note=note,
            uploaded_by=uploaded_by,
        )

        return ticket_attachment_crud.create(db, payload)

    def delete_attachment(self, db: Session, attachment: TicketAttachment) -> None:
        media_root = Path(settings.MEDIA_ROOT)
        file_path = media_root / "tickets" / str(attachment.ticket_id) / attachment.stored_name
        if file_path.exists():
            file_path.unlink()
        ticket_attachment_crud.soft_delete(db, attachment)


ticket_attachment_service = TicketAttachmentService()
