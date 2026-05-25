"""
Tests para `app.core.ticket_status_transitions`.

Estas pruebas blindan el flujo de estados de un ticket:
RECEIVED → DIAGNOSING → WAITING_APPROVAL → REPAIRING → READY → DELIVERED → CLOSED

Cada cambio futuro al flujo debe pasar por estos tests. Si rompes uno,
estás cambiando una regla de negocio (a propósito o por accidente).
"""

import pytest

from app.core.roles import ROLE_ADMIN, ROLE_ADVISOR, ROLE_CLIENT, ROLE_TECHNICIAN
from app.core.ticket_status_transitions import (
    ADMIN_ONLY_TRANSITIONS,
    VALID_TRANSITIONS,
    get_allowed_transitions,
    is_valid_transition,
)

# ---------------------------------------------------------------------------
# Flujo principal: cada paso es válido para roles con permiso suficiente
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "current,target",
    [
        ("RECEIVED", "DIAGNOSING"),
        ("DIAGNOSING", "WAITING_APPROVAL"),
        ("DIAGNOSING", "REPAIRING"),
        ("WAITING_APPROVAL", "REPAIRING"),
        ("REPAIRING", "READY"),
        ("REPAIRING", "WAITING_APPROVAL"),
        ("READY", "DELIVERED"),
        ("DELIVERED", "CLOSED"),
    ],
)
def test_main_flow_transitions_are_allowed_for_admin(current, target):
    valid, error = is_valid_transition(current, target, role_name=ROLE_ADMIN)
    assert valid is True, f"ADMIN no pudo {current}→{target}: {error}"


# ---------------------------------------------------------------------------
# Estados finales: nadie (ni ADMIN siguiendo flujo normal) avanza desde aquí
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("final_state", ["CLOSED", "CANCELLED"])
def test_final_states_have_no_normal_outgoing_transitions(final_state):
    assert VALID_TRANSITIONS[final_state] == set()


def test_admin_can_reopen_closed_ticket():
    valid, _ = is_valid_transition("CLOSED", "RECEIVED", role_name=ROLE_ADMIN)
    assert valid is True


def test_admin_can_reopen_cancelled_ticket():
    valid, _ = is_valid_transition("CANCELLED", "RECEIVED", role_name=ROLE_ADMIN)
    assert valid is True


def test_advisor_cannot_reopen_closed_ticket():
    valid, _ = is_valid_transition("CLOSED", "RECEIVED", role_name=ROLE_ADVISOR)
    assert valid is False


# ---------------------------------------------------------------------------
# Transición a sí mismo: siempre válida (no es un cambio real)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("state", list(VALID_TRANSITIONS.keys()))
@pytest.mark.parametrize("role", [ROLE_ADMIN, ROLE_ADVISOR, ROLE_TECHNICIAN, ROLE_CLIENT])
def test_self_transition_is_always_allowed(state, role):
    valid, _ = is_valid_transition(state, state, role_name=role)
    assert valid is True


# ---------------------------------------------------------------------------
# Reglas por rol
# ---------------------------------------------------------------------------


def test_client_can_approve_quote():
    """Cliente aprueba presupuesto → REPAIRING."""
    valid, _ = is_valid_transition("WAITING_APPROVAL", "REPAIRING", role_name=ROLE_CLIENT)
    assert valid is True


def test_client_can_reject_quote():
    """Cliente rechaza presupuesto → CANCELLED."""
    valid, _ = is_valid_transition("WAITING_APPROVAL", "CANCELLED", role_name=ROLE_CLIENT)
    assert valid is True


def test_client_cannot_advance_diagnosis():
    """Cliente NO puede mover el ticket fuera del flujo de aprobación."""
    valid, _ = is_valid_transition("DIAGNOSING", "REPAIRING", role_name=ROLE_CLIENT)
    assert valid is False


def test_client_cannot_deliver_ticket():
    """Marcar como entregado es responsabilidad del asesor, no del cliente."""
    valid, _ = is_valid_transition("READY", "DELIVERED", role_name=ROLE_CLIENT)
    assert valid is False


def test_technician_cannot_deliver_ticket():
    """El técnico repara, el asesor entrega. Separación de funciones."""
    valid, _ = is_valid_transition("READY", "DELIVERED", role_name=ROLE_TECHNICIAN)
    assert valid is False


def test_technician_cannot_close_ticket():
    valid, _ = is_valid_transition("DELIVERED", "CLOSED", role_name=ROLE_TECHNICIAN)
    assert valid is False


def test_advisor_can_deliver_and_close():
    valid_d, _ = is_valid_transition("READY", "DELIVERED", role_name=ROLE_ADVISOR)
    valid_c, _ = is_valid_transition("DELIVERED", "CLOSED", role_name=ROLE_ADVISOR)
    assert valid_d is True
    assert valid_c is True


# ---------------------------------------------------------------------------
# Mensajes de error útiles (los necesita el frontend)
# ---------------------------------------------------------------------------


def test_invalid_transition_returns_explanatory_error():
    valid, error = is_valid_transition("RECEIVED", "DELIVERED", role_name=ROLE_ADVISOR)
    assert valid is False
    assert error  # no vacío
    assert "RECEIVED" in error or "DELIVERED" in error


def test_role_restriction_error_mentions_role_or_state():
    valid, error = is_valid_transition("DIAGNOSING", "REPAIRING", role_name=ROLE_CLIENT)
    assert valid is False
    assert error


# ---------------------------------------------------------------------------
# get_allowed_transitions: vista usada por el frontend para mostrar opciones
# ---------------------------------------------------------------------------


def test_admin_sees_all_allowed_transitions_including_admin_only():
    allowed = get_allowed_transitions("CLOSED", role_name=ROLE_ADMIN)
    assert "RECEIVED" in allowed  # rama admin-only


def test_non_admin_does_not_see_admin_only_transitions():
    allowed = get_allowed_transitions("CLOSED", role_name=ROLE_ADVISOR)
    assert "RECEIVED" not in allowed
    assert allowed == set()


def test_client_sees_only_approve_or_reject_from_waiting_approval():
    allowed = get_allowed_transitions("WAITING_APPROVAL", role_name=ROLE_CLIENT)
    assert allowed == {"REPAIRING", "CANCELLED"}


# ---------------------------------------------------------------------------
# Invariantes globales
# ---------------------------------------------------------------------------


def test_admin_only_transitions_do_not_overlap_with_normal_ones():
    """
    Las transiciones admin-only deben ser realmente _solo de admin_,
    no duplicarse en VALID_TRANSITIONS (sería confuso).
    """
    for state, admin_targets in ADMIN_ONLY_TRANSITIONS.items():
        normal_targets = VALID_TRANSITIONS.get(state, set())
        overlap = admin_targets & normal_targets
        assert not overlap, (
            f"Estado {state}: targets {overlap} aparecen en ambos diccionarios"
        )


def test_every_documented_state_has_an_entry_in_valid_transitions():
    expected_states = {
        "RECEIVED",
        "DIAGNOSING",
        "WAITING_APPROVAL",
        "REPAIRING",
        "READY",
        "DELIVERED",
        "CLOSED",
        "CANCELLED",
    }
    assert set(VALID_TRANSITIONS.keys()) == expected_states


def test_case_insensitive_input_is_normalized():
    """El módulo normaliza con .upper(), debemos verificar que funciona."""
    valid_lower, _ = is_valid_transition("received", "diagnosing", role_name="admin")
    valid_upper, _ = is_valid_transition("RECEIVED", "DIAGNOSING", role_name="ADMIN")
    assert valid_lower == valid_upper is True
