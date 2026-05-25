from sqlalchemy.orm import Session
from app.crud.role_crud import role_crud
from app.crud.ticket_status_crud import ticket_status_crud
from app.crud.module_crud import module_crud
from app.crud.module_role_crud import module_role_crud

DEFAULT_ROLES = [
    ("ADMIN", "Full access / owner"),
    ("TECHNICIAN", "Performs diagnostics and repairs"),
    ("ADVISOR", "Front desk / intake / entrega"),
    ("CLIENT", "Customer portal"),
    ("COURIER", "Pickup & delivery logistics"),
]

DEFAULT_STATUSES = [
    ("RECEIVED", "Recibido en taller", 1),
    ("DIAGNOSING", "En diagnóstico", 2),
    ("WAITING_APPROVAL", "Esperando aprobación del cliente", 3),
    ("REPAIRING", "En reparación", 4),
    ("READY", "Listo para entregar", 5),
    ("DELIVERED", "Entregado al cliente", 6),
    ("CLOSED", "Cerrado", 7),
    ("CANCELLED", "Cancelado", 8),
]

DEFAULT_MODULES = [
    ("DASHBOARD", "Panel principal y KPIs"),
    ("TICKETS", "Gestión de tickets y dispositivos"),
    ("USERS", "Gestión de usuarios y roles"),
    ("DEVICES", "Inventario de dispositivos"),
    ("INVENTORY", "Gestión de repuestos e inventarios"),
    ("REPORTS", "Reportes y analítica"),
    ("FINANCE", "Finanzas y facturación"),
]

MODULE_ROLE_MATRIX = {
    "ADMIN": ["DASHBOARD", "TICKETS", "USERS", "DEVICES", "INVENTORY", "REPORTS", "FINANCE"],
    "ADVISOR": ["DASHBOARD", "TICKETS", "DEVICES", "INVENTORY", "FINANCE"],
    "TECHNICIAN": ["DASHBOARD", "TICKETS","INVENTORY"],
    "CLIENT": ["DASHBOARD"],
    "COURIER": ["DASHBOARD", "TICKETS"],
}

class BootstrapService:
    def bootstrap(self, db: Session) -> dict:
        created_roles = 0
        role_map: dict[str, int] = {}
        for name, desc in DEFAULT_ROLES:
            role = role_crud.get_by_name(db, name)
            if not role:
                role = role_crud.create(db, name=name, description=desc)
                created_roles += 1
            role_map[name] = role.id

        created_statuses = 0
        for code, name, order in DEFAULT_STATUSES:
            if not ticket_status_crud.get_by_code(db, code):
                ticket_status_crud.create(db, code=code, name=name, order=order)
                created_statuses += 1

        created_modules = 0
        module_map: dict[str, int] = {}
        for name, desc in DEFAULT_MODULES:
            module = module_crud.get_by_name(db, name)
            if not module:
                module = module_crud.create(db, name=name, description=desc)
                created_modules += 1
            module_map[name] = module.id

        created_permissions = 0
        for role_name, module_names in MODULE_ROLE_MATRIX.items():
            role_id = role_map.get(role_name)
            if not role_id:
                continue
            for module_name in module_names:
                module_id = module_map.get(module_name)
                if not module_id:
                    continue
                existing = module_role_crud.get_by_role_and_module(
                    db, role_id=role_id, module_id=module_id
                )
                if not existing:
                    module_role_crud.create(
                        db,
                        role_id=role_id,
                        module_id=module_id,
                        description=f"{role_name} puede acceder a {module_name}",
                    )
                    created_permissions += 1

        return {
            "roles_created": created_roles,
            "ticket_statuses_created": created_statuses,
            "modules_created": created_modules,
            "module_roles_created": created_permissions,
        }

bootstrap_service = BootstrapService()
