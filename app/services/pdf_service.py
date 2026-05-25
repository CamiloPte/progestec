"""
Servicio de generación de PDFs para ProGesTec.
Genera: Facturas, Comprobantes de Recepción, Órdenes de Entrega.
"""
from __future__ import annotations

import io
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.platypus import (
   SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    HRFlowable,
)
from reportlab.graphics.shapes import Drawing, Line


# Configuración de la empresa
COMPANY_INFO = {
    "name": "ProGesTec - Servicio Técnico",
    "slogan": "Fedecafe - Barranquilla",
    "address": "Calle 34 # 46- Esquina, Barranquilla, Colombia",
    "phone": "+57 (301) 255-4106",
    "email": "servicioprogestec@gmail.com",
    "nit": "100.199.865-9",
}

# Colores corporativos
PRIMARY_COLOR = colors.HexColor("#1a472a")  # Verde oscuro (café)
SECONDARY_COLOR = colors.HexColor("#2d5016")  # Verde medio
ACCENT_COLOR = colors.HexColor("#d4af37")  # Dorado
LIGHT_BG = colors.HexColor("#f5f5f5")
WHITE = colors.white
BLACK = colors.black


class PDFService:
    """Servicio para generar PDFs profesionales."""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Configura estilos personalizados."""
        # Título principal
        self.styles.add(ParagraphStyle(
            name="TitleMain",
            parent=self.styles["Heading1"],
            fontSize=20,
            textColor=PRIMARY_COLOR,
            alignment=TA_CENTER,
            spaceAfter=12,
        ))
        
        # Subtítulo
        self.styles.add(ParagraphStyle(
            name="SubtitleCustom",
            parent=self.styles["Normal"],
            fontSize=10,
            textColor=SECONDARY_COLOR,
            alignment=TA_CENTER,
            spaceAfter=6,
        ))
        
        # Encabezado de sección
        self.styles.add(ParagraphStyle(
            name="SectionHeader",
            parent=self.styles["Heading2"],
            fontSize=12,
            textColor=PRIMARY_COLOR,
            spaceBefore=12,
            spaceAfter=6,
            borderPadding=4,
        ))
        
        # Texto normal personalizado
        self.styles.add(ParagraphStyle(
            name="BodyTextCustom",
            parent=self.styles["Normal"],
            fontSize=10,
            leading=14,
        ))
        
        # Texto pequeño (notas, pie de página)
        self.styles.add(ParagraphStyle(
            name="SmallTextCustom",
            parent=self.styles["Normal"],
            fontSize=8,
            textColor=colors.gray,
        ))
        
        # Texto de monto grande
        self.styles.add(ParagraphStyle(
            name="BigAmount",
            parent=self.styles["Normal"],
            fontSize=16,
            textColor=PRIMARY_COLOR,
            alignment=TA_RIGHT,
            fontName="Helvetica-Bold",
        ))

    def _create_header(self, doc_title: str, doc_number: str, doc_date: datetime) -> List:
        """Crea el encabezado del documento."""
        elements = []
        
        # Nombre de la empresa
        elements.append(Paragraph(COMPANY_INFO["name"], self.styles["TitleMain"]))
        elements.append(Paragraph(COMPANY_INFO["slogan"], self.styles["SubtitleCustom"]))
        elements.append(Spacer(1, 0.2 * inch))
        
        # Información de contacto y documento
        header_data = [
            [
                # Columna izquierda - Info empresa
                Paragraph(f"""
                    <b>NIT:</b> {COMPANY_INFO['nit']}<br/>
                    <b>Dirección:</b> {COMPANY_INFO['address']}<br/>
                    <b>Teléfono:</b> {COMPANY_INFO['phone']}<br/>
                    <b>Email:</b> {COMPANY_INFO['email']}
                """, self.styles["SmallTextCustom"]),
                # Columna derecha - Info documento
                Paragraph(f"""
                    <b>{doc_title}</b><br/>
                    <b>No.:</b> {doc_number}<br/>
                    <b>Fecha:</b> {doc_date.strftime('%d/%m/%Y')}<br/>
                    <b>Hora:</b> {doc_date.strftime('%H:%M')}
                """, self.styles["BodyTextCustom"]),
            ]
        ]
        
        header_table = Table(header_data, colWidths=[4 * inch, 3 * inch])
        header_table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ]))
        elements.append(header_table)
        
        # Línea separadora
        elements.append(Spacer(1, 0.15 * inch))
        elements.append(HRFlowable(
            width="100%",
            thickness=2,
            color=PRIMARY_COLOR,
            spaceBefore=0,
            spaceAfter=12,
        ))
        
        return elements

    def _create_client_section(self, client_name: str, client_email: str = None, 
                                client_phone: str = None, client_id: str = None) -> List:
        """Crea la sección de información del cliente."""
        elements = []
        elements.append(Paragraph("INFORMACIÓN DEL CLIENTE", self.styles["SectionHeader"]))
        
        client_info = f"<b>Nombre:</b> {client_name or 'N/A'}"
        if client_email:
            client_info += f"<br/><b>Email:</b> {client_email}"
        if client_phone:
            client_info += f"<br/><b>Teléfono:</b> {client_phone}"
        if client_id:
            client_info += f"<br/><b>Identificación:</b> {client_id}"
        
        elements.append(Paragraph(client_info, self.styles["BodyTextCustom"]))
        elements.append(Spacer(1, 0.15 * inch))
        
        return elements

    def _create_device_section(self, device_type: str, brand: str, model: str,
                                serial: str = None, imei: str = None) -> List:
        """Crea la sección de información del dispositivo."""
        elements = []
        elements.append(Paragraph("INFORMACIÓN DEL EQUIPO", self.styles["SectionHeader"]))
        
        device_info = f"""
            <b>Tipo:</b> {device_type}<br/>
            <b>Marca:</b> {brand}<br/>
            <b>Modelo:</b> {model}
        """
        if serial:
            device_info += f"<br/><b>Serial:</b> {serial}"
        if imei:
            device_info += f"<br/><b>IMEI:</b> {imei}"
        
        elements.append(Paragraph(device_info, self.styles["BodyTextCustom"]))
        elements.append(Spacer(1, 0.15 * inch))
        
        return elements

    def _create_parts_table(self, parts: List[dict]) -> List:
        """Crea la tabla de repuestos."""
        elements = []
        
        if not parts:
            return elements
        
        elements.append(Paragraph("REPUESTOS UTILIZADOS", self.styles["SectionHeader"]))
        
        # Encabezados
        table_data = [["Repuesto", "Cant.", "Precio Unit.", "Total"]]
        
        # Filas de datos
        for part in parts:
            table_data.append([
                part.get("name", ""),
                str(part.get("qty", 1)),
                f"${part.get('unit_price', 0):,.2f}",
                f"${part.get('total', 0):,.2f}",
            ])
        
        parts_table = Table(table_data, colWidths=[3.5 * inch, 0.7 * inch, 1.3 * inch, 1.3 * inch])
        parts_table.setStyle(TableStyle([
            # Encabezado
            ("BACKGROUND", (0, 0), (-1, 0), PRIMARY_COLOR),
            ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),
            # Cuerpo
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 1), (-1, -1), 9),
            ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
            ("ALIGN", (0, 1), (0, -1), "LEFT"),
            # Bordes
            ("GRID", (0, 0), (-1, -1), 0.5, colors.gray),
            # Alternancia de colores
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_BG]),
            # Padding
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(parts_table)
        elements.append(Spacer(1, 0.15 * inch))
        
        return elements

    def _create_totals_section(self, parts_cost: float, labor_cost: float,
                                discount: float, subtotal: float,
                                tax_percentage: float, tax_amount: float,
                                total: float) -> List:
        """Crea la sección de totales."""
        elements = []
        elements.append(Paragraph("RESUMEN DE COSTOS", self.styles["SectionHeader"]))
        
        totals_data = [
            ["Costo de Repuestos:", f"${parts_cost:,.2f}"],
            ["Mano de Obra:", f"${labor_cost:,.2f}"],
        ]
        
        if discount > 0:
            totals_data.append(["Descuento:", f"-${discount:,.2f}"])
        
        totals_data.append(["Subtotal:", f"${subtotal:,.2f}"])
        
        if tax_percentage > 0:
            totals_data.append([f"IVA ({tax_percentage}%):", f"${tax_amount:,.2f}"])
        
        totals_data.append(["TOTAL A PAGAR:", f"${total:,.2f}"])
        
        totals_table = Table(totals_data, colWidths=[5 * inch, 2 * inch])
        totals_table.setStyle(TableStyle([
            ("ALIGN", (0, 0), (0, -1), "RIGHT"),
            ("ALIGN", (1, 0), (1, -1), "RIGHT"),
            ("FONTNAME", (0, 0), (-1, -2), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -2), 10),
            # Última fila (total) en negrita y más grande
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, -1), (-1, -1), 12),
            ("TEXTCOLOR", (0, -1), (-1, -1), PRIMARY_COLOR),
            ("LINEABOVE", (0, -1), (-1, -1), 1.5, PRIMARY_COLOR),
            ("TOPPADDING", (0, -1), (-1, -1), 8),
        ]))
        
        elements.append(totals_table)
        elements.append(Spacer(1, 0.2 * inch))
        
        return elements

    def _create_footer(self, notes: str = None) -> List:
        """Crea el pie de página."""
        elements = []
        
        if notes:
            elements.append(Paragraph("NOTAS:", self.styles["SectionHeader"]))
            elements.append(Paragraph(notes, self.styles["BodyTextCustom"]))
            elements.append(Spacer(1, 0.2 * inch))
        
        # Línea separadora
        elements.append(HRFlowable(
            width="100%",
            thickness=1,
            color=colors.gray,
            spaceBefore=12,
            spaceAfter=8,
        ))
        
        # Mensaje de agradecimiento
        elements.append(Paragraph(
            "¡Gracias por confiar en nuestro servicio!",
            ParagraphStyle(
                name="Thanks",
                parent=self.styles["Normal"],
                fontSize=11,
                textColor=PRIMARY_COLOR,
                alignment=TA_CENTER,
                fontName="Helvetica-Bold",
            )
        ))
        
        elements.append(Spacer(1, 0.1 * inch))
        
        # Info legal
        elements.append(Paragraph(
            f"Documento generado el {datetime.now().strftime('%d/%m/%Y a las %H:%M')}<br/>"
            "Este documento es válido como comprobante de servicio.",
            self.styles["SmallTextCustom"]
        ))
        
        return elements

    # ========== GENERADORES DE DOCUMENTOS ==========

    def generate_invoice_pdf(self, invoice_data: dict) -> bytes:
        """
        Genera PDF de factura.
        
        invoice_data debe contener:
        - invoice_number, issue_date, due_date
        - client_name, client_email, client_phone
        - device_type, device_brand, device_model, device_serial, device_imei
        - ticket_tracking_code, ticket_failure_desc
        - parts: lista de {name, qty, unit_price, total}
        - parts_cost, labor_cost, discount_amount, subtotal, tax_percentage, tax_amount, total
        - status, notes
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.75 * inch,
            leftMargin=0.75 * inch,
            topMargin=0.5 * inch,
            bottomMargin=0.5 * inch,
        )
        
        elements = []
        
        # Encabezado
        elements.extend(self._create_header(
            "FACTURA DE SERVICIO",
            invoice_data.get("invoice_number", "N/A"),
            invoice_data.get("issue_date", datetime.now()),
        ))
        
        # Estado de la factura
        status = invoice_data.get("status", "PENDING")
        status_labels = {
            "DRAFT": "BORRADOR",
            "PENDING": "PENDIENTE DE PAGO",
            "PAID": "PAGADA",
            "CANCELLED": "CANCELADA",
        }
        status_colors = {
            "DRAFT": colors.gray,
            "PENDING": colors.orange,
            "PAID": colors.green,
            "CANCELLED": colors.red,
        }
        
        status_text = Paragraph(
            f"<b>Estado:</b> {status_labels.get(status, status)}",
            ParagraphStyle(
                name="Status",
                parent=self.styles["BodyTextCustom"],
                textColor=status_colors.get(status, colors.gray),
                alignment=TA_RIGHT,
            )
        )
        elements.append(status_text)
        elements.append(Spacer(1, 0.1 * inch))
        
        # Referencia al ticket
        tracking = invoice_data.get("ticket_tracking_code", "")
        if tracking:
            elements.append(Paragraph(
                f"<b>Ticket de Referencia:</b> {tracking}",
                self.styles["BodyTextCustom"]
            ))
            elements.append(Spacer(1, 0.1 * inch))
        
        # Cliente
        elements.extend(self._create_client_section(
            invoice_data.get("client_name"),
            invoice_data.get("client_email"),
            invoice_data.get("client_phone"),
            invoice_data.get("client_id_number"),
        ))
        
        # Dispositivo
        elements.extend(self._create_device_section(
            invoice_data.get("device_type", "N/A"),
            invoice_data.get("device_brand", "N/A"),
            invoice_data.get("device_model", "N/A"),
            invoice_data.get("device_serial"),
            invoice_data.get("device_imei"),
        ))
        
        # Descripción del servicio
        failure_desc = invoice_data.get("ticket_failure_desc")
        if failure_desc:
            elements.append(Paragraph("DESCRIPCIÓN DEL SERVICIO", self.styles["SectionHeader"]))
            elements.append(Paragraph(failure_desc, self.styles["BodyTextCustom"]))
            elements.append(Spacer(1, 0.15 * inch))
        
        # Tabla de repuestos
        parts = invoice_data.get("parts", [])
        elements.extend(self._create_parts_table(parts))
        
        # Totales
        elements.extend(self._create_totals_section(
            invoice_data.get("parts_cost", 0),
            invoice_data.get("labor_cost", 0),
            invoice_data.get("discount_amount", 0),
            invoice_data.get("subtotal", 0),
            invoice_data.get("tax_percentage", 0),
            invoice_data.get("tax_amount", 0),
            invoice_data.get("total", 0),
        ))
        
        # Información de pago si está pagada
        if status == "PAID":
            paid_at = invoice_data.get("paid_at")
            if paid_at:
                elements.append(Paragraph(
                    f"<b>Pagada el:</b> {paid_at.strftime('%d/%m/%Y')}",
                    ParagraphStyle(
                        name="Paid",
                        parent=self.styles["BodyTextCustom"],
                        textColor=colors.green,
                    )
                ))
                elements.append(Spacer(1, 0.1 * inch))
        
        # Fecha de vencimiento
        due_date = invoice_data.get("due_date")
        if due_date and status not in ("PAID", "CANCELLED"):
            elements.append(Paragraph(
                f"<b>Fecha de Vencimiento:</b> {due_date.strftime('%d/%m/%Y')}",
                self.styles["BodyTextCustom"]
            ))
            elements.append(Spacer(1, 0.1 * inch))
        
        # Footer
        elements.extend(self._create_footer(invoice_data.get("notes")))
        
        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()

    def generate_reception_pdf(self, ticket_data: dict) -> bytes:
        """
        Genera PDF de comprobante de recepción de equipo.
        
        ticket_data debe contener:
        - tracking_code, intake_at
        - client_name, client_email, client_phone
        - device_type, device_brand, device_model, device_serial, device_imei
        - failure_desc, cost_estimate
        - technician_name
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.75 * inch,
            leftMargin=0.75 * inch,
            topMargin=0.5 * inch,
            bottomMargin=0.5 * inch,
        )
        
        elements = []
        
        # Encabezado
        elements.extend(self._create_header(
            "COMPROBANTE DE RECEPCIÓN",
            ticket_data.get("tracking_code", "N/A"),
            ticket_data.get("intake_at", datetime.now()),
        ))
        
        # Cliente
        elements.extend(self._create_client_section(
            ticket_data.get("client_name"),
            ticket_data.get("client_email"),
            ticket_data.get("client_phone"),
        ))
        
        # Dispositivo
        elements.extend(self._create_device_section(
            ticket_data.get("device_type", "N/A"),
            ticket_data.get("device_brand", "N/A"),
            ticket_data.get("device_model", "N/A"),
            ticket_data.get("device_serial"),
            ticket_data.get("device_imei"),
        ))
        
        # Falla reportada
        elements.append(Paragraph("FALLA REPORTADA", self.styles["SectionHeader"]))
        elements.append(Paragraph(
            ticket_data.get("failure_desc", "No especificada"),
            self.styles["BodyTextCustom"]
        ))
        elements.append(Spacer(1, 0.15 * inch))
        
        # Presupuesto estimado (si existe)
        cost_estimate = ticket_data.get("cost_estimate")
        if cost_estimate and float(cost_estimate) > 0:
            elements.append(Paragraph("PRESUPUESTO ESTIMADO", self.styles["SectionHeader"]))
            elements.append(Paragraph(
                f"${float(cost_estimate):,.2f}",
                self.styles["BigAmount"]
            ))
            elements.append(Paragraph(
                "* Este es un estimado inicial, el costo final puede variar según el diagnóstico.",
                self.styles["SmallTextCustom"]
            ))
            elements.append(Spacer(1, 0.15 * inch))
        
        # Técnico asignado
        technician = ticket_data.get("technician_name")
        if technician:
            elements.append(Paragraph(
                f"<b>Técnico Asignado:</b> {technician}",
                self.styles["BodyTextCustom"]
            ))
            elements.append(Spacer(1, 0.1 * inch))
        
        # Código de seguimiento destacado
        elements.append(Spacer(1, 0.2 * inch))
        tracking_box = Table(
            [[Paragraph(
                f"<b>CÓDIGO DE SEGUIMIENTO</b><br/><br/>"
                f"<font size='18'>{ticket_data.get('tracking_code', 'N/A')}</font>",
                ParagraphStyle(
                    name="TrackingBox",
                    parent=self.styles["Normal"],
                    alignment=TA_CENTER,
                    textColor=PRIMARY_COLOR,
                )
            )]],
            colWidths=[4 * inch],
        )
        tracking_box.setStyle(TableStyle([
            ("BOX", (0, 0), (-1, -1), 2, PRIMARY_COLOR),
            ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BG),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 15),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 15),
        ]))
        
        # Centrar la caja
        container = Table([[tracking_box]], colWidths=[7 * inch])
        container.setStyle(TableStyle([
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ]))
        elements.append(container)
        elements.append(Spacer(1, 0.15 * inch))
        
        elements.append(Paragraph(
            "Conserve este código para consultar el estado de su equipo.",
            ParagraphStyle(
                name="TrackingNote",
                parent=self.styles["SmallTextCustom"],
                alignment=TA_CENTER,
            )
        ))
        
        # Términos y condiciones
        elements.append(Spacer(1, 0.3 * inch))
        elements.append(Paragraph("TÉRMINOS Y CONDICIONES", self.styles["SectionHeader"]))
        terms = """
        1. El cliente autoriza la revisión y diagnóstico del equipo.<br/>
        2. El tiempo de diagnóstico es de 24-48 horas hábiles.<br/>
        3. Se notificará al cliente cuando el equipo esté listo.<br/>
        4. Los equipos no reclamados en 30 días serán considerados abandonados.<br/>
        5. ProGesTec no se hace responsable por datos no respaldados.
        """
        elements.append(Paragraph(terms, self.styles["SmallTextCustom"]))
        
        # Firma
        elements.append(Spacer(1, 0.4 * inch))
        signature_table = Table(
            [
                ["____________________________", "____________________________"],
                ["Firma del Cliente", "Firma del Asesor"],
            ],
            colWidths=[3.25 * inch, 3.25 * inch],
        )
        signature_table.setStyle(TableStyle([
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 1), (-1, 1), "Helvetica"),
            ("FONTSIZE", (0, 1), (-1, 1), 9),
            ("TOPPADDING", (0, 1), (-1, 1), 5),
        ]))
        elements.append(signature_table)
        
        # Footer
        elements.extend(self._create_footer())
        
        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()

    def generate_delivery_pdf(self, ticket_data: dict) -> bytes:
        """
        Genera PDF de orden de entrega.
        
        ticket_data debe contener:
        - tracking_code, delivered_at (o ready_at)
        - client_name, client_email, client_phone
        - device_type, device_brand, device_model, device_serial, device_imei
        - failure_desc, diagnosis
        - parts: lista de repuestos usados
        - invoice_number, invoice_total, invoice_status
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.75 * inch,
            leftMargin=0.75 * inch,
            topMargin=0.5 * inch,
            bottomMargin=0.5 * inch,
        )
        
        elements = []
        
        delivery_date = ticket_data.get("delivered_at") or ticket_data.get("ready_at") or datetime.now()
        
        # Encabezado
        elements.extend(self._create_header(
            "ORDEN DE ENTREGA",
            ticket_data.get("tracking_code", "N/A"),
            delivery_date,
        ))
        
        # Cliente
        elements.extend(self._create_client_section(
            ticket_data.get("client_name"),
            ticket_data.get("client_email"),
            ticket_data.get("client_phone"),
        ))
        
        # Dispositivo
        elements.extend(self._create_device_section(
            ticket_data.get("device_type", "N/A"),
            ticket_data.get("device_brand", "N/A"),
            ticket_data.get("device_model", "N/A"),
            ticket_data.get("device_serial"),
            ticket_data.get("device_imei"),
        ))
        
        # Trabajo realizado
        elements.append(Paragraph("TRABAJO REALIZADO", self.styles["SectionHeader"]))
        
        diagnosis = ticket_data.get("diagnosis")
        failure = ticket_data.get("failure_desc", "")
        
        work_info = f"<b>Falla Reportada:</b> {failure}"
        if diagnosis:
            work_info += f"<br/><br/><b>Diagnóstico y Reparación:</b> {diagnosis}"
        
        elements.append(Paragraph(work_info, self.styles["BodyTextCustom"]))
        elements.append(Spacer(1, 0.15 * inch))
        
        # Repuestos usados
        parts = ticket_data.get("parts", [])
        if parts:
            elements.extend(self._create_parts_table(parts))
        
        # Información de factura
        invoice_number = ticket_data.get("invoice_number")
        if invoice_number:
            elements.append(Paragraph("INFORMACIÓN DE PAGO", self.styles["SectionHeader"]))
            
            invoice_status = ticket_data.get("invoice_status", "PENDING")
            status_labels = {"DRAFT": "Borrador", "PENDING": "Pendiente", "PAID": "Pagada", "CANCELLED": "Cancelada"}
            
            invoice_info = f"""
                <b>Factura No.:</b> {invoice_number}<br/>
                <b>Total:</b> ${ticket_data.get('invoice_total', 0):,.2f}<br/>
                <b>Estado:</b> {status_labels.get(invoice_status, invoice_status)}
            """
            elements.append(Paragraph(invoice_info, self.styles["BodyTextCustom"]))
            elements.append(Spacer(1, 0.15 * inch))
        
        # Garantía
        elements.append(Spacer(1, 0.2 * inch))
        warranty_box = Table(
            [[Paragraph(
                "<b>GARANTÍA DEL SERVICIO</b><br/><br/>"
                "Este servicio cuenta con garantía de 30 días a partir de la fecha de entrega.<br/>"
                "La garantía cubre únicamente el trabajo realizado y los repuestos instalados.<br/>"
                "No cubre daños por mal uso, golpes, líquidos o manipulación por terceros.",
                ParagraphStyle(
                    name="WarrantyBox",
                    parent=self.styles["SmallTextCustom"],
                    alignment=TA_LEFT,
                )
            )]],
            colWidths=[6.5 * inch],
        )
        warranty_box.setStyle(TableStyle([
            ("BOX", (0, 0), (-1, -1), 1, colors.gray),
            ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BG),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ]))
        elements.append(warranty_box)
        
        # Firma de recibido
        elements.append(Spacer(1, 0.4 * inch))
        elements.append(Paragraph(
            "CONSTANCIA DE ENTREGA",
            ParagraphStyle(
                name="DeliveryTitle",
                parent=self.styles["SectionHeader"],
                alignment=TA_CENTER,
            )
        ))
        elements.append(Paragraph(
            "Declaro que recibo el equipo en condiciones funcionales y satisfactorias.",
            ParagraphStyle(
                name="DeliveryText",
                parent=self.styles["BodyTextCustom"],
                alignment=TA_CENTER,
            )
        ))
        
        elements.append(Spacer(1, 0.3 * inch))
        signature_table = Table(
            [
                ["____________________________", "____________________________"],
                ["Firma del Cliente", "Nombre y Cédula"],
                ["", ""],
                ["____________________________", "____________________________"],
                ["Firma del Asesor", "Fecha de Entrega"],
            ],
            colWidths=[3.25 * inch, 3.25 * inch],
        )
        signature_table.setStyle(TableStyle([
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 1), (-1, 1), "Helvetica"),
            ("FONTSIZE", (0, 1), (-1, 1), 9),
            ("TOPPADDING", (0, 1), (-1, 1), 5),
            ("TOPPADDING", (0, 4), (-1, 4), 5),
        ]))
        elements.append(signature_table)
        
        # Footer
        elements.extend(self._create_footer())
        
        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()


# Instancia global
pdf_service = PDFService()
