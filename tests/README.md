# Tests

## Cómo correrlos

Todo dentro del contenedor Docker para usar el mismo entorno que la app.

```bash
# Una vez: instalar dependencias de desarrollo
docker compose exec app pip install -r requirements-dev.txt

# Correr todos los tests
docker compose exec app pytest

# Correr solo un archivo
docker compose exec app pytest tests/unit/core/test_ticket_status_transitions.py

# Correr con detalle
docker compose exec app pytest -v

# Correr con cobertura
docker compose exec app pytest --cov=app --cov-report=term-missing
```

## Estructura

```
tests/
├── conftest.py            # Fixtures globales (cuando existan)
├── unit/                  # Tests rápidos, sin DB ni red
│   ├── core/             # Tests de funciones puras
│   └── services/         # Tests de lógica de negocio
├── integration/           # Tests con DB y/o cliente HTTP
└── property/              # Tests basados en propiedades (Hypothesis)
```

## Convenciones

- Archivos: `test_*.py`
- Funciones: `test_<situacion>_<resultado_esperado>`
  - Ejemplo: `test_create_ticket_with_invalid_status_raises_400`
- Un test = una afirmación clara. Si el test es difícil de nombrar, probablemente prueba dos cosas.

Más detalle en `.kiro/steering/testing.md`.
