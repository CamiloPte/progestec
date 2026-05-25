from typing import Optional, Set, Dict

from app.core.roles import (
    ROLE_ADMIN,
    ROLE_ADVISOR,
    ROLE_TECHNICIAN,
    ROLE_CLIENT,
    ROLE_COURIER,
)

# Estados que puede ver/seleccionar cada rol.
# None indica "todos los estados activos".
STATUS_VISIBILITY_BY_ROLE: Dict[str, Optional[Set[str]]] = {
    ROLE_ADMIN: None,
    ROLE_ADVISOR: None,
    ROLE_TECHNICIAN: {
        "RECEIVED",
        "DIAGNOSING",
        "WAITING_APPROVAL",
        "REPAIRING",
        "READY",
    },
    ROLE_CLIENT: {"READY", "DELIVERED", "CLOSED", "CANCELLED"},
    ROLE_COURIER: {"READY", "DELIVERED"},
}


def get_allowed_status_codes_for_role(role_name: Optional[str]) -> Optional[Set[str]]:
    if not role_name:
        return None
    allowed = STATUS_VISIBILITY_BY_ROLE.get(role_name.upper())
    if allowed is None:
        return None
    return set(code.upper() for code in allowed)
