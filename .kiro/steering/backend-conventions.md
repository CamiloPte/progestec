# Convenciones del Backend

## Naming
- Archivos: `snake_case.py`. Modelos en singular (`ticket.py`, `user.py`); módulos de routes y crud en singular o plural según ya esté establecido (mantener consistencia con el directorio).
- Clases: `PascalCase`. Modelos SQLAlchemy = nombre de entidad (`Ticket`, `Invoice`).
- Funciones y variables: `snake_case`.
- Constantes: `UPPER_SNAKE_CASE`.
- Schemas: sufijos claros — `TicketCreate`, `TicketUpdate`, `TicketRead`, `TicketWithRelations`.

## Modelos SQLAlchemy
- Usar el estilo declarativo 2.0 con `Mapped[...]` y `mapped_column(...)`.
- Heredar de `app.db.base_class.Base`.
- Mixins en `app/models/mixins.py` para `id`, `created_at`, `updated_at`.
- Foreign keys con `ondelete` explícito (`CASCADE`, `SET NULL`, `RESTRICT`) — **nunca** dejar el default sin pensar.
- `relationship(...)` siempre con `back_populates` (no `backref`).
- Tablas en plural en snake_case (`tickets`, `ticket_history`, `invoice_payments`).

## Schemas Pydantic
- Modo Pydantic 2: `model_config = ConfigDict(from_attributes=True)` para schemas que leen modelos.
- Validaciones de formato en el schema (`EmailStr`, `Annotated[str, StringConstraints(...)]`), no en el service.
- Schemas de Read **nunca** exponen `password_hash`, tokens o IDs internos sensibles.

## Services
- Una función pública por caso de uso (`create_ticket`, `assign_technician`, `transition_status`, ...).
- Validan reglas de negocio antes de llamar al CRUD.
- Devuelven el modelo SQLAlchemy resultante o un DTO; el route lo serializa con su schema Read.
- Si una operación toca múltiples tablas, **debe** estar en un service, dentro de la misma transacción.

## CRUD
- Funciones cortas y declarativas. No mezclan operaciones (`create_with_history` no va aquí).
- Usar `db.execute(select(...))` (SQLAlchemy 2.0), no la API legacy `db.query(...)`.
- Paginación obligatoria en listados: `skip`, `limit`, con tope superior (`min(limit, 100)`).

## Routes
- Un router por dominio (`ticket.py`, `finance.py`).
- Prefijo y tags definidos al crear el `APIRouter`: `APIRouter(prefix="/api/tickets", tags=["tickets"])`.
- `response_model=` siempre presente para que aparezca en OpenAPI con tipos correctos.
- Códigos HTTP: 200 para read, 201 para create, 204 para delete sin body, 200/202 para updates.
- Errores con `HTTPException` y mensaje en español orientado al usuario; el `type` (mapeado en `exceptions.py`) lo decide el código.

## Logging
- Importar `from app.core.logger import logger`.
- Niveles:
  - `debug`: detalles de desarrollo (SQL custom, valores intermedios).
  - `info`: hitos de negocio (ticket creado, factura emitida).
  - `warning`: comportamiento inesperado pero recuperable (auth fallido, transición rechazada).
  - `error`: excepciones que merecen revisión.
- Nunca loguear contraseñas, tokens, ni payloads completos con PII.

## Manejo de transacciones
- En services, abrir transacciones explícitas cuando se mutan varias tablas (`with db.begin_nested(): ...`) o usar el patrón de unit-of-work con `db.commit()` solo al final del service.
- Si lanzas `HTTPException` dentro del service, asegúrate de que el `Session` haga rollback (FastAPI lo hace si la dependencia inyectada usa `try/finally`, verifica `app/db/session.py`).

## Validación de inputs externos
- IDs numéricos siempre `int` con `ge=1`.
- Strings con longitud máxima: usar `Annotated[str, StringConstraints(max_length=...)]`.
- Decimales monetarios: `Decimal` (no `float`). Hablamos pesos colombianos en COP, mantener escala consistente (2 decimales).

## Documentación inline
- Docstring corto en cada función pública del service y del crud.
- No comentar lo obvio. Comentar el _porqué_, no el _qué_.
- Comentarios de revisión histórica (`# [Revisión] ...`) ya presentes — están OK como anotación; al refactorizar se eliminan junto al cambio.
