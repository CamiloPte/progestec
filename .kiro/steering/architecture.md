# Arquitectura

## Vista general
Monorepo con tres unidades desplegables:
- `app/` — API principal (FastAPI + MySQL)
- `progestec-front/` — frontend Angular
- `catalog-service/` — microservicio catálogo (Express + Postgres)

Comunicación: el frontend habla REST con la API y con el catálogo directamente. La API y el catálogo no se hablan entre sí (por ahora).

## Capas del backend (`app/`)
La regla de oro: **las dependencias siempre apuntan hacia adentro**.

```
api/routes/   → services/   → crud/   → models/
                  │             │
                  └──→ schemas/ │
                                └──→ db/
core/  ← usado transversalmente (config, security, exceptions, logger, roles)
```

### Reglas de capas
- **`api/routes/`**: solo orquestación HTTP. Reciben request, llaman a un service, devuelven response. **No** ejecutan SQL ni reglas de negocio.
- **`services/`**: contienen la lógica de negocio. Reciben `Session` + datos validados, retornan modelos o DTOs. Pueden coordinar varios `crud`.
- **`crud/`**: solo acceso a datos. Una función por operación atómica (`get_by_id`, `list_paginated`, `create`, `update`, `delete`). **No** validan reglas de negocio.
- **`models/`**: SQLAlchemy. Definen tablas y relaciones. **No** contienen lógica.
- **`schemas/`**: Pydantic. Definen contratos de entrada/salida HTTP. Hay `Create`, `Update`, `Read`, y a veces `*WithRelations` para respuestas anidadas.
- **`core/`**: utilidades sin estado de negocio (config, JWT, hashing, logger, manejadores de excepciones, constantes de roles).
- **`db/`**: configuración de SQLAlchemy y `Base`.

### Antipatrones que rechazamos
- Llamar `crud.*` desde `routes/` directamente (saltarse el service). Se permite SOLO para operaciones triviales sin reglas (ej. healthchecks). En cualquier caso con reglas, el service es obligatorio.
- Lógica de negocio en `models/` (métodos que mutan estado, validan transiciones, etc.).
- Schemas que importan models (debe ser al revés cuando se requiera).
- `print()` o `logging.basicConfig` ad-hoc — usar siempre `from app.core.logger import logger`.

## Capas del frontend (`progestec-front/src/app/`)
```
core/           → infraestructura (services HTTP, models, layouts, guards, interceptors)
auth/           → login y flujos de autenticación
<feature>/     → módulos de feature (tickets/, devices/, finance/, ...)
shared/         → componentes y utilidades compartidos entre features
```

### Reglas
- Cada feature tiene componentes propios y consume `services` desde `core/services/`.
- Los `services` no llaman a otros `services` salvo cuando es estrictamente necesario (evitar grafo de dependencias circular).
- Modelos de dominio en `core/models/` reflejan los schemas del backend (sufijo de feature, no `interface I*`).

## Microservicio catálogo
- Aislado con su propia DB (Postgres 16).
- Solo expone GET (por ahora). Los datos de manufacturers/models/variants son maestros, no transaccionales.
- El backend principal **no** consulta el catálogo; solo guarda los IDs (`manufacturer_id`, `model_id`, `variant_id`). El frontend resuelve los nombres pidiendo al catálogo directamente.

## Manejo de errores
Backend tiene tres manejadores globales (`app/core/exceptions.py`):
- `HTTPException` → respuesta tipada con `error.type` + `error.code` + `error.message`
- `RequestValidationError` (422) → detalla campos inválidos
- `Exception` (500) → log con `exc_info` y respuesta genérica al cliente

El frontend debe leer `error.error.message` para mostrar al usuario.

## Autenticación
- Login → token JWT (HS256) con expiración configurable.
- Cada request lleva `Authorization: Bearer <token>`.
- Dependencia `get_current_user` resuelve el usuario y su rol desde el token.
- RBAC se aplica en services o en dependencias específicas (`require_roles(...)`).
