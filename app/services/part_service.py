from datetime import date, datetime
from typing import Optional, Sequence

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.roles import ROLE_ADMIN, ROLE_ADVISOR, ROLE_TECHNICIAN, user_has_role
from app.crud.part_crud import part_crud
from app.crud.part_movement_crud import part_movement_crud
from app.models.part import Part
from app.models.part_movement import PartMovement
from app.models.user import User
from app.schemas.part import (
    InventorySummary,
    PartCreate,
    PartMovementCreate,
    PartUpdate,
)

# Roles permitidos para acceder/usar inventario (ver partes, registrar movimientos, etc.)
ALLOWED_ROLES_INVENTORY = (ROLE_ADMIN, ROLE_ADVISOR, ROLE_TECHNICIAN)

# Códigos de categoría para SKU
CATEGORY_CODES = {
    "PANTALLAS": "SCR",
    "PANTALLA": "SCR",
    "BATERIAS": "BAT",
    "BATERIA": "BAT",
    "CAMARAS": "CAM",
    "CAMARA": "CAM",
}


def generate_sku(part: Part) -> str:
    """Genera un SKU legible basado en categoría, fabricante, modelos y el id del repuesto."""

    # 1) código por categoría
    cat = (part.category or "").upper()
    cat_code = CATEGORY_CODES.get(cat, "PRT")

    # 2) fabricante (3 letras)
    manu_raw = (part.manufacturer or "GEN").upper().replace(" ", "")
    manu_code = manu_raw[:3] or "GEN"

    # 3) modelos compatibles (limpiamos texto, 5 chars)
    model_raw = (part.compatible_models or "GEN").upper()
    model_clean = "".join(ch for ch in model_raw if ch.isalnum())
    model_code = model_clean[:5] or "GEN"

    # 4) secuencia basada en id
    seq = f"{part.id:05d}"

    return f"{cat_code}-{manu_code}-{model_code}-{seq}"


class PartService:
    # ==========================
    # Helpers de permisos
    # ==========================
    def _ensure_can_use_inventory(self, user: User) -> None:
        """Permite ADMIN, ADVISOR y TECHNICIAN acceder al inventario."""
        if not user_has_role(user, *ALLOWED_ROLES_INVENTORY):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No autorizado para inventario",
            )

    def _ensure_admin_or_advisor(self, user: User) -> None:
        """Solo ADMIN / ADVISOR pueden gestionar catálogo de repuestos."""
        if not user_has_role(user, ROLE_ADMIN, ROLE_ADVISOR):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo un administrador o asesor puede gestionar el inventario",
            )

    # ==========================
    # Listado / lectura
    # ==========================
    def list_parts(
        self,
        db: Session,
        *,
        user: User,
        search: Optional[str] = None,
        category: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Sequence[Part]:
        self._ensure_can_use_inventory(user)

        parts = part_crud.list(db, search=search, category=category, status=status)
        if not parts:
            return []

        part_ids = [p.id for p in parts]
        movement_rows = (
            db.query(PartMovement.part_id, func.max(PartMovement.movement_at))
            .filter(PartMovement.part_id.in_(part_ids))
            .group_by(PartMovement.part_id)
            .all()
        )
        movement_map = {row[0]: row[1] for row in movement_rows}
        for part in parts:
            part.last_movement_at = movement_map.get(part.id)

        return parts

    def get_part(self, db: Session, *, user: User, part_id: int) -> Part:
        self._ensure_can_use_inventory(user)

        part = part_crud.get(db, part_id)
        if not part:
            raise HTTPException(status_code=404, detail="Repuesto no encontrado")
        return part

    def list_movements(
        self,
        db: Session,
        *,
        user: User,
        part_id: int,
        limit: Optional[int] = None,
    ):
        self._ensure_can_use_inventory(user)

        part = self.get_part(db, user=user, part_id=part_id)
        return part_movement_crud.list_by_part(db, part.id, limit=limit)

    def get_summary(self, db: Session, *, user: User) -> InventorySummary:
        self._ensure_can_use_inventory(user)

        total_stock = db.query(func.coalesce(func.sum(Part.stock_current), 0)).scalar() or 0
        alerts = (
            db.query(func.count(Part.id))
            .filter(Part.state == 1, Part.stock_current <= Part.stock_min)
            .scalar()
            or 0
        )
        critical = (
            db.query(func.count(Part.id)).filter(Part.state == 1, Part.stock_current <= 0).scalar()
            or 0
        )
        today = date.today()
        movements_today = (
            db.query(func.count(PartMovement.id))
            .filter(func.date(PartMovement.movement_at) == today)
            .scalar()
            or 0
        )

        categories = (
            db.query(Part.category, func.coalesce(func.sum(Part.stock_current), 0))
            .filter(Part.state == 1)
            .group_by(Part.category)
            .all()
        )
        category_counts = {cat or "Sin categoría": int(total) for cat, total in categories}

        return InventorySummary(
            total_stock=int(total_stock),
            low_stock_alerts=int(alerts),
            movements_today=int(movements_today),
            critical_parts=int(critical),
            stock_by_category=category_counts,
        )

    # ==========================
    # Movimientos de stock
    # ==========================
    def register_movement(
        self,
        db: Session,
        *,
        user: User,
        part_id: int,
        payload: PartMovementCreate,
    ):
        self._ensure_can_use_inventory(user)

        part = self.get_part(db, user=user, part_id=part_id)

        movement_type = payload.movement_type.upper()
        if movement_type not in ("IN", "OUT"):
            raise HTTPException(status_code=400, detail="movement_type inválido")

        quantity = payload.quantity
        if quantity <= 0:
            raise HTTPException(status_code=400, detail="La cantidad debe ser mayor que 0")

        # Regla de requires_approval: aplica solo a salidas
        if (
            movement_type == "OUT"
            and part.requires_approval
            and not user_has_role(user, ROLE_ADMIN, ROLE_ADVISOR)
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Este repuesto requiere aprobación de un administrador "
                    "o asesor para realizar salidas."
                ),
            )

        # Calcular stock nuevo
        if movement_type == "IN":
            new_stock = part.stock_current + quantity
        else:  # OUT
            new_stock = part.stock_current - quantity
            if new_stock < 0:
                raise HTTPException(
                    status_code=400,
                    detail="El movimiento dejaría el stock en negativo",
                )

        movement_at = payload.movement_at or datetime.utcnow()

        movement = part_movement_crud.create(
            db,
            part_id=part.id,
            movement_type=movement_type,
            quantity=quantity,
            document_ref=payload.document_ref,
            movement_at=movement_at,
            responsible_user_id=user.id,
            notes=payload.notes,
        )

        part_crud.update_stock(db, part, new_stock=new_stock)
        part.last_movement_at = movement.movement_at

        # Mantengo la firma original: devolver el repuesto actualizado
        return part

    # ==========================
    # Gestión de partes (solo Admin / Advisor)
    # ==========================
    def create_part(
        self,
        db: Session,
        *,
        user: User,
        payload: PartCreate,
    ) -> Part:
        # Solo Admin / Advisor pueden crear repuestos
        self._ensure_admin_or_advisor(user)

        # Ignoramos cualquier SKU que pueda venir del payload,
        # porque será generado automáticamente.
        data = payload.model_dump()
        data.pop("sku", None)

        # Crear repuesto sin SKU primero
        part = part_crud.create(db, data=data)

        # Generar SKU una vez que tenemos el id
        part.sku = generate_sku(part)
        db.add(part)
        db.commit()
        db.refresh(part)

        return part

    def update_part(
        self,
        db: Session,
        *,
        user: User,
        part_id: int,
        payload: PartUpdate,
    ) -> Part:
        # Solo Admin / Advisor pueden editar repuestos
        self._ensure_admin_or_advisor(user)

        part = self.get_part(db, user=user, part_id=part_id)

        data = payload.model_dump(exclude_unset=True)

        # No permitimos cambiar SKU desde actualización
        if "sku" in data:
            data.pop("sku")

        if not data:
            return part

        part = part_crud.update(db, part, data=data)
        return part

    def delete_part(
        self,
        db: Session,
        *,
        user: User,
        part_id: int,
    ) -> None:
        # Solo Admin / Advisor pueden eliminar (soft delete) repuestos
        self._ensure_admin_or_advisor(user)

        part = self.get_part(db, user=user, part_id=part_id)
        part_crud.soft_delete(db, part)


part_service = PartService()
