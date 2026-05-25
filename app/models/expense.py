from sqlalchemy import Column, Integer, Numeric, String, ForeignKey, DateTime, Text, text
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.mixins import TimestampStateMixin, PKMixin


class ExpenseCategory(Base, PKMixin, TimestampStateMixin):
    """Categorías de gastos: Compras de inventario, Servicios, Nómina, etc."""
    __tablename__ = "expense_categories"

    name = Column(String(100), nullable=False, unique=True)
    description = Column(String(255))
    icon = Column(String(50))  # Icono para UI (opcional)

    expenses = relationship("Expense", back_populates="category")


class Expense(Base, PKMixin, TimestampStateMixin):
    """Registro de gastos operativos del negocio."""
    __tablename__ = "expenses"

    category_id = Column(
        Integer,
        ForeignKey("expense_categories.id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    description = Column(String(255), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    payment_method = Column(String(30), nullable=False)  # CASH, CARD, TRANSFER, OTHER
    reference = Column(String(100))  # Número de factura o recibo del proveedor
    expense_date = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    
    # Vinculación opcional con compras de inventario
    part_id = Column(
        Integer,
        ForeignKey("parts.id", onupdate="CASCADE", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    quantity = Column(Integer)  # Si es compra de inventario
    
    # Vinculación opcional con proveedor (para futuro)
    supplier_name = Column(String(150))
    supplier_rut = Column(String(20))  # RUT/NIT del proveedor
    
    notes = Column(Text)
    
    created_by_id = Column(
        Integer,
        ForeignKey("users.id", onupdate="CASCADE", ondelete="SET NULL"),
        nullable=True,
    )

    # Relaciones
    category = relationship("ExpenseCategory", back_populates="expenses")
    part = relationship("Part", back_populates="expenses")
    creator = relationship("User", foreign_keys=[created_by_id])
