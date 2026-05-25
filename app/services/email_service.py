# app/services/email_service.py
"""
Servicio de notificaciones por correo electrónico.
Usa fastapi-mail para enviar emails HTML con plantillas Jinja2.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from jinja2 import Environment, FileSystemLoader

from app.core.config import settings

logger = logging.getLogger(__name__)

# Configuración de templates
TEMPLATES_DIR = Path(__file__).parent.parent / "templates" / "email"

# Configuración de Jinja2
jinja_env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)), autoescape=True)


def get_mail_config() -> ConnectionConfig:
    """Obtiene la configuración de correo."""
    return ConnectionConfig(
        MAIL_USERNAME=settings.MAIL_USERNAME,
        MAIL_PASSWORD=settings.MAIL_PASSWORD,
        MAIL_FROM=settings.MAIL_FROM,
        MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
        MAIL_PORT=settings.MAIL_PORT,
        MAIL_SERVER=settings.MAIL_SERVER,
        MAIL_STARTTLS=settings.MAIL_STARTTLS,
        MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
        USE_CREDENTIALS=settings.MAIL_USE_CREDENTIALS,
        VALIDATE_CERTS=settings.MAIL_VALIDATE_CERTS,
    )


class EmailService:
    """Servicio para envío de notificaciones por email."""

    def __init__(self):
        if settings.mail_enabled:
            self.config = get_mail_config()
            self.fastmail = FastMail(self.config)
        else:
            self.config = None
            self.fastmail = None
            logger.warning("Email service disabled: MAIL_USERNAME or MAIL_PASSWORD not configured")

    def _render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """Renderiza una plantilla HTML con Jinja2."""
        # Agregar datos de la empresa al contexto
        context.update(
            {
                "company_name": settings.COMPANY_NAME,
                "company_phone": settings.COMPANY_PHONE,
                "company_email": settings.COMPANY_EMAIL,
                "company_address": settings.COMPANY_ADDRESS,
                "company_website": settings.COMPANY_WEBSITE,
                "current_year": datetime.now().year,
            }
        )

        template = jinja_env.get_template(template_name)
        return template.render(**context)

    async def send_email(
        self,
        to_email: str,
        subject: str,
        template_name: str,
        context: Dict[str, Any],
        cc: Optional[List[str]] = None,
    ) -> bool:
        """
        Envía un email usando una plantilla HTML.

        Args:
            to_email: Dirección de correo del destinatario
            subject: Asunto del correo
            template_name: Nombre del archivo de plantilla (ej: 'ticket_received.html')
            context: Diccionario con variables para la plantilla
            cc: Lista opcional de direcciones en copia

        Returns:
            True si se envió correctamente, False en caso contrario
        """
        if not settings.mail_enabled:
            logger.info(f"Email skipped (disabled): {subject} to {to_email}")
            return False

        try:
            # Renderizar plantilla HTML
            html_body = self._render_template(template_name, context)

            # Crear mensaje
            message = MessageSchema(
                subject=f"[ProGesTec] {subject}",
                recipients=[to_email],
                body=html_body,
                subtype=MessageType.html,
                cc=cc or [],
            )

            # Enviar
            await self.fastmail.send_message(message)
            logger.info(f"Email sent successfully: {subject} to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Error sending email to {to_email}: {str(e)}")
            return False

    # ==========================================
    # Métodos específicos para cada notificación
    # ==========================================

    async def send_ticket_received(
        self,
        to_email: str,
        client_name: str,
        tracking_code: str,
        device_brand: str,
        device_model: str,
        failure_desc: str,
        intake_date: str,
        portal_url: str,
    ) -> bool:
        """Notifica al cliente que su equipo fue recibido."""
        context = {
            "client_name": client_name,
            "tracking_code": tracking_code,
            "device_brand": device_brand,
            "device_model": device_model,
            "failure_desc": failure_desc,
            "intake_date": intake_date,
            "portal_url": portal_url,
        }
        return await self.send_email(
            to_email=to_email,
            subject=f"Equipo recibido - {tracking_code}",
            template_name="ticket_received.html",
            context=context,
        )

    async def send_ticket_diagnosed(
        self,
        to_email: str,
        client_name: str,
        tracking_code: str,
        device_brand: str,
        device_model: str,
        diagnosis: str,
        portal_url: str,
    ) -> bool:
        """Notifica al cliente que el diagnóstico está completo."""
        context = {
            "client_name": client_name,
            "tracking_code": tracking_code,
            "device_brand": device_brand,
            "device_model": device_model,
            "diagnosis": diagnosis,
            "portal_url": portal_url,
        }
        return await self.send_email(
            to_email=to_email,
            subject=f"Diagnóstico completado - {tracking_code}",
            template_name="ticket_diagnosed.html",
            context=context,
        )

    async def send_ticket_quote(
        self,
        to_email: str,
        client_name: str,
        tracking_code: str,
        device_brand: str,
        device_model: str,
        diagnosis: str,
        cost_estimate: float,
        portal_url: str,
        approve_url: str,
        reject_url: str,
    ) -> bool:
        """Notifica al cliente que hay una cotización pendiente de aprobación."""
        context = {
            "client_name": client_name,
            "tracking_code": tracking_code,
            "device_brand": device_brand,
            "device_model": device_model,
            "diagnosis": diagnosis,
            "cost_estimate": cost_estimate,
            "portal_url": portal_url,
            "approve_url": approve_url,
            "reject_url": reject_url,
        }
        return await self.send_email(
            to_email=to_email,
            subject=f"Cotización lista para aprobación - {tracking_code}",
            template_name="ticket_quote.html",
            context=context,
        )

    async def send_ticket_in_progress(
        self,
        to_email: str,
        client_name: str,
        tracking_code: str,
        device_brand: str,
        device_model: str,
        portal_url: str,
    ) -> bool:
        """Notifica al cliente que la reparación está en progreso."""
        context = {
            "client_name": client_name,
            "tracking_code": tracking_code,
            "device_brand": device_brand,
            "device_model": device_model,
            "portal_url": portal_url,
        }
        return await self.send_email(
            to_email=to_email,
            subject=f"Reparación en progreso - {tracking_code}",
            template_name="ticket_in_progress.html",
            context=context,
        )

    async def send_ticket_ready(
        self,
        to_email: str,
        client_name: str,
        tracking_code: str,
        device_brand: str,
        device_model: str,
        address: str,
        portal_url: str,
    ) -> bool:
        """Notifica al cliente que su equipo está listo para recoger."""
        context = {
            "client_name": client_name,
            "tracking_code": tracking_code,
            "device_brand": device_brand,
            "device_model": device_model,
            "address": address,
            "portal_url": portal_url,
        }
        return await self.send_email(
            to_email=to_email,
            subject=f"Tu equipo está listo - {tracking_code}",
            template_name="ticket_ready.html",
            context=context,
        )

    async def send_ticket_delivered(
        self,
        to_email: str,
        client_name: str,
        tracking_code: str,
        device_brand: str,
        device_model: str,
        intake_date: str,
        delivery_date: str,
        total_cost: float,
        portal_url: str,
    ) -> bool:
        """Notifica al cliente que su equipo fue entregado."""
        context = {
            "client_name": client_name,
            "tracking_code": tracking_code,
            "device_brand": device_brand,
            "device_model": device_model,
            "intake_date": intake_date,
            "delivery_date": delivery_date,
            "total_cost": total_cost,
            "portal_url": portal_url,
        }
        return await self.send_email(
            to_email=to_email,
            subject=f"Equipo entregado - {tracking_code}",
            template_name="ticket_delivered.html",
            context=context,
        )

    async def send_ticket_closed(
        self,
        to_email: str,
        client_name: str,
        tracking_code: str,
        device_brand: str,
        device_model: str,
        intake_date: str,
        close_date: str,
        final_status: str,
        total_cost: float,
        notes: Optional[str],
        portal_url: str,
    ) -> bool:
        """Notifica al cliente que su caso fue cerrado."""
        context = {
            "client_name": client_name,
            "tracking_code": tracking_code,
            "device_brand": device_brand,
            "device_model": device_model,
            "intake_date": intake_date,
            "close_date": close_date,
            "final_status": final_status,
            "total_cost": total_cost,
            "notes": notes,
            "portal_url": portal_url,
        }
        return await self.send_email(
            to_email=to_email,
            subject=f"Caso cerrado - {tracking_code}",
            template_name="ticket_closed.html",
            context=context,
        )

    async def send_quote_approved(
        self,
        to_email: str,
        client_name: str,
        tracking_code: str,
        device_brand: str,
        device_model: str,
        cost_estimate: float,
        approval_date: str,
        portal_url: str,
    ) -> bool:
        """Confirma al cliente que su cotización fue aprobada."""
        context = {
            "client_name": client_name,
            "tracking_code": tracking_code,
            "device_brand": device_brand,
            "device_model": device_model,
            "cost_estimate": cost_estimate,
            "approval_date": approval_date,
            "portal_url": portal_url,
        }
        return await self.send_email(
            to_email=to_email,
            subject=f"Cotización aprobada - {tracking_code}",
            template_name="quote_approved.html",
            context=context,
        )

    async def send_quote_rejected(
        self,
        to_email: str,
        client_name: str,
        tracking_code: str,
        device_brand: str,
        device_model: str,
        cost_estimate: float,
        rejection_date: str,
        rejection_reason: Optional[str],
        portal_url: str,
    ) -> bool:
        """Confirma al cliente que rechazó la cotización."""
        context = {
            "client_name": client_name,
            "tracking_code": tracking_code,
            "device_brand": device_brand,
            "device_model": device_model,
            "cost_estimate": cost_estimate,
            "rejection_date": rejection_date,
            "rejection_reason": rejection_reason,
            "portal_url": portal_url,
        }
        return await self.send_email(
            to_email=to_email,
            subject=f"Cotización rechazada - {tracking_code}",
            template_name="quote_rejected.html",
            context=context,
        )

    # ==========================================
    # Notificaciones de cuenta de usuario
    # ==========================================

    async def send_welcome_email(
        self,
        to_email: str,
        client_name: str,
        temp_password: str,
        portal_url: str,
        tracking_code: Optional[str] = None,
    ) -> bool:
        """
        Envía email de bienvenida con credenciales temporales al nuevo cliente.

        Args:
            to_email: Email del cliente (también es su usuario)
            client_name: Nombre completo del cliente
            temp_password: Contraseña temporal generada
            portal_url: URL del portal del cliente
            tracking_code: Código de seguimiento del ticket (opcional, si ya tiene uno)
        """
        context = {
            "client_name": client_name,
            "email": to_email,
            "temp_password": temp_password,
            "portal_url": portal_url,
            "tracking_code": tracking_code,
        }
        return await self.send_email(
            to_email=to_email,
            subject="Bienvenido - Tus credenciales de acceso",
            template_name="welcome.html",
            context=context,
        )


# Singleton del servicio de email
email_service = EmailService()
