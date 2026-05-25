# Testing

## Filosofía
- Tests son documentación ejecutable. Priorizamos legibilidad sobre brevedad.
- Cobertura objetivo: 70% en `app/services/` y `app/core/` (lógica de negocio). Routes y CRUD se cubren indirectamente.
- Property-based testing donde tenga sentido (validaciones, transiciones, cálculos monetarios).

## Backend

### Stack
- `pytest` — runner.
- `pytest-asyncio` — para tests async (FastAPI).
- `httpx.AsyncClient` — cliente para tests de integración contra la app.
- `hypothesis` — property-based testing.
- `factory_boy` o helpers manuales — para construir entidades.
- SQLite en memoria para tests (override `DB_URL`) o un MySQL dedicado para tests con docker-compose.

### Estructura
```
tests/
├── conftest.py            # fixtures globales (db, client, users por rol)
├── unit/
│   ├── core/
│   │   └── test_ticket_status_transitions.py
│   └── services/
│       ├── test_ticket_service.py
│       └── test_invoice_service.py
├── integration/
│   ├── test_auth_flow.py
│   ├── test_ticket_flow.py
│   └── test_invoice_flow.py
└── property/
    └── test_invariants.py
```

### Naming
- Archivos: `test_*.py`.
- Funciones: `test_<situacion>_<resultado_esperado>`. Ej: `test_create_ticket_with_invalid_status_raises_400`.

### Fixtures clave (a definir en `conftest.py`)
- `db`: sesión de SQLAlchemy con rollback al final.
- `client`: `AsyncClient` de FastAPI con la app.
- `admin_user`, `advisor_user`, `technician_user`, `client_user`: usuarios precreados con su token.
- `auth_headers(user)`: helper que retorna `{"Authorization": f"Bearer {token}"}`.

### Property-based testing — qué probar
Ejemplos de propiedades que debe cumplir el sistema:

1. **Transiciones de estado**: para todo `(state, role)`, `is_valid_transition(state, new_state, role)` retorna `True` solo si `new_state` está en el set documentado.
2. **Cálculo de factura**: `total = sum(items) + tax - discount` debe ser estable bajo reordenamiento de items.
3. **Stock de repuestos**: `stock_actual = stock_inicial + sum(entradas) - sum(salidas)` para todo movimiento histórico.
4. **Saldo de factura**: `saldo = total - sum(pagos)` y nunca puede ser negativo.
5. **Soft delete**: si una entidad tiene `deleted_at`, no aparece en listados por defecto.

### Tests de transiciones (ejemplo concreto)
```python
from hypothesis import given, strategies as st
from app.core.ticket_status_transitions import VALID_TRANSITIONS, is_valid_transition

states = st.sampled_from(list(VALID_TRANSITIONS.keys()) + ["CANCELLED"])

@given(current=states, target=states)
def test_transition_admits_only_documented_targets(current, target):
    valid, _ = is_valid_transition(current, target, role_name="ADMIN")
    if current == target:
        assert valid
    elif target in VALID_TRANSITIONS.get(current, set()):
        assert valid
```

## Frontend

### Stack
- Karma + Jasmine (default Angular CLI) — tests unitarios.
- Playwright o Cypress — E2E (a decidir cuando creemos esa spec).

### Qué probar
- Servicios HTTP: mock de `HttpClient`, verificar URL/método/payload.
- Componentes: render condicional, estado tras input, eventos emitidos.
- Pipes y validators: tablas de casos.

### Lo que NO testeamos en unit
- CSS visual.
- Integración real con backend (eso es E2E).

## Schemathesis (API fuzzing)
Cuando se incorpore:
```bash
schemathesis run http://localhost:8000/openapi.json --base-url http://localhost:8000
```
Encuentra bugs de validación, status codes inconsistentes, errores 500 inesperados.

## CI
Cada PR ejecuta:
1. `ruff check` + `ruff format --check`
2. `mypy app/`
3. `pytest -q --cov=app --cov-report=term-missing`
4. (Frontend) `ng lint` + `ng test --watch=false --browsers=ChromeHeadless`
5. (Frontend) `ng build` para verificar que compila

Solo se mergea con todo en verde.
