import io
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.security_deps import get_current_user
from app.crud.invoice_crud import invoice_crud
from app.db.session import get_db
from app.schemas.invoice import InvoiceCreateFromTicket, InvoiceRead, InvoiceUpdate
from app.schemas.invoice_payment import (
    InvoicePaymentCreate,
    InvoicePaymentCreateFromInvoice,
    InvoicePaymentRead,
)
from app.services.invoice_service import invoice_service
from app.services.pdf_service import pdf_service

router = APIRouter(prefix="/invoices", tags=["Invoices"])


@router.post(
    "/from-ticket/{ticket_id}",
    response_model=InvoiceRead,
    status_code=status.HTTP_201_CREATED,
)
def create_invoice_from_ticket(
    ticket_id: int,
    payload: InvoiceCreateFromTicket,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return invoice_service.generate_invoice_for_ticket(
        db,
        current_user=current_user,
        ticket_id=ticket_id,
        payload=payload,
    )


@router.get("/{invoice_id}", response_model=InvoiceRead)
def get_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return invoice_service.get_invoice(db, current_user=current_user, invoice_id=invoice_id)


@router.patch("/{invoice_id}", response_model=InvoiceRead)
def update_invoice(
    invoice_id: int,
    payload: InvoiceUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Actualiza una factura en estado DRAFT.
    Permite agregar mano de obra, descuentos, impuestos.
    Si confirm=True, cambia el estado a PENDING.
    """
    return invoice_service.update_invoice(
        db, current_user=current_user, invoice_id=invoice_id, payload=payload
    )


@router.get("", response_model=List[InvoiceRead])
def list_invoices(
    status_list: Optional[List[str]] = Query(None, alias="status"),
    client_id: Optional[int] = Query(None),
    from_date: Optional[datetime] = Query(None),
    to_date: Optional[datetime] = Query(None),
    with_debt: Optional[bool] = Query(
        None, description="Si es true devuelve solo facturas con saldo pendiente"
    ),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return invoice_service.list_invoices(
        db,
        current_user=current_user,
        status_list=status_list,
        client_id=client_id,
        from_date=from_date,
        to_date=to_date,
        with_debt=with_debt,
    )


@router.post(
    "/{invoice_id}/payments",
    response_model=InvoiceRead,
    status_code=status.HTTP_201_CREATED,
)
def register_payment(
    invoice_id: int,
    payload: InvoicePaymentCreateFromInvoice,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    full_payload = InvoicePaymentCreate(
        invoice_id=invoice_id,
        amount=payload.amount,
        payment_method=payload.payment_method,
        reference=payload.reference,
        paid_at=payload.paid_at,
    )
    return invoice_service.register_payment(db, current_user=current_user, payload=full_payload)


@router.get("/{invoice_id}/payments", response_model=List[InvoicePaymentRead])
def list_payments(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return invoice_service.list_payments_for_invoice(
        db, current_user=current_user, invoice_id=invoice_id
    )


@router.get("/{invoice_id}/pdf")
def download_invoice_pdf(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Descarga la factura en formato PDF.
    """
    # Obtener la factura con todos sus datos
    invoice = invoice_crud.get(db, invoice_id)
    if not invoice or invoice.state != 1:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Factura no encontrada")

    # Verificar permisos usando el service
    invoice_data_read = invoice_service.get_invoice(
        db, current_user=current_user, invoice_id=invoice_id
    )

    # Obtener datos del ticket y dispositivo
    ticket = invoice.ticket
    device = ticket.device if ticket else None
    owner = device.owner if device else None

    # Obtener repuestos usados
    parts_list = []
    if ticket and ticket.ticket_parts:
        for tp in ticket.ticket_parts:
            if tp.state == 1 and tp.part:
                parts_list.append(
                    {
                        "name": tp.part.name,
                        "qty": tp.qty,
                        "unit_price": float(tp.unit_price_snapshot),
                        "total": float(tp.total_cost),
                    }
                )

    # Preparar datos completos para el PDF
    invoice_data = {
        "invoice_number": invoice.invoice_number,
        "issue_date": invoice.issue_date,
        "due_date": invoice.due_date,
        "status": invoice.status,
        "paid_at": invoice.paid_at,
        # Cliente
        "client_name": owner.full_name if owner else invoice_data_read.client_name,
        "client_email": owner.email if owner else None,
        "client_phone": owner.phone if owner else None,
        "client_id_number": owner.id_number if owner and hasattr(owner, "id_number") else None,
        # Ticket
        "ticket_tracking_code": ticket.tracking_code if ticket else None,
        "ticket_failure_desc": ticket.failure_desc if ticket else None,
        # Dispositivo
        "device_type": device.type if device else None,
        "device_brand": device.brand if device else None,
        "device_model": device.model if device else None,
        "device_serial": device.serial if device else None,
        "device_imei": device.imei if device else None,
        # Repuestos
        "parts": parts_list,
        # Montos
        "parts_cost": float(invoice.parts_cost or 0),
        "labor_cost": float(invoice.labor_cost or 0),
        "discount_amount": float(invoice.discount_amount or 0),
        "subtotal": float(invoice.subtotal or 0),
        "tax_percentage": float(invoice.tax_percentage or 0),
        "tax_amount": float(invoice.tax_amount or 0),
        "total": float(invoice.total or 0),
        # Notas
        "notes": invoice.notes,
    }

    pdf_bytes = pdf_service.generate_invoice_pdf(invoice_data)

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="factura_{invoice.invoice_number}.pdf"'
        },
    )
