# app/services/ticket_notification_service.py
"""
Servicio de notificaciones para tickets.
Maneja el envío de emails según los cambios de estado de los tickets.
"""

import logging
from datetime import datetime
from typing import Optional, TYPE_CHECKING
import asyncio

from app.core.config import settings
from app.services.email_service import email_service

if TYPE_CHECKING:
    from app.models.ticket import Ticket

logger = logging.getLogger(__name__)


class TicketNotificationService:
    """Servicio para enviar notificaciones relacionadas con tickets."""
    
    def _get_portal_url(self, tracking_code: str) -> str:
        """Genera la URL del portal del cliente para un ticket."""
        base = settings.FRONTEND_URL.rstrip("/")
        return f"{base}/client/tickets/{tracking_code}"
    
    def _get_client_info(self, ticket) -> tuple[Optional[str], Optional[str]]:
        """
        Obtiene el email y nombre del cliente asociado al ticket.
        Returns: (email, nombre)
        """
        if ticket.device and ticket.device.owner:
            owner = ticket.device.owner
            return owner.email, owner.full_name or owner.email.split("@")[0]
        return None, None
    
    def _get_device_info(self, ticket) -> tuple[str, str]:
        """Obtiene marca y modelo del dispositivo."""
        if ticket.device:
            brand = ticket.device.brand or "Sin marca"
            model = ticket.device.model or "Sin modelo"
            return brand, model
        return "Dispositivo", "Desconocido"
    
    def _format_date(self, dt: Optional[datetime]) -> str:
        """Formatea una fecha para mostrar en emails."""
        if not dt:
            return datetime.utcnow().strftime("%d/%m/%Y %H:%M")
        return dt.strftime("%d/%m/%Y %H:%M")
    
    async def send_status_notification(
        self,
        ticket,
        old_status_code: str,
        new_status_code: str,
    ) -> bool:
        """
        Envía la notificación apropiada según el cambio de estado.
        
        Args:
            ticket: El objeto Ticket con la información actualizada
            old_status_code: Código del estado anterior
            new_status_code: Código del nuevo estado
        
        Returns:
            True si se envió correctamente, False en caso contrario
        """
        if not settings.mail_enabled:
            logger.info(f"Email notifications disabled, skipping for ticket {ticket.tracking_code}")
            return False
        
        email, client_name = self._get_client_info(ticket)
        if not email:
            logger.warning(f"No client email found for ticket {ticket.tracking_code}")
            return False
        
        brand, model = self._get_device_info(ticket)
        portal_url = self._get_portal_url(ticket.tracking_code)
        tracking_code = ticket.tracking_code
        
        new_status = new_status_code.upper()
        
        try:
            if new_status == "RECEIVED":
                return await email_service.send_ticket_received(
                    to_email=email,
                    client_name=client_name,
                    tracking_code=tracking_code,
                    device_brand=brand,
                    device_model=model,
                    failure_desc=ticket.failure_desc or "No especificada",
                    intake_date=self._format_date(ticket.created_at),
                    portal_url=portal_url
                )
            
            elif new_status == "DIAGNOSING":
                # No enviamos email al iniciar diagnóstico, 
                # pero sí cuando termina (WAITING_APPROVAL)
                return True
            
            elif new_status == "WAITING_APPROVAL":
                return await email_service.send_ticket_quote(
                    to_email=email,
                    client_name=client_name,
                    tracking_code=tracking_code,
                    device_brand=brand,
                    device_model=model,
                    diagnosis=ticket.diagnosis or ticket.failure_desc or "Diagnóstico completado",
                    cost_estimate=float(ticket.cost_estimate or 0),
                    portal_url=portal_url,
                    approve_url=f"{portal_url}?action=approve",
                    reject_url=f"{portal_url}?action=reject"
                )
            
            elif new_status == "REPAIRING":
                # Si venimos de WAITING_APPROVAL, significa que se aprobó
                if old_status_code.upper() == "WAITING_APPROVAL":
                    return await email_service.send_quote_approved(
                        to_email=email,
                        client_name=client_name,
                        tracking_code=tracking_code,
                        device_brand=brand,
                        device_model=model,
                        cost_estimate=float(ticket.cost_estimate or 0),
                        approval_date=self._format_date(datetime.utcnow()),
                        portal_url=portal_url
                    )
                else:
                    # Reparación directa sin cotización
                    return await email_service.send_ticket_in_progress(
                        to_email=email,
                        client_name=client_name,
                        tracking_code=tracking_code,
                        device_brand=brand,
                        device_model=model,
                        portal_url=portal_url
                    )
            
            elif new_status == "READY":
                return await email_service.send_ticket_ready(
                    to_email=email,
                    client_name=client_name,
                    tracking_code=tracking_code,
                    device_brand=brand,
                    device_model=model,
                    address=settings.COMPANY_ADDRESS,
                    portal_url=portal_url
                )
            
            elif new_status == "DELIVERED":
                return await email_service.send_ticket_delivered(
                    to_email=email,
                    client_name=client_name,
                    tracking_code=tracking_code,
                    device_brand=brand,
                    device_model=model,
                    intake_date=self._format_date(ticket.created_at),
                    delivery_date=self._format_date(ticket.delivered_at or datetime.utcnow()),
                    total_cost=float(ticket.total_cost or ticket.cost_estimate or 0),
                    portal_url=portal_url
                )
            
            elif new_status == "CLOSED":
                # Determinar estado final
                final_status = "Completado"
                if old_status_code.upper() == "DELIVERED":
                    final_status = "Entregado y cerrado"
                
                return await email_service.send_ticket_closed(
                    to_email=email,
                    client_name=client_name,
                    tracking_code=tracking_code,
                    device_brand=brand,
                    device_model=model,
                    intake_date=self._format_date(ticket.created_at),
                    close_date=self._format_date(ticket.closed_at or datetime.utcnow()),
                    final_status=final_status,
                    total_cost=float(ticket.total_cost or ticket.cost_estimate or 0),
                    notes=None,  # Se podría agregar notas de cierre
                    portal_url=portal_url
                )
            
            elif new_status == "CANCELLED":
                # Notificar cancelación como rechazo si venía de cotización
                if old_status_code.upper() == "WAITING_APPROVAL":
                    return await email_service.send_quote_rejected(
                        to_email=email,
                        client_name=client_name,
                        tracking_code=tracking_code,
                        device_brand=brand,
                        device_model=model,
                        cost_estimate=float(ticket.cost_estimate or 0),
                        rejection_date=self._format_date(datetime.utcnow()),
                        rejection_reason="Servicio cancelado",
                        portal_url=portal_url
                    )
                else:
                    # Para otros casos de cancelación, enviar email de cierre
                    return await email_service.send_ticket_closed(
                        to_email=email,
                        client_name=client_name,
                        tracking_code=tracking_code,
                        device_brand=brand,
                        device_model=model,
                        intake_date=self._format_date(ticket.created_at),
                        close_date=self._format_date(datetime.utcnow()),
                        final_status="Cancelado",
                        total_cost=0,
                        notes="El servicio fue cancelado.",
                        portal_url=portal_url
                    )
            
            else:
                logger.info(f"No notification template for status: {new_status}")
                return True
                
        except Exception as e:
            logger.error(f"Error sending notification for ticket {tracking_code}: {str(e)}")
            return False
    
    async def send_quote_response_notification(
        self,
        ticket,
        approved: bool,
        rejection_reason: Optional[str] = None,
    ) -> bool:
        """
        Envía confirmación cuando el cliente aprueba o rechaza una cotización.
        Este método se llama desde el endpoint de respuesta del cliente.
        """
        email, client_name = self._get_client_info(ticket)
        if not email:
            return False
        
        brand, model = self._get_device_info(ticket)
        portal_url = self._get_portal_url(ticket.tracking_code)
        
        if approved:
            return await email_service.send_quote_approved(
                to_email=email,
                client_name=client_name,
                tracking_code=ticket.tracking_code,
                device_brand=brand,
                device_model=model,
                cost_estimate=float(ticket.cost_estimate or 0),
                approval_date=self._format_date(datetime.utcnow()),
                portal_url=portal_url
            )
        else:
            return await email_service.send_quote_rejected(
                to_email=email,
                client_name=client_name,
                tracking_code=ticket.tracking_code,
                device_brand=brand,
                device_model=model,
                cost_estimate=float(ticket.cost_estimate or 0),
                rejection_date=self._format_date(datetime.utcnow()),
                rejection_reason=rejection_reason,
                portal_url=portal_url
            )
    
    def send_status_notification_sync(
        self,
        ticket,
        old_status_code: str,
        new_status_code: str,
    ) -> bool:
        """
        Versión síncrona del envío de notificaciones.
        Usa asyncio.run() o un event loop existente.
        """
        try:
            # Intentar usar el loop existente
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Si hay un loop corriendo, crear una tarea
                asyncio.create_task(
                    self.send_status_notification(ticket, old_status_code, new_status_code)
                )
                return True
            else:
                # Si no hay loop, ejecutar directamente
                return loop.run_until_complete(
                    self.send_status_notification(ticket, old_status_code, new_status_code)
                )
        except RuntimeError:
            # No hay event loop, crear uno nuevo
            return asyncio.run(
                self.send_status_notification(ticket, old_status_code, new_status_code)
            )


# Singleton del servicio
ticket_notification_service = TicketNotificationService()
