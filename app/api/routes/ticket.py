# app/api/routes/ticket.py
import io
from datetime import datetime
from typing import List, Optional

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    Response,
    UploadFile,
    status,
)
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.roles import ROLE_ADMIN, ROLE_ADVISOR, ROLE_CLIENT, get_role_name
from app.core.security_deps import get_current_user
from app.crud.ticket_attachment_crud import ticket_attachment_crud
from app.crud.ticket_crud import ticket_crud
from app.crud.ticket_status_crud import ticket_status_crud
from app.db.session import get_db
from app.models.user import User
from app.schemas.ticket import (
    TicketCreate,
    TicketReadDetail,
    TicketReadMinimal,
    TicketUpdate,
)
from app.schemas.ticket_attachment import TicketAttachmentRead
from app.schemas.ticket_part import TicketPartCreate, TicketPartRead
from app.services.pdf_service import pdf_service
from app.services.ticket_attachment_service import ticket_attachment_service
from app.services.ticket_service import ticket_service

router = APIRouter(prefix="/tickets", tags=["tickets"])


class TicketAssignRequest(BaseModel):
    """
    Payload para asignar o desasignar un técnico.
    - assignee_user_id: id del técnico (USER con rol TECHNICIAN) o null para dejar sin asignar.
    """

    assignee_user_id: Optional[int] = None


class QuoteResponseRequest(BaseModel):
    """
    Payload para aprobar o rechazar una cotización.
    """

    approved: bool
    rejection_reason: Optional[str] = None


@router.get("/", response_model=List[TicketReadMinimal])
def list_tickets(
    status: Optional[List[str]] = Query(
        default=None,
        description="Lista de códigos de estado (RECEIVED, READY, CLOSED, etc.)",
    ),
    assigned: str = Query(
        default="all",
        regex="^(all|me|unassigned)$",
        description="Filtrar por asignación: all | me | unassigned",
    ),
    from_date: Optional[datetime] = Query(
        default=None,
        description="Fecha mínima de creación (inclusive, por created_at)",
    ),
    to_date: Optional[datetime] = Query(
        default=None,
        description="Fecha máxima de creación (inclusive, por created_at)",
    ),
    search: Optional[str] = Query(
        default=None,
        description="Texto a buscar en código, dispositivo, estado o técnico",
    ),
    device_type: Optional[str] = Query(
        default=None,
        description="Tipo de dispositivo (PHONE, LAPTOP, etc.)",
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Listado de tickets con filtros server-side.
    """
    return ticket_service.list_tickets_for_user(
        db=db,
        current_user=current_user,
        status_codes=status,
        assigned_filter=assigned,
        from_date=from_date,
        to_date=to_date,
        search=search,
        device_type=device_type,
    )


@router.get("/{ticket_id}", response_model=TicketReadDetail)
def get_ticket_detail(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ticket_service.get_ticket_detail(db, ticket_id, current_user)


@router.post("/", response_model=TicketReadDetail)
def create_ticket(
    data: TicketCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ticket_service.create_ticket(db, current_user, data)


@router.put("/{ticket_id}", response_model=TicketReadDetail)
def update_ticket(
    ticket_id: int,
    data: TicketUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ticket_service.update_ticket(db, current_user, ticket_id, data)


@router.patch("/{ticket_id}/assign", response_model=TicketReadDetail)
def assign_ticket(
    ticket_id: int,
    payload: TicketAssignRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Asigna o desasigna un técnico a un ticket.
    """
    update_data = TicketUpdate(assignee_user_id=payload.assignee_user_id)
    return ticket_service.update_ticket(db, current_user, ticket_id, update_data)


@router.patch("/{ticket_id}/quote-response", response_model=TicketReadDetail)
def respond_to_quote(
    ticket_id: int,
    payload: QuoteResponseRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Permite al cliente aprobar o rechazar una cotización.
    Solo disponible cuando el ticket está en estado WAITING_APPROVAL.
    """
    # Verificar que el usuario es cliente o admin
    role = get_role_name(current_user)

    # Obtener ticket
    db_ticket = ticket_crud.get_by_id(db, ticket_id)
    if not db_ticket or db_ticket.state != 1:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket no encontrado")

    # Verificar que el ticket pertenece al cliente (o es admin/asesor)
    if role == ROLE_CLIENT:
        if not db_ticket.device or db_ticket.device.owner_user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Este ticket no te pertenece"
            )
    elif role not in (ROLE_ADMIN, ROLE_ADVISOR):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para esta acción"
        )

    # Verificar que está en estado WAITING_APPROVAL
    current_status = db_ticket.status.code.upper() if db_ticket.status else ""
    if current_status != "WAITING_APPROVAL":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El ticket no está en estado de espera de aprobación. Estado actual: {current_status}",
        )

    # Obtener el status_id para REPAIRING o CANCELLED
    if payload.approved:
        new_status = ticket_status_crud.get_by_code(db, "REPAIRING")
        if not new_status:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Estado REPAIRING no encontrado en el sistema",
            )
        history_note = "Cotización aprobada por el cliente"
    else:
        new_status = ticket_status_crud.get_by_code(db, "CANCELLED")
        if not new_status:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Estado CANCELLED no encontrado en el sistema",
            )
        history_note = "Cotización rechazada por el cliente"
        if payload.rejection_reason:
            history_note += f": {payload.rejection_reason}"

    # Actualizar ticket (usar sistema existente para registrar historia y notificaciones)
    update_data = TicketUpdate(status_id=new_status.id, history_note=history_note)

    return ticket_service.update_ticket(db, current_user, ticket_id, update_data)


@router.post("/{ticket_id}/attachments", response_model=TicketAttachmentRead, status_code=201)
def upload_ticket_attachment(
    ticket_id: int,
    attachment_type: str = Form(..., description="diagnosis | budget | status"),
    note: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Sube un archivo asociado al ticket y lo registra en la bitácora."""

    detail = ticket_service.get_ticket_detail(db, ticket_id, current_user)
    role = current_user.role.name if current_user.role else None
    is_allowed = False
    if role in ("ADMIN", "ADVISOR"):
        is_allowed = True
    elif role == "TECHNICIAN" and detail.assignee_user_id == current_user.id:
        is_allowed = True

    if not is_allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to upload attachments for this ticket",
        )

    db_ticket = ticket_crud.get_by_id(db, ticket_id)
    if not db_ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    attachment = ticket_attachment_service.save_attachment(
        db,
        ticket=db_ticket,
        file=file,
        attachment_type=attachment_type,
        uploaded_by=current_user.id,
        note=note,
    )

    return TicketAttachmentRead(
        id=attachment.id,
        ticket_id=attachment.ticket_id,
        history_id=attachment.history_id,
        attachment_type=attachment.attachment_type,
        original_name=attachment.original_name,
        stored_name=attachment.stored_name,
        file_url=attachment.file_url,
        mime_type=attachment.mime_type,
        file_size=attachment.file_size,
        note=attachment.note,
        uploaded_by=attachment.uploaded_by,
        created_at=attachment.created_at,
        updated_at=attachment.updated_at,
        state=attachment.state,
    )


@router.delete("/{ticket_id}/attachments/{attachment_id}", status_code=204)
def delete_ticket_attachment(
    ticket_id: int,
    attachment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    detail = ticket_service.get_ticket_detail(db, ticket_id, current_user)
    role = current_user.role.name if current_user.role else None
    is_allowed = False
    if role in ("ADMIN", "ADVISOR"):
        is_allowed = True
    elif role == "TECHNICIAN" and detail.assignee_user_id == current_user.id:
        is_allowed = True

    if not is_allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to delete attachments for this ticket",
        )

    attachment = ticket_attachment_crud.get_by_id(db, attachment_id)
    if not attachment or attachment.ticket_id != ticket_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attachment not found")

    ticket_attachment_service.delete_attachment(db, attachment)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ---------- NUEVOS ENDPOINTS: REPUESTOS POR TICKET ----------


@router.post("/{ticket_id}/parts", response_model=TicketPartRead, status_code=201)
def add_ticket_part(
    ticket_id: int,
    payload: TicketPartCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Agrega un repuesto a un ticket y descuenta del inventario.
    """
    return ticket_service.add_part_to_ticket(
        db=db,
        current_user=current_user,
        ticket_id=ticket_id,
        data=payload,
    )


@router.get("/{ticket_id}/parts", response_model=List[TicketPartRead])
def list_ticket_parts(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Lista los repuestos usados en un ticket.
    """
    return ticket_service.list_ticket_parts(
        db=db,
        current_user=current_user,
        ticket_id=ticket_id,
    )


@router.delete("/{ticket_id}/parts/{ticket_part_id}", status_code=204)
def remove_ticket_part(
    ticket_id: int,
    ticket_part_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Elimina un repuesto usado en un ticket y devuelve al inventario.
    """
    ticket_service.remove_part_from_ticket(
        db=db,
        current_user=current_user,
        ticket_id=ticket_id,
        ticket_part_id=ticket_part_id,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ---------- ENDPOINTS PDF ----------


@router.get("/{ticket_id}/pdf/reception")
def download_reception_pdf(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Descarga el comprobante de recepción del ticket en PDF.
    """
    detail = ticket_service.get_ticket_detail(db, ticket_id, current_user)

    # Extraer datos del owner y device (que son objetos anidados)
    owner = detail.owner
    device = detail.device

    # Preparar datos para el PDF
    ticket_data = {
        "tracking_code": detail.tracking_code,
        "intake_at": detail.intake_at or detail.created_at,
        "client_name": owner.full_name if owner else None,
        "client_email": owner.email if owner else None,
        "client_phone": owner.phone if owner else None,
        "device_type": device.type if device else None,
        "device_brand": device.brand if device else None,
        "device_model": device.model if device else None,
        "device_serial": device.serial if device else None,
        "device_imei": device.imei if device else None,
        "failure_desc": detail.failure_desc,
        "cost_estimate": detail.cost_estimate,
        "technician_name": detail.assignee_name,
    }

    pdf_bytes = pdf_service.generate_reception_pdf(ticket_data)

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="recepcion_{detail.tracking_code}.pdf"'
        },
    )


@router.get("/{ticket_id}/pdf/delivery")
def download_delivery_pdf(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Descarga la orden de entrega del ticket en PDF.
    """
    detail = ticket_service.get_ticket_detail(db, ticket_id, current_user)

    # Extraer datos del owner y device (que son objetos anidados)
    owner = detail.owner
    device = detail.device

    # Obtener repuestos usados
    parts = ticket_service.list_ticket_parts(db, current_user=current_user, ticket_id=ticket_id)
    parts_list = [
        {
            "name": p.part_name,
            "qty": p.qty,
            "unit_price": float(p.unit_price_snapshot),
            "total": float(p.total_cost),
        }
        for p in parts
    ]

    # Datos de factura si existe
    invoice_number = None
    invoice_total = 0
    invoice_status = None
    # Verificar si hay factura asociada al ticket
    ticket = ticket_crud.get_by_id(db, ticket_id)
    if ticket and ticket.invoice:
        invoice_number = ticket.invoice.invoice_number
        invoice_total = float(ticket.invoice.total or 0)
        invoice_status = ticket.invoice.status

    ticket_data = {
        "tracking_code": detail.tracking_code,
        "delivered_at": detail.delivered_at,
        "ready_at": detail.ready_at,
        "client_name": owner.full_name if owner else None,
        "client_email": owner.email if owner else None,
        "client_phone": owner.phone if owner else None,
        "device_type": device.type if device else None,
        "device_brand": device.brand if device else None,
        "device_model": device.model if device else None,
        "device_serial": device.serial if device else None,
        "device_imei": device.imei if device else None,
        "failure_desc": detail.failure_desc,
        "diagnosis": detail.diagnosis,
        "parts": parts_list,
        "invoice_number": invoice_number,
        "invoice_total": invoice_total,
        "invoice_status": invoice_status,
    }

    pdf_bytes = pdf_service.generate_delivery_pdf(ticket_data)

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="entrega_{detail.tracking_code}.pdf"'
        },
    )
