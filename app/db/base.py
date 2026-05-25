# app/db/base.py
# Importar todos los modelos aquí garantiza que Alembic los detecte
# para autogenerar migraciones. Los imports explícitos viven en
# app/models/__init__.py para mantener un único punto de registro.
from app.db.base_class import Base
from app.models import (
    Attribute,
    AttributeUser,
    ClaimCode,
    DeliveryOrder,
    Device,
    Expense,
    ExpenseCategory,
    Invoice,
    InvoicePayment,
    Module,
    ModuleRole,
    Part,
    PartMovement,
    Role,
    Service,
    Ticket,
    TicketAttachment,
    TicketHistory,
    TicketIssue,
    TicketPart,
    TicketService,
    TicketStatus,
    User,
)

# Re-exportar para retrocompatibilidad con código que haga `from app.db.base import Base, ...`
__all__ = [
    "Base",
    "Attribute",
    "AttributeUser",
    "ClaimCode",
    "DeliveryOrder",
    "Device",
    "Expense",
    "ExpenseCategory",
    "Invoice",
    "InvoicePayment",
    "Module",
    "ModuleRole",
    "Part",
    "PartMovement",
    "Role",
    "Service",
    "Ticket",
    "TicketAttachment",
    "TicketHistory",
    "TicketIssue",
    "TicketPart",
    "TicketService",
    "TicketStatus",
    "User",
]
