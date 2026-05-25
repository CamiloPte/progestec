# app/services/ticket_service.py
from typing import List, Optional
from datetime import datetime
from decimal import Decimal
import asyncio

from sqlalchemy.orm import Session
from fastapi import HTTPException, status, BackgroundTasks

from app.crud.ticket_crud import ticket_crud  # :contentReference[oaicite:1]{index=1}
from app.crud.user_crud import user_crud
from app.crud.ticket_status_crud import ticket_status_crud
from app.crud.part_crud import part_crud  # :contentReference[oaicite:2]{index=2}
from app.crud.invoice_crud import invoice_crud
from app.models.user import User
from app.models.ticket_part import TicketPart
from app.schemas.ticket import (
    TicketCreate,
    TicketUpdate,
    TicketReadMinimal,
    TicketReadDetail,
    TicketOwnerInfo,
)
from app.schemas.ticket_issue import TicketIssueRead
from app.schemas.ticket_history import TicketHistoryCreate, TicketHistoryRead
from app.schemas.ticket_attachment import TicketAttachmentRead
from app.schemas.ticket_part import TicketPartCreate, TicketPartRead
from app.schemas.part import PartMovementCreate
from app.services.ticket_attachment_service import ticket_attachment_service
from app.services.part_service import part_service
from app.core.roles import (
    ROLE_ADMIN,
    ROLE_ADVISOR,
    ROLE_TECHNICIAN,
    ROLE_CLIENT,
    ROLE_COURIER,
    TICKET_CREATORS,
    get_role_name,
)
from app.core.ticket_status_transitions import is_valid_transition


class TicketService:
    # ---------- helpers de mapeo ----------
    def _build_device_label(self, db_ticket) -> Optional[str]:
        device_label = None
        if db_ticket.device:
            pieces = []
            if db_ticket.device.brand:
                pieces.append(db_ticket.device.brand)
            if db_ticket.device.model:
                pieces.append(db_ticket.device.model)
            base_label = " ".join(pieces).strip()

            if db_ticket.failure_desc:
                short_failure = (
                    db_ticket.failure_desc[:60] + "…"
                    if len(db_ticket.failure_desc) > 60
                    else db_ticket.failure_desc
                )
                device_label = (
                    f"{base_label} – {short_failure}" if base_label else short_failure
                )
            else:
                device_label = base_label or f"Dispositivo #{db_ticket.device_id}"
        return device_label

    def _build_history_list(self, db_ticket) -> List[TicketHistoryRead]:
        history_entries = sorted(
            [h for h in db_ticket.history if h.state == 1],
            key=lambda h: h.created_at or datetime.min,
            reverse=True,
        )
        return [
            TicketHistoryRead(
                id=h.id,
                ticket_id=h.ticket_id,
                status_id=h.status_id,
                user_id=h.user_id,
                note=h.note,
                created_at=h.created_at,
                state=h.state,
                status_name=h.status.name if h.status else None,
                status_code=h.status.code if h.status else None,
                user_name=h.user.full_name if h.user else None,
            )
            for h in history_entries
        ]

    def _build_attachments_list(self, db_ticket) -> List[TicketAttachmentRead]:
        return [
            TicketAttachmentRead(
                id=a.id,
                ticket_id=a.ticket_id,
                history_id=a.history_id,
                attachment_type=a.attachment_type,
                original_name=a.original_name,
                stored_name=a.stored_name,
                file_url=a.file_url,
                mime_type=a.mime_type,
                file_size=a.file_size,
                note=a.note,
                uploaded_by=a.uploaded_by,
                created_at=a.created_at,
                updated_at=a.updated_at,
                state=a.state,
            )
            for a in db_ticket.attachments
            if a.state == 1
        ]

    def _map_ticket_detail(self, db_ticket) -> TicketReadDetail:
        detail = TicketReadDetail.model_validate(db_ticket, from_attributes=True)
        detail.device_label = self._build_device_label(db_ticket)
        detail.assignee_name = (
            db_ticket.assignee.full_name or db_ticket.assignee.email
            if db_ticket.assignee
            else None
        )
        detail.issues = [
            TicketIssueRead.model_validate(i, from_attributes=True)
            for i in db_ticket.issues
            if i.state == 1
        ]

        if db_ticket.device and db_ticket.device.owner:
            detail.owner = TicketOwnerInfo(
                id=db_ticket.device.owner.id,
                full_name=db_ticket.device.owner.full_name,
                email=db_ticket.device.owner.email,
                phone=db_ticket.device.owner.phone,
                identification_type=db_ticket.device.owner.identification_type,
                identification=db_ticket.device.owner.identification,
                address=None,
            )

        detail.history = self._build_history_list(db_ticket)
        detail.attachments = self._build_attachments_list(db_ticket)
        return detail

    def _map_ticket_minimal(self, db_ticket) -> TicketReadMinimal:
        minimal = TicketReadMinimal.model_validate(db_ticket, from_attributes=True)
        minimal.device_label = self._build_device_label(db_ticket)
        minimal.assignee_name = (
            db_ticket.assignee.full_name or db_ticket.assignee.email
            if db_ticket.assignee
            else None
        )
        minimal.status_code = db_ticket.status.code if db_ticket.status else None
        minimal.status_name = db_ticket.status.name if db_ticket.status else None
        return minimal

    # ---------- permisos para gestionar repuestos ----------
    def _ensure_ticket_parts_permissions(self, current_user: User) -> None:
        role = get_role_name(current_user)
        if role not in (ROLE_ADMIN, ROLE_ADVISOR, ROLE_TECHNICIAN):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not allowed to manage ticket parts",
            )

    # -------- list tickets --------
    def list_tickets_for_user(
        self,
        db: Session,
        current_user: User,
        status_codes: Optional[List[str]] = None,
        assigned_filter: str = "all",
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        search: Optional[str] = None,
        device_type: Optional[str] = None,
    ) -> List[TicketReadMinimal]:

        role = get_role_name(current_user)

        if role in (ROLE_ADMIN, ROLE_ADVISOR):
            tickets = ticket_crud.list_all_active(db)
        elif role == ROLE_TECHNICIAN:
            all_tickets = ticket_crud.list_all_active(db)
            tickets = [
                t
                for t in all_tickets
                if t.assignee_user_id is None or t.assignee_user_id == current_user.id
            ]
        elif role == ROLE_CLIENT:
            tickets = ticket_crud.list_by_owner(db, current_user.id)
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Role not allowed to list tickets",
            )

        if status_codes:
            codes = {c.upper() for c in status_codes}
            tickets = [
                t for t in tickets if t.status and t.status.code.upper() in codes
            ]

        if device_type:
            dt = device_type.upper()
            tickets = [
                t
                for t in tickets
                if t.device and t.device.type and t.device.type.upper() == dt
            ]

        if from_date:
            tickets = [
                t for t in tickets if t.created_at and t.created_at >= from_date
            ]
        if to_date:
            tickets = [t for t in tickets if t.created_at and t.created_at <= to_date]

        if assigned_filter == "me":
            tickets = [t for t in tickets if t.assignee_user_id == current_user.id]
        elif assigned_filter == "unassigned":
            tickets = [t for t in tickets if t.assignee_user_id is None]

        tickets.sort(key=lambda t: t.created_at or datetime.min, reverse=True)
        result: List[TicketReadMinimal] = [
            self._map_ticket_minimal(t) for t in tickets
        ]

        if search:
            q = search.lower().strip()
            if q:
                result = [
                    r
                    for r in result
                    if (
                        (r.tracking_code and q in r.tracking_code.lower())
                        or (r.device_label and q in r.device_label.lower())
                        or (r.status_name and q in r.status_name.lower())
                        or (r.assignee_name and q in r.assignee_name.lower())
                    )
                ]

        return result

    # -------- get detail --------
    def get_ticket_detail(
        self,
        db: Session,
        ticket_id: int,
        current_user: User,
    ) -> TicketReadDetail:

        db_ticket = ticket_crud.get_by_id(db, ticket_id)
        if not db_ticket or db_ticket.state != 1:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found",
            )

        role = get_role_name(current_user)

        if role in (ROLE_ADMIN, ROLE_ADVISOR):
            pass
        elif role == ROLE_TECHNICIAN:
            # Técnico puede ver: tickets asignados a él O tickets sin asignar
            is_assigned_to_me = db_ticket.assignee_user_id == current_user.id
            is_unassigned = db_ticket.assignee_user_id is None
            if not (is_assigned_to_me or is_unassigned):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Ticket not assigned to you",
                )
        elif role == ROLE_CLIENT:
            if not db_ticket.device or db_ticket.device.owner_user_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Ticket does not belong to you",
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Role not allowed",
            )
        return self._map_ticket_detail(db_ticket)

    # -------- create ticket --------
    def create_ticket(
        self,
        db: Session,
        current_user: User,
        data: TicketCreate,
    ) -> TicketReadDetail:

        role = get_role_name(current_user)
        if role not in TICKET_CREATORS:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not allowed to create tickets",
            )

        if data.assignee_user_id is not None:
            assignee = user_crud.get_by_id(db, data.assignee_user_id)
            if (
                not assignee
                or not assignee.role
                or assignee.role.name != ROLE_TECHNICIAN
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="assignee_user_id must belong to a TECHNICIAN user",
                )

        db_ticket = ticket_crud.create(db, data)

        hist = TicketHistoryCreate(
            ticket_id=db_ticket.id,
            status_id=db_ticket.status_id,
            user_id=current_user.id,
            note="Ticket created",
        )
        ticket_crud.add_history(db, hist)

        db_ticket = ticket_crud.commit(db, db_ticket)
        
        # Enviar notificación de ticket recibido
        if db_ticket.status and db_ticket.status.code:
            self._send_status_change_notification(
                db_ticket,
                "",  # No hay estado anterior
                db_ticket.status.code.upper()
            )
        
        return self.get_ticket_detail(db, db_ticket.id, current_user)

    # -------- update ticket --------
    def update_ticket(
        self,
        db: Session,
        current_user: User,
        ticket_id: int,
        data: TicketUpdate,
    ) -> TicketReadDetail:

        db_ticket = ticket_crud.get_by_id(db, ticket_id)
        if not db_ticket or db_ticket.state != 1:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found",
            )

        role = get_role_name(current_user)
        allowed = False

        # Detectar si es un intento de auto-asignación (técnico asignándose a sí mismo un ticket sin asignar)
        is_self_assign_attempt = (
            role == ROLE_TECHNICIAN
            and db_ticket.assignee_user_id is None
            and data.assignee_user_id == current_user.id
        )
        
        # Detectar si técnico intenta desasignarse
        is_self_unassign_attempt = (
            role == ROLE_TECHNICIAN
            and db_ticket.assignee_user_id == current_user.id
            and data.assignee_user_id is None
        )
        
        # Estados donde el técnico puede desasignarse
        early_status_codes = {"RECEIVED", "DIAGNOSING"}
        current_status_code = (db_ticket.status.code.upper() if db_ticket.status else "RECEIVED")

        if role == ROLE_ADMIN:
            allowed = True
        elif role == ROLE_CLIENT:
            # Cliente puede actualizar su ticket si está en WAITING_APPROVAL (aprobar/rechazar cotización)
            if db_ticket.device and db_ticket.device.owner_user_id == current_user.id:
                if current_status_code == "WAITING_APPROVAL":
                    allowed = True
        elif role == ROLE_TECHNICIAN:
            # Técnico puede actualizar si el ticket está asignado a él
            if db_ticket.assignee_user_id == current_user.id:
                # Si intenta desasignarse, solo permitir en estados tempranos
                if is_self_unassign_attempt:
                    if current_status_code in early_status_codes:
                        allowed = True
                    else:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Solo puedes quitarte la asignación en estado Recibido o En diagnóstico",
                        )
                else:
                    allowed = True
            # Técnico puede auto-asignarse un ticket sin asignar
            elif is_self_assign_attempt:
                allowed = True
        elif role == ROLE_ADVISOR:
            allowed = True

        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not allowed to update this ticket",
            )

        old_status_id = db_ticket.status_id
        new_data = data.model_dump(exclude_unset=True)
        history_note = new_data.pop("history_note", None)

        if "assignee_user_id" in new_data:
            new_assignee_id = new_data["assignee_user_id"]
            if new_assignee_id is not None:
                assignee = user_crud.get_by_id(db, new_assignee_id)
                if (
                    not assignee
                    or not assignee.role
                    or assignee.role.name != ROLE_TECHNICIAN
                ):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="assignee_user_id must belong to a TECHNICIAN user",
                    )

        status_changed = False
        new_status_obj = None
        old_status_code = db_ticket.status.code.upper() if db_ticket.status else "RECEIVED"
        
        if "status_id" in new_data:
            new_status_id = new_data["status_id"]
            if new_status_id is not None and new_status_id != old_status_id:
                new_status_obj = ticket_status_crud.get_by_id(db, new_status_id)
                if not new_status_obj:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid status_id",
                    )
                
                # Validar transición de estado
                new_status_code = (new_status_obj.code or "").upper()
                is_valid, error_msg = is_valid_transition(old_status_code, new_status_code, role)
                if not is_valid:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=error_msg,
                    )
                
                status_changed = True

        sanitized_payload = TicketUpdate(**new_data)
        db_ticket = ticket_crud.update(db, db_ticket, sanitized_payload)

        if status_changed and new_status_obj:
            status_code = (new_status_obj.code or "").upper()
            now = datetime.utcnow()
            if status_code == "READY":
                db_ticket.ready_at = now
                # Auto-generar factura borrador si no existe
                self._auto_create_draft_invoice(db, db_ticket, current_user)
            elif status_code == "DELIVERED":
                db_ticket.delivered_at = now
            elif status_code == "CLOSED":
                db_ticket.closed_at = now
            elif status_code == "CANCELLED":
                db_ticket.closed_at = now  # Usar closed_at para indicar cierre

            hist = TicketHistoryCreate(
                ticket_id=db_ticket.id,
                status_id=new_status_obj.id,
                user_id=current_user.id,
                note=history_note or f"Status changed to {new_status_obj.name}",
            )
            ticket_crud.add_history(db, hist)
            history_note = None

        db_ticket = ticket_crud.commit(db, db_ticket)

        if history_note:
            hist = TicketHistoryCreate(
                ticket_id=db_ticket.id,
                status_id=db_ticket.status_id,
                user_id=current_user.id,
                note=history_note,
            )
            ticket_crud.add_history(db, hist)
            db_ticket = ticket_crud.commit(db, db_ticket)

        # Enviar notificación por email si cambió el estado
        if status_changed and new_status_obj:
            self._send_status_change_notification(
                db_ticket,
                old_status_code,
                new_status_obj.code.upper()
            )

        return self.get_ticket_detail(db, db_ticket.id, current_user)
    
    def _send_status_change_notification(
        self,
        ticket,
        old_status_code: str,
        new_status_code: str,
    ) -> None:
        """
        Envía notificación por email cuando cambia el estado del ticket.
        Se ejecuta de forma asíncrona para no bloquear la respuesta.
        """
        try:
            from app.services.ticket_notification_service import ticket_notification_service
            ticket_notification_service.send_status_notification_sync(
                ticket,
                old_status_code,
                new_status_code
            )
        except Exception as e:
            # Log error pero no fallar la operación principal
            import logging
            logging.getLogger(__name__).error(
                f"Error sending notification for ticket {ticket.tracking_code}: {e}"
            )

    # -------- add part to ticket + inventario --------
    def add_part_to_ticket(
        self,
        db: Session,
        *,
        current_user: User,
        ticket_id: int,
        data: TicketPartCreate,
    ) -> TicketPartRead:
        """
        Agrega un repuesto a un ticket y registra el movimiento de inventario (OUT).
        """
        self._ensure_ticket_parts_permissions(current_user)

        db_ticket = ticket_crud.get_by_id(db, ticket_id)
        if not db_ticket or db_ticket.state != 1:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found",
            )

        db_part = part_crud.get(db, part_id=data.part_id)
        if not db_part or db_part.state != 1:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Part not found",
            )

        if db_part.stock_current is not None and db_part.stock_current < data.qty:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Not enough stock for this part",
            )

        unit_price_snapshot: Decimal = (
            data.unit_price_snapshot
            if data.unit_price_snapshot is not None
            else db_part.unit_price
        )

        movement_payload = PartMovementCreate(
            movement_type="OUT",
            quantity=data.qty,
            document_ref=f"TICKET-{db_ticket.id}",
            movement_at=data.movement_at or datetime.utcnow(),
            notes=data.notes or f"Uso de repuesto en ticket #{db_ticket.id}",
        )

        part_service.register_movement(
            db=db,
            user=current_user,
            part_id=db_part.id,
            payload=movement_payload,
        )

        line_total = unit_price_snapshot * data.qty

        db_ticket_part = (
            db.query(TicketPart)
            .filter(
                TicketPart.ticket_id == db_ticket.id,
                TicketPart.part_id == db_part.id,
                TicketPart.state == 1,
            )
            .one_or_none()
        )

        if db_ticket_part:
            db_ticket_part.qty += data.qty
            db_ticket_part.total_cost = db_ticket_part.total_cost + line_total
            db_ticket_part.unit_price_snapshot = unit_price_snapshot
        else:
            db_ticket_part = TicketPart(
                ticket_id=db_ticket.id,
                part_id=db_part.id,
                qty=data.qty,
                unit_price_snapshot=unit_price_snapshot,
                total_cost=line_total,
                created_by_id=current_user.id,
            )
            db.add(db_ticket_part)

        db.commit()
        db.refresh(db_ticket_part)

        result = TicketPartRead.model_validate(
            db_ticket_part,
            from_attributes=True,
        )
        result.part_name = db_part.name
        result.part_sku = db_part.sku
        return result

    # -------- list ticket parts --------
    def list_ticket_parts(
        self,
        db: Session,
        *,
        current_user: User,
        ticket_id: int,
    ) -> List[TicketPartRead]:
        """
        Lista los repuestos usados en un ticket.
        """
        self._ensure_ticket_parts_permissions(current_user)

        db_ticket = ticket_crud.get_by_id(db, ticket_id)
        if not db_ticket or db_ticket.state != 1:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found",
            )

        query = (
            db.query(TicketPart)
            .join(TicketPart.part)
            .filter(
                TicketPart.ticket_id == db_ticket.id,
                TicketPart.state == 1,
            )
            .order_by(TicketPart.created_at.asc())
        )

        items = query.all()
        result: List[TicketPartRead] = []
        for tp in items:
            read = TicketPartRead.model_validate(tp, from_attributes=True)
            if tp.part:
                read.part_name = tp.part.name
                read.part_sku = tp.part.sku
            result.append(read)
        return result

    # -------- auto-create draft invoice --------
    def _auto_create_draft_invoice(
        self,
        db: Session,
        db_ticket,
        current_user: User,
    ) -> None:
        """
        Crea automáticamente una factura borrador cuando el ticket pasa a READY.
        Solo si el ticket no tiene factura y tiene un cliente asociado.
        """
        # Verificar si ya existe factura
        existing = invoice_crud.get_by_ticket_id(db, db_ticket.id)
        if existing:
            return  # Ya tiene factura, no crear otra
        
        # Verificar que tenga cliente
        if not db_ticket.device or not db_ticket.device.owner:
            return  # Sin cliente, no se puede crear factura
        
        # Calcular costo de repuestos
        parts_cost = Decimal("0")
        parts = (
            db.query(TicketPart)
            .filter(TicketPart.ticket_id == db_ticket.id, TicketPart.state == 1)
            .all()
        )
        for tp in parts:
            parts_cost += Decimal(str(tp.total_cost or 0))
        
        # Generar número de factura
        base = db_ticket.tracking_code or f"TKT{db_ticket.id}"
        safe = "".join(ch for ch in base if ch.isalnum()).upper() or f"TKT{db_ticket.id}"
        date_part = datetime.utcnow().strftime("%Y%m%d")
        invoice_number = f"INV-{date_part}-{safe}"
        
        # Crear factura borrador (DRAFT)
        invoice_data = {
            "ticket_id": db_ticket.id,
            "client_id": db_ticket.device.owner.id,
            "invoice_number": invoice_number,
            "issue_date": datetime.utcnow(),
            "due_date": None,
            "parts_cost": parts_cost,
            "labor_cost": Decimal("0"),  # El asesor ajustará esto
            "discount_amount": Decimal("0"),
            "subtotal": parts_cost,
            "tax_percentage": Decimal("0"),
            "tax_amount": Decimal("0"),
            "total": parts_cost,
            "status": "DRAFT",  # Borrador - el asesor debe confirmar
            "created_by_id": current_user.id,
            "notes": "Factura generada automáticamente al marcar equipo como listo.",
        }
        
        invoice_crud.create(db, invoice_data)


ticket_service = TicketService()
