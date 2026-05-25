# app/core/ticket_status_transitions.py
"""
Definición de transiciones válidas entre estados de ticket.

Flujo principal:
RECEIVED → DIAGNOSING → WAITING_APPROVAL → REPAIRING → READY → DELIVERED → CLOSED

Casos especiales:
- CANCELLED: Se puede cancelar desde RECEIVED, DIAGNOSING, WAITING_APPROVAL, REPAIRING
- No se puede retroceder de estado (excepto casos autorizados por ADMIN)
- El cliente puede aprobar (→ REPAIRING) o rechazar (→ CANCELLED) desde WAITING_APPROVAL

Notificaciones:
    Las transiciones marcadas con `# TODO(notify): ...` deben disparar
    un email al cliente. Ver `.kiro/steering/notifications.md` para la
    matriz completa de eventos → mensajes.
"""

from typing import Dict, Optional, Set

from app.core.roles import ROLE_ADMIN, ROLE_ADVISOR, ROLE_CLIENT, ROLE_TECHNICIAN

# Transiciones válidas: estado_actual -> estados_permitidos
VALID_TRANSITIONS: Dict[str, Set[str]] = {
    "RECEIVED": {"DIAGNOSING", "CANCELLED"},
    "DIAGNOSING": {
        "WAITING_APPROVAL",
        "REPAIRING",
        "CANCELLED",
    },  # Puede saltar a REPAIRING si no requiere aprobación
    "WAITING_APPROVAL": {"REPAIRING", "CANCELLED"},  # Cliente aprueba → reparación
    "REPAIRING": {
        "READY",
        "WAITING_APPROVAL",
        "CANCELLED",
    },  # Puede volver a esperar aprobación si hay cambios
    "READY": {"DELIVERED", "CANCELLED"},
    "DELIVERED": {"CLOSED"},
    "CLOSED": set(),  # Estado final, no hay transiciones
    "CANCELLED": set(),  # Estado final, no hay transiciones
}

# Transiciones que solo puede hacer el ADMIN (excepciones)
ADMIN_ONLY_TRANSITIONS: Dict[str, Set[str]] = {
    # Admin puede reabrir tickets cerrados o cancelados
    "CLOSED": {"RECEIVED"},
    "CANCELLED": {"RECEIVED"},
    # Admin puede retroceder de DELIVERED a READY si hubo un error
    "DELIVERED": {"READY"},
}

# Transiciones permitidas por rol
# - El técnico no puede marcar como DELIVERED ni CLOSED (eso lo hace el asesor).
# - El cliente solo puede aprobar o rechazar la cotización; cualquier otra
#   transición la deciden los roles internos.
ROLE_TRANSITION_RESTRICTIONS: Dict[str, Set[str]] = {
    ROLE_TECHNICIAN: {
        "DIAGNOSING",
        "WAITING_APPROVAL",
        "REPAIRING",
        "READY",
        "CANCELLED",
    },  # Puede cancelar si cliente no responde
    ROLE_ADVISOR: {
        "DIAGNOSING",
        "WAITING_APPROVAL",
        "REPAIRING",
        "READY",
        "DELIVERED",
        "CLOSED",
        "CANCELLED",
    },
    ROLE_CLIENT: {"REPAIRING", "CANCELLED"},  # Solo puede aprobar o rechazar cotización
    ROLE_ADMIN: None,  # None = sin restricciones
}

# Reglas adicionales para roles con flujos muy acotados.
# Cada entrada define: rol -> {estado_origen: {estados_destino_permitidos}}.
# Si un rol no aparece aquí, se valida solo con ROLE_TRANSITION_RESTRICTIONS.
ROLE_ALLOWED_FROM: Dict[str, Dict[str, Set[str]]] = {
    # El cliente solo puede actuar cuando hay un presupuesto pendiente.
    # Aprobar  → REPAIRING
    # Rechazar → CANCELLED
    ROLE_CLIENT: {
        "WAITING_APPROVAL": {"REPAIRING", "CANCELLED"},
    },
}


def is_valid_transition(
    current_status: str,
    new_status: str,
    role_name: Optional[str] = None,
) -> tuple[bool, str]:
    """
    Valida si una transición de estado es permitida.

    Returns:
        tuple: (is_valid: bool, error_message: str)
    """
    current = current_status.upper()
    new = new_status.upper()
    role = (role_name or "").upper()

    # Mismo estado, no hay cambio
    if current == new:
        return True, ""

    # Admin tiene permisos especiales
    if role == ROLE_ADMIN:
        admin_allowed = ADMIN_ONLY_TRANSITIONS.get(current, set())
        normal_allowed = VALID_TRANSITIONS.get(current, set())
        all_allowed = admin_allowed | normal_allowed

        if new in all_allowed:
            return True, ""
        return False, f"Transición no permitida: {current} → {new}"

    # Verificar transición válida en el flujo normal
    allowed_next = VALID_TRANSITIONS.get(current, set())
    if new not in allowed_next:
        return (
            False,
            f"No se puede cambiar de '{current}' a '{new}'. Estados permitidos: {', '.join(allowed_next) or 'ninguno'}",
        )

    # Verificar restricciones por rol (set de estados destino permitidos).
    role_allowed = ROLE_TRANSITION_RESTRICTIONS.get(role)
    if role_allowed is not None and new not in role_allowed:
        return False, f"Tu rol no permite cambiar a estado '{new}'"

    # Restricciones adicionales: algunos roles solo pueden actuar desde
    # estados de origen específicos (ej. CLIENT solo desde WAITING_APPROVAL).
    role_from = ROLE_ALLOWED_FROM.get(role)
    if role_from is not None:
        allowed_targets_from_current = role_from.get(current, set())
        if new not in allowed_targets_from_current:
            return (
                False,
                f"Tu rol solo puede cambiar el estado desde "
                f"{', '.join(role_from.keys()) or 'ningún estado'}",
            )

    return True, ""


def get_allowed_transitions(
    current_status: str,
    role_name: Optional[str] = None,
) -> Set[str]:
    """
    Obtiene los estados a los que se puede transicionar desde el estado actual.
    """
    current = current_status.upper()
    role = (role_name or "").upper()

    # Transiciones normales
    allowed = VALID_TRANSITIONS.get(current, set()).copy()

    # Admin tiene transiciones extra
    if role == ROLE_ADMIN:
        admin_extra = ADMIN_ONLY_TRANSITIONS.get(current, set())
        allowed = allowed | admin_extra

    # Filtrar por rol si aplica
    role_allowed = ROLE_TRANSITION_RESTRICTIONS.get(role)
    if role_allowed is not None:
        allowed = allowed & role_allowed

    # Si el rol tiene restricciones por estado de origen, aplicarlas también.
    role_from = ROLE_ALLOWED_FROM.get(role)
    if role_from is not None:
        allowed = allowed & role_from.get(current, set())

    return allowed
