# Implementation Plan — Consolidación del flujo de tickets

> **Spec:** `tickets-flow-consolidation` · **Workflow:** requirements-first
> **Lenguaje:** Python 3.11 (FastAPI + SQLAlchemy 2.0 + Alembic)
> **Inputs:** `requirements.md` cerrado, `design.md` cerrado, decisiones D1–D10 y open questions OQ1–OQ5 resueltas.

## Overview

Plan ejecutable, ordenado por dependencias. Cada tarea entrega valor verificable (un test pasa, un endpoint responde, una migración corre). Las sub-tareas marcadas con `*` (postfijo del checkbox) son opcionales y pueden omitirse para acelerar el MVP — son tests adicionales y documentación.

**Restricciones globales que aplican a todas las tareas:**

- No tocar `app/core/ticket_status_transitions.py` ni los 60 tests de `tests/unit/core/test_ticket_status_transitions.py`.
- Migraciones backward-compatible (solo añaden).
- No implementar emails: los `# TODO(notify)` permanecen anclados.
- Backend únicamente; nada de frontend en este spec.
- No tocar `delivery_order`, `invoice_*`, `expense_*`, `part_*` (solo lectura cuando ya está integrado en serializaciones existentes).

## Tasks

### Fase 1 — Cimientos (sin afectar API existente)

- [x] 1. Migración Alembic `add_priority_to_tickets`
  - [ ] 1.1 Generar archivo de migración
    - `alembic revision --autogenerate -m "add_priority_to_tickets"` (revisar `alembic heads` antes para no fork-ear).
    - Añadir `op.add_column('tickets', sa.Column('priority', sa.Enum('LOW','NORMAL','HIGH','URGENT', name='ticket_priority'), server_default='NORMAL', nullable=False))`.
    - Implementar `downgrade()` con `op.drop_column('tickets', 'priority')`.
    - _Refs: Req 3.1.1; Migration Plan §1_

  - [ ] 1.2 Verificar upgrade/downgrade en contenedor Docker
    - `alembic upgrade head` debe completar sin error y poblar `priority='NORMAL'` en filas existentes.
    - `alembic downgrade -1` debe revertir limpiamente.
    - _Refs: Req 3.1.1; database-migrations.md_

  - [ ] 1.3 Actualizar `app/models/ticket.py`
    - Añadir columna `priority` con `Mapped[str]` y enum `("LOW","NORMAL","HIGH","URGENT")`, default `NORMAL`, `server_default="NORMAL"`, `nullable=False`.
    - _Refs: Req 3.1.1; Data Models §A_

  - [ ] 1.4 Actualizar schemas en `app/schemas/ticket.py`
    - `TicketCreate`: `priority: Optional[Literal["LOW","NORMAL","HIGH","URGENT"]] = "NORMAL"`.
    - `TicketUpdate`: `priority: Optional[Literal[...]] = None`.
    - `TicketReadMinimal` y `TicketReadDetail`: `priority: Literal[...] = "NORMAL"`.
    - _Refs: Req 3.1.1; Data Models §D_

- [ ] 2. Migración Alembic `add_sla_config_table`
  - [ ] 2.1 Generar archivo con tabla y unique constraint
    - `op.create_table('sla_config', ...)` con columnas `id, state_code, device_type, priority, max_hours, is_active, state, created_at, updated_at` (heredando `PKMixin` + `TimestampStateMixin`).
    - `UniqueConstraint('state_code','device_type','priority', name='uq_sla_state_device_priority')`.
    - Índices en `state_code` y `device_type`.
    - Implementar `downgrade()` con `op.drop_table('sla_config')`.
    - _Refs: Req 3.1.2; Data Models §B; Migration Plan §2_

  - [ ] 2.2 Incluir bulk_insert con datos seed
    - 8 filas placeholder (DIAGNOSING/WAITING_APPROVAL/REPAIRING/READY × tipos × prioridad NORMAL/URGENT).
    - Comentario `# TODO(sla-tuning): valores placeholder; el admin ajusta desde panel`.
    - _Refs: Req 3.1.7; Data Models §B (seed)_

  - [ ] 2.3 Crear `app/models/sla_config.py`
    - Clase `SLAConfig(Base, PKMixin, TimestampStateMixin)` con `__tablename__ = "sla_config"` y `__table_args__` con el `UniqueConstraint`.
    - _Refs: Req 3.1.2; Data Models §B_

  - [ ] 2.4 Registrar modelo en `app/models/__init__.py` y `app/db/base.py`
    - Importar `SLAConfig` en ambos archivos para que Alembic y SQLAlchemy lo descubran.
    - _Refs: Req 3.1.2_

  - [ ] 2.5 Verificar upgrade/downgrade
    - `alembic upgrade head` crea la tabla y carga 8 filas seed.
    - `alembic downgrade -1` la elimina sin error.
    - _Refs: database-migrations.md_

- [ ] 3. Migración Alembic `add_internal_notification_table`
  - [ ] 3.1 Generar archivo con tabla, FK y unique constraint compuesto
    - `op.create_table('internal_notification', ...)` con columnas `id, recipient_role, recipient_user_id, reason, entity_type, entity_id, breach_at, payload (JSON), read_at, state, created_at, updated_at`.
    - FK `recipient_user_id → users.id` con `ondelete="SET NULL"`, `onupdate="CASCADE"`.
    - `UniqueConstraint('entity_type','entity_id','reason','breach_at', name='uq_notif_entity_reason_breach')`.
    - Índices en `recipient_role`, `recipient_user_id`, `reason`, `entity_type`, `entity_id`, `breach_at`.
    - Implementar `downgrade()`.
    - _Refs: Req 3.3.3, 3.3.4; Data Models §C; Migration Plan §3_

  - [ ] 3.2 Crear `app/models/internal_notification.py`
    - Clase `InternalNotification(Base, PKMixin, TimestampStateMixin)`.
    - _Refs: Req 3.3.3; Data Models §C_

  - [ ] 3.3 Registrar modelo en `app/models/__init__.py` y `app/db/base.py`
    - _Refs: Req 3.3.3_

  - [ ] 3.4 Verificar upgrade/downgrade
    - _Refs: database-migrations.md_

### Fase 2 — Permisos finos (fachada)

- [ ] 4. Crear `app/core/permissions.py` con fachada `user_can` y constantes `CAP_*`
  - [ ] 4.1 Implementar `user_can(user, capability)` con fallback hardcodeado por rol
    - Constantes `CAP_TICKETS_APPROVE_QUOTE`, `CAP_SLA_MANAGE`, `CAP_SLA_READ`.
    - Fallback: `tickets.approve_quote` → ADMIN/ADVISOR; `sla.manage` → ADMIN; `sla.read` → ADMIN/ADVISOR.
    - "Negar por defecto" para capabilities desconocidas.
    - Docstring con `TODO(rbac-fine-grained-permissions)` apuntando al spec futuro.
    - _Refs: Req 4.4-bis.2, 3.1.5, 3.1.6; Components §1_

  - [ ]* 4.2 Tests unitarios en `tests/unit/core/test_permissions.py`
    - Cobertura 100%: matriz rol × capability para todas las constantes + capability inexistente.
    - _Refs: Req 4.4-bis.2; Cobertura esperada (permissions = 100%)_

### Fase 3 — Visibilidad CLIENT corregida

- [ ] 5. Corregir `STATUS_VISIBILITY_BY_ROLE[ROLE_CLIENT]` en `app/core/ticket_status_visibility.py`
  - [ ] 5.1 Cambiar la lista a todos los estados del flujo
    - `{RECEIVED, DIAGNOSING, WAITING_APPROVAL, REPAIRING, READY, DELIVERED, CLOSED, CANCELLED}`.
    - _Refs: Req 4.4.2; Decisión D2; Components §7_

  - [ ]* 5.2 Test integration en `tests/integration/test_client_visibility.py`
    - Crear ticket de un CLIENT, ponerlo en `WAITING_APPROVAL`, verificar que `GET /tickets/{id}` autenticado como ese CLIENT responde 200 y trae el ticket (regresión del bug original).
    - Cubrir además los demás estados nuevos (`RECEIVED`, `DIAGNOSING`, `REPAIRING`).
    - _Refs: Req 4.4.1, 4.4.2; Property P12_

### Fase 4 — Refactor del service: única vía de transición

- [ ] 6. Refactorizar `app/services/ticket_service.py` con `transition_status` como única función pública para mutar `status_id`
  - [ ] 6.1 Implementar firma nueva con todas las validaciones
    - `transition_status(db, ticket, new_status_code, user, *, note=None, acted_on_behalf_of_client=False, reopen_reason=None) -> Ticket`.
    - Llama a `is_valid_transition`; si False → HTTP 400.
    - Capability `tickets.approve_quote` para `WAITING_APPROVAL → REPAIRING/CANCELLED` cuando actor no es CLIENT (vía `user_can`).
    - Validación de `reopen_reason` (mín 10 chars) para `CLOSED/CANCELLED → RECEIVED`.
    - Actualiza timestamps `ready_at`/`delivered_at`/`closed_at` según destino.
    - Inserta una fila en `ticket_history` con nota contextual.
    - Hook `# TODO(notify): hook email tras transición exitosa`.
    - Toda la mutación dentro de la misma transacción.
    - _Refs: Req 1.1.1, 1.1.2, 1.1.3, 1.1.4, 1.1.5, 1.2.1, 4.4-bis.1, 4.4-bis.3, 4.4-bis.5, 6.1.1, 6.1.2, 6.1.3; Components §2_

  - [ ] 6.2 Refactorizar `update_ticket` para delegar en `transition_status`
    - Pop `status_id`, `history_note`, `reopen_reason`, `acted_on_behalf_of_client` del payload.
    - Persistir el resto de campos primero.
    - Si hay cambio de `status_id`, llamar `transition_status` con la nota y el reopen_reason.
    - Si no hay cambio de estado pero sí `history_note`, registrar la nota y commit (comportamiento actual).
    - _Refs: Req 1.1.5, 1.2.1, 1.2.2_

  - [ ] 6.3 Refactorizar el handler de `PATCH /tickets/{id}/quote-response`
    - Eliminar la construcción manual de `TicketUpdate(status_id=...)`.
    - Delegar directo en `ticket_service.transition_status` con el destino correcto y `acted_on_behalf_of_client` derivado del rol del actor.
    - _Refs: Req 1.1.5, 1.2.1, 4.4-bis.1, 4.4-bis.4_

  - [ ] 6.4 Documentar inventario en docstring del módulo
    - Listar en el docstring de `app/services/ticket_service.py` los endpoints que mutan `status_id` actualmente: `PUT /tickets/{id}` y `PATCH /tickets/{id}/quote-response`.
    - Aclarar que `PATCH /tickets/{id}/assign` y `POST /tickets/{id}/claim` NO cambian estado (decisión OQ1).
    - _Refs: Req 1.2.3; Endpoints §Inventario_

  - [ ]* 6.5 Tests unitarios en `tests/unit/services/test_transition_status.py`
    - Matriz de escenarios: ADMIN/ADVISOR avanza, TECHNICIAN avanza, CLIENT aprueba, CLIENT rechaza, ADMIN/ADVISOR auto-aprueba, TECHNICIAN sin permiso, ADMIN reabre con motivo, ADMIN reabre sin motivo, transición inválida.
    - Asserts: HTTP code, fila en `ticket_history`, formato de la nota, timestamps poblados.
    - _Refs: Req 1.1; Properties P1, P2, P3, P4, P13_

  - [ ]* 6.6 Tests integration en `tests/integration/test_ticket_flow.py`
    - End-to-end: cada endpoint que cambia estado, por cada rol relevante, con verificación de respuesta y persistencia.
    - _Refs: Req 1.1, 1.2; Property P1_

  - [ ] 6.7 Verificar que los 60 tests existentes siguen verdes
    - `pytest tests/unit/core/test_ticket_status_transitions.py -v` debe seguir reportando 60 passed sin tocar el archivo.
    - _Refs: Req 1.3.1, 1.3.2, 1.3.3_

- [ ] 7. Checkpoint — Asegurar que tests existentes y nuevos pasan
  - Ejecutar `pytest tests/` localmente. Asegurar que los 60 tests existentes siguen verdes y los nuevos de Fase 4 pasan. Preguntar al usuario si surgen dudas.
  - _Refs: Req 1.3_

### Fase 5 — Reapertura con motivo

- [ ] 8. Implementar validación de `reopen_reason` (ya cableada por la fachada en T6)
  - [ ] 8.1 Schema `TicketUpdate` acepta `reopen_reason`
    - `reopen_reason: Optional[Annotated[str, StringConstraints(min_length=10, max_length=500)]] = None`.
    - _Refs: Req 6.1.4; Data Models §D_

  - [ ] 8.2 Validación contextual en `transition_status`
    - Si origen ∈ {`CLOSED`, `CANCELLED`} y destino == `RECEIVED`: exigir `reopen_reason` con `len(reopen_reason.strip()) >= 10`. Si falta, HTTP 400 "Debes indicar un motivo de reapertura de al menos 10 caracteres".
    - _Refs: Req 6.1.1, 6.1.2_

  - [ ] 8.3 Formato de nota en `ticket_history`
    - Prefijo "Reapertura por {full_name}: " concatenado con el motivo aportado.
    - _Refs: Req 6.1.3; Property P4_

  - [ ]* 8.4 Tests integration en `tests/integration/test_reopen.py`
    - ADMIN reabre con motivo válido (200, fila history con prefijo). ADMIN reabre sin motivo (400). ADMIN reabre con motivo de 9 chars (400). Rol no-ADMIN intenta reabrir (400, transición inválida).
    - _Refs: Req 6.1.1, 6.1.2, 6.1.3; Property P4_

### Fase 6 — Auto-aprobación gobernada por capability

- [ ] 9. Implementar lógica de auto-aprobación en `transition_status` (ya cableada en T6)
  - [ ] 9.1 Schema `TicketUpdate` acepta `acted_on_behalf_of_client`
    - `acted_on_behalf_of_client: bool = False`.
    - _Refs: Req 4.4-bis.4; Data Models §D_

  - [ ] 9.2 Validación de capability en `transition_status`
    - Cuando actor no es CLIENT y la transición es `WAITING_APPROVAL → REPAIRING/CANCELLED`: exigir `user_can(user, CAP_TICKETS_APPROVE_QUOTE)`.
    - Si falla: HTTP 403 "No tienes permiso para aprobar cotizaciones en nombre del cliente".
    - Si actor no es CLIENT y `acted_on_behalf_of_client` es False/ausente, asumir implícitamente True.
    - _Refs: Req 4.4-bis.1, 4.4-bis.2, 4.4-bis.4, 4.4-bis.5_

  - [ ] 9.3 Formato distinguible de la nota
    - CLIENT: `"Cliente {full_name} aprobó/rechazó el presupuesto"`.
    - Personal interno: `"Auto-aprobado/rechazado por {rol} {full_name} en nombre del cliente"`.
    - _Refs: Req 4.4-bis.3; Property P13_

  - [ ]* 9.4 Tests integration en `tests/integration/test_quote_response.py`
    - CLIENT propietario aprueba/rechaza (200, nota "Cliente …").
    - ADMIN aprueba en nombre del cliente (200, nota "Auto-aprobado por ADMIN …").
    - ADVISOR aprueba en nombre del cliente (200).
    - TECHNICIAN sin permiso intenta aprobar (403).
    - CLIENT no propietario intenta aprobar (403/404 según orden de validación existente).
    - _Refs: Req 4.4-bis; Property P13_

### Fase 7 — Claim ticket con concurrencia

- [ ] 10. Implementar `POST /tickets/{id}/claim`
  - [ ] 10.1 Crear `claim_atomic` en `app/crud/ticket_crud.py`
    - `UPDATE tickets SET assignee_user_id = :uid WHERE id = :id AND state = 1 AND assignee_user_id IS NULL`.
    - Retornar `result.rowcount or 0`.
    - Comentario `# CONCURRENCY: optimista — UPDATE…WHERE assignee_user_id IS NULL`.
    - _Refs: Req 2.2.1, 2.2.2, 2.2.3, 7.1.2; Components §3, Concurrency Strategy_

  - [ ] 10.2 Implementar `claim_ticket` en `app/services/ticket_service.py`
    - Validar rol TECHNICIAN (403), ticket existente y `state == 1` (404), estado en `{RECEIVED, DIAGNOSING}` (400).
    - Llamar `claim_atomic`; si rowcount != 1, HTTP 409 "El ticket ya fue tomado por otro técnico".
    - Insertar fila `ticket_history` con nota `"Técnico {full_name or email} reclamó el ticket"` dentro de la misma transacción.
    - `db.commit()` único al final.
    - Retornar `TicketReadDetail` actualizado.
    - _Refs: Req 2.1.1, 2.1.2, 2.1.3, 2.1.4, 2.1.5, 2.1.6, 2.2.1, 2.2.4_

  - [ ] 10.3 Anchor `# TODO(carga-tecnico)`
    - Marcar el lugar antes de `claim_atomic` con `# TODO(carga-tecnico): aplicar límite por usuario aquí`.
    - _Refs: Req 2.5.2_

  - [ ] 10.4 Crear endpoint en `app/api/routes/ticket.py`
    - `POST /tickets/{ticket_id}/claim` con `response_model=TicketReadDetail`, dependencia `get_current_user`.
    - Delega en `ticket_service.claim_ticket(db, ticket_id, current_user)`.
    - _Refs: Req 2.1.1; Endpoints §1_

  - [ ]* 10.5 Tests integration en `tests/integration/test_claim_endpoint.py`
    - 200 (técnico toma ticket sin asignar en RECEIVED y en DIAGNOSING).
    - 400 (técnico intenta tomar ticket en WAITING_APPROVAL/REPAIRING/READY/etc.).
    - 403 (rol no técnico).
    - 404 (ticket inexistente o `state != 1`).
    - 409 (ticket ya asignado a otro).
    - Verificar fila `ticket_history` y nota correcta.
    - _Refs: Req 2.1.2–2.1.6; Property P5_

  - [ ]* 10.6 Test de concurrencia en `tests/integration/test_claim_concurrency.py`
    - `ThreadPoolExecutor(max_workers=10)` con 10 técnicos distintos sobre el mismo ticket.
    - Aserciones: exactamente una respuesta 200, las demás 409. Una sola fila nueva en `ticket_history`. `assignee_user_id` final == ganador.
    - _Refs: Req 2.2.1, 2.2.4; Property P6_

### Fase 8 — Reasignación con concurrencia

- [ ] 11. Refactorizar reasignación por ADMIN/ADVISOR para usar `reassign_atomic`
  - [ ] 11.1 Crear `reassign_atomic` en `app/crud/ticket_crud.py`
    - Firma: `reassign_atomic(db, *, ticket_id, expected_old_id, new_assignee_id) -> int`.
    - `UPDATE … WHERE id = :id AND state = 1 AND assignee_user_id <op> :expected_old_id` (cond `IS NULL` cuando `expected_old_id is None`).
    - Comentario `# CONCURRENCY: optimista con check de versión por valor anterior`.
    - _Refs: Req 7.1.3; Components §3, Concurrency Strategy_

  - [ ] 11.2 Modificar `update_ticket` para usar `reassign_atomic` cuando hay cambio de `assignee_user_id`
    - Solo cuando rol es ADMIN/ADVISOR y el campo viene en el payload.
    - Si rowcount != 1: HTTP 409 "El técnico asignado cambió mientras editabas. Recarga el ticket.".
    - Registrar entrada en `ticket_history` con nota "Reasignado de {anterior} a {nuevo} por {actor}".
    - _Refs: Req 2.4.1, 2.4.2, 7.1.3; Concurrency Strategy_

  - [ ] 11.3 Anchor `# TODO(carga-tecnico)` en reasignación
    - Marcar el lugar previo al `reassign_atomic` con `# TODO(carga-tecnico): aplicar límite por usuario`.
    - _Refs: Req 2.5.2_

  - [ ]* 11.4 Test de concurrencia en `tests/integration/test_reassign_concurrency.py`
    - Dos ADMIN reasignan a técnicos distintos simultáneamente con el mismo `expected_old_id`.
    - Aserciones: una 200 y una 409. Estado final coherente.
    - _Refs: Req 2.4, 7.1.3; Property P7_

### Fase 9 — Devolución por TECHNICIAN

- [ ] 12. Validar Requisito 2.3 (devolver solo en RECEIVED/DIAGNOSING)
  - [ ] 12.1 Verificar que la lógica actual ya cubre el caso
    - Revisar `update_ticket` en su rama TECHNICIAN: el check de estado al setear `assignee_user_id = null` sigue activo y devuelve 400 con el mensaje exacto del Req 2.3.2.
    - Si ya estaba, dejar nota en commit `chore(tickets): verificar regla de devolución sin cambios funcionales`.
    - _Refs: Req 2.3.1, 2.3.2_

  - [ ] 12.2 Asegurar entrada en `ticket_history`
    - Cuando el TECHNICIAN devuelve un ticket asignado (assignee_user_id pasa de su id a null), insertar fila con nota `"Técnico {full_name} liberó el ticket"`.
    - _Refs: Req 2.3.3; Property P8_

  - [ ]* 12.3 Tests integration en `tests/integration/test_ticket_flow.py`
    - Casos: TECHNICIAN devuelve en RECEIVED/DIAGNOSING (200, fila history correcta). TECHNICIAN intenta devolver en WAITING_APPROVAL/REPAIRING/READY (400 con mensaje del Req 2.3.2).
    - _Refs: Req 2.3; Property P8_

### Fase 10 — SLA: cálculo y configuración

- [ ] 13. Implementar `app/services/sla_service.py`
  - [ ] 13.1 Función `compute_sla(db, ticket) -> tuple[bool, int]`
    - Pura, no muta el ticket.
    - Si estado terminal → `(False, 0)`.
    - Buscar `last_history` con `status_id == ticket.status_id` (ya creado en `ticket_crud.get_last_history_for_status`).
    - Buscar `sla_config` aplicable con fallback (estado×tipo×prioridad → estado×tipo×NORMAL → estado×NULL×NORMAL → None).
    - `delta_hours = int((utcnow() - last_history.created_at).total_seconds() // 3600)` (enteros truncados, OQ4).
    - Si `delta_hours > cfg.max_hours` → `(True, delta_hours - cfg.max_hours)`. Sino `(False, 0)`.
    - _Refs: Req 3.1.3, 3.1.4, 3.2.1, 3.2.4, 3.2.5, 3.3.2; Decisión OQ4_

  - [ ] 13.2 Función `record_breach_if_new(db, ticket, overdue_hours)`
    - `breach_at = last_history.created_at` (estable durante un mismo ciclo en el estado).
    - Si ya existe `internal_notification` con `(entity_type='ticket', entity_id, reason='SLA_BREACH', breach_at)`: skip.
    - Resolver destinatario por contexto (decisión OQ3):
      - Estado ∈ {`DIAGNOSING`, `REPAIRING`} y `assignee_user_id is not None` → `recipient_user_id = ticket.assignee_user_id`.
      - Otros estados o sin asignado → `recipient_role = 'ADVISOR'`.
    - Insertar `InternalNotification` con `payload = {"overdue_hours": ..., "state_code": ...}`.
    - _Refs: Req 3.3.3, 3.3.4; Decisión OQ3; Properties P11_

  - [ ] 13.3 Función `get_last_history_for_status` en `app/crud/ticket_crud.py`
    - Si no existe: `db.execute(select(TicketHistory).where(...).order_by(TicketHistory.created_at.desc()).limit(1))`.
    - _Refs: Req 3.2.5; Components §3_

  - [ ]* 13.4 Tests unitarios en `tests/unit/services/test_compute_sla.py`
    - Estado terminal → `(False, 0)`.
    - Sin config aplicable → `(False, 0)`.
    - Lookup directo coincide → calcular delta.
    - Fallback nivel 2 (priority NORMAL).
    - Fallback nivel 3 (device_type NULL).
    - Compute no muta ticket (snapshot antes/después).
    - _Refs: Req 3.1.3, 3.1.4, 3.2.5, 3.3.2; Properties P9, P10_

- [ ] 14. CRUD y endpoints de `sla_config`
  - [ ] 14.1 Crear `app/crud/sla_config_crud.py`
    - `find_applicable(db, *, state_code, device_type, priority) -> Optional[SLAConfig]` con la cadena de fallback.
    - CRUD básico: `get_by_id`, `list`, `create`, `update`, `soft_delete` (`is_active = False`).
    - _Refs: Req 3.1.3, 3.1.4, 3.1.6_

  - [ ] 14.2 Crear `app/services/sla_config_service.py`
    - Operaciones gobernadas por `user_can(user, CAP_SLA_MANAGE)` para mutaciones y `CAP_SLA_READ` para lecturas.
    - Manejar duplicado por `UNIQUE` con HTTP 400 "Ya existe una configuración para esa combinación (estado, tipo, prioridad)".
    - _Refs: Req 3.1.5, 3.1.6_

  - [ ] 14.3 Crear schemas en `app/schemas/sla_config.py`
    - `SLAConfigBase`, `SLAConfigCreate`, `SLAConfigUpdate`, `SLAConfigRead`.
    - Validaciones: `state_code` 1-32 chars, `device_type` ≤ 20 chars, `priority` Literal, `max_hours` 1-8760.
    - _Refs: Req 3.1.2; Data Models §D_

  - [ ] 14.4 Crear router `app/api/routes/sla_config.py`
    - `APIRouter(prefix="/tickets/sla-config", tags=["sla"])`.
    - `GET /` (list, query opcionales `state_code`, `device_type`, `priority`, `is_active`).
    - `POST /` (201, `SLAConfigRead`).
    - `PUT /{id}` (200, `SLAConfigRead`).
    - `DELETE /{id}` (204, soft delete).
    - _Refs: Req 3.1.5, 3.1.6; Endpoints §2-§5_

  - [ ] 14.5 Registrar router en `app/main.py`
    - `app.include_router(sla_config_router)` con el prefijo correspondiente.
    - _Refs: Req 3.1.6_

  - [ ]* 14.6 Tests integration en `tests/integration/test_sla_config_crud.py`
    - Matriz por capability: ADMIN crea/lee/edita/borra (2xx). ADVISOR lee (200) pero no muta (403). TECHNICIAN/CLIENT (403 en todo).
    - Crear duplicado → 400.
    - Soft delete deja la fila pero `is_active = False` y el listado por defecto la oculta o la muestra según query.
    - _Refs: Req 3.1.5, 3.1.6; Property P14_

- [ ] 15. Integrar SLA en serialización de tickets
  - [ ] 15.1 Llenar `is_overdue` y `overdue_hours` en respuestas
    - En `get_ticket_detail`: invocar `compute_sla(db, ticket)` y poblar `TicketReadDetail`.
    - En `list_tickets_for_user`: idem para cada ticket; cachear `find_applicable` por request en un dict local para evitar lookups repetidos.
    - Enteros truncados (decisión OQ4).
    - _Refs: Req 3.2.1, 3.2.2; Decisión OQ4; Property P9_

  - [ ] 15.2 Llamar `record_breach_if_new` lazy cuando `is_overdue=True`
    - Solo cuando el booleano sale `True` desde `compute_sla`. No mutar el ticket.
    - _Refs: Req 3.3.1, 3.3.3; Property P11_

  - [ ] 15.3 Optimización N+1
    - Cargar `device` y `history` con `joinedload`/`selectinload` en las queries de listado y detalle para evitar N+1.
    - _Refs: Risks and Mitigations §1_

  - [ ]* 15.4 Tests integration en `tests/integration/test_sla_overdue.py`
    - Crear ticket con history simulado (insertar fila vieja).
    - `GET /tickets/{id}` como ADMIN: `is_overdue=true`, `overdue_hours > 0`. Verificar fila en `internal_notification`.
    - Segundo `GET` no duplica notificación (idempotencia P11).
    - Estado terminal → `is_overdue=false`, sin notificación.
    - Destinatarios: estado REPAIRING con assignee → `recipient_user_id`. Estado WAITING_APPROVAL → `recipient_role='ADVISOR'`.
    - _Refs: Req 3.2, 3.3; Decisión OQ3; Properties P9, P11_

### Fase 11 — Filtro 6 meses para CLIENT

- [ ] 16. Implementar filtro temporal por defecto en `list_tickets_for_user`
  - [ ] 16.1 Aplicar `relativedelta(months=6)` para CLIENT sin filtros de fecha
    - `from dateutil.relativedelta import relativedelta` (verificar `python-dateutil==2.8.2` ya en `requirements.txt`).
    - Constante `CLIENT_DEFAULT_WINDOW_MONTHS = 6`.
    - Si `role == ROLE_CLIENT` y `from_date is None and to_date is None`: cutoff = `datetime.utcnow() - relativedelta(months=CLIENT_DEFAULT_WINDOW_MONTHS)`. Mantener tickets cuya `created_at >= cutoff` o cuyo estado no sea terminal.
    - Si vienen `from_date`/`to_date` explícitos, no aplicar el cutoff (Req 5.1.2).
    - _Refs: Req 5.1.1, 5.1.2, 5.1.3; Decisión OQ5; Property P12_

  - [ ] 16.2 Exponer `default_window_months = 6` en `/auth/me`
    - Endpoint ya existe en `app/api/routes/auth.py` (`GET /auth/me`, `response_model=UserReadMinimal`).
    - Añadir el campo `default_window_months: int = 6` al schema de respuesta (o crear schema `MeResponse` que extiende `UserReadMinimal` con la flag) sin romper el contrato existente.
    - Documentar en docstring que es la ventana por defecto del portal cliente.
    - _Refs: Req 5.1.4; Decisión OQ2_

  - [ ]* 16.3 Tests integration en `tests/integration/test_client_window.py`
    - CLIENT con tickets de hace 1 mes y de hace 8 meses. Sin filtros: solo aparece el de 1 mes (más el ticket activo de 8 meses si su estado no es terminal). Con `from_date` explícito de hace 12 meses: aparecen ambos.
    - `GET /auth/me` devuelve `default_window_months = 6`.
    - Aserción del cálculo calendario: ticket creado exactamente hace 6 meses (con `relativedelta`) sigue dentro; un día antes no.
    - _Refs: Req 5.1; Decisiones OQ2, OQ5; Property P12_

### Fase 12 — Property tests

- [ ] 17. Suite de property tests
  - [ ] 17.1 Estrategias compartidas en `tests/property/strategies.py`
    - `state_codes`, `roles`, `priorities`, `device_types`, `sla_config_rows`.
    - _Refs: Testing Strategy §Property_

  - [ ]* 17.2 Properties P1, P2, P3, P4, P8, P9, P10, P11, P12, P13, P14 en `tests/property/test_invariants.py`
    - Cada test con docstring `Feature: tickets-flow-consolidation, Property N: <texto>`.
    - Anotar property number y requisitos validados.
    - `@settings(max_examples=100)` mínimo; 200 para P1 y P9 (críticas).
    - **Nota:** P5 vive en `tests/integration/test_claim_endpoint.py` (Hypothesis genera (rol, estado, assignee)). P6 y P7 viven en los tests de concurrencia ya planificados (T10.6, T11.4).
    - _Refs: Properties P1–P14; Testing Strategy_

### Fase 13 — CI y verificación final

- [ ] 18. Verificación final
  - [ ] 18.1 Lint y formato
    - `ruff check app/ tests/ alembic/` sin errores.
    - _Refs: testing.md §CI_

  - [ ] 18.2 Tests
    - `pytest tests/ -q --cov=app --cov-report=term-missing`. Cobertura objetivo: services ≥ 85%, `app/core/permissions.py` = 100%.
    - _Refs: testing.md §CI; Cobertura esperada_

  - [ ] 18.3 Bytecode
    - `python -m compileall app/ tests/ alembic/` para detectar errores sintácticos.
    - _Refs: backend-conventions.md_

  - [ ] 18.4 Push y validación de CI
    - Push de la rama y validar que el workflow `backend-ci` queda verde.
    - _Refs: testing.md §CI; git-workflow.md_

- [ ] 19. Checkpoint final
  - Asegurar todos los tests verdes (60 existentes + nuevos), las tres migraciones aplicadas y reversibles, los endpoints nuevos respondiendo y los TODOs anclados (`# TODO(notify)`, `# TODO(carga-tecnico)`, `# TODO(sla-tuning)`, `# TODO(rbac-fine-grained-permissions)`). Preguntar al usuario si surgen dudas antes del merge.
  - _Refs: Req 1.3; Restricciones de alcance_

- [ ]* 20. Documentación breve para el frontend (opcional, no bloqueante)
  - Listar los nuevos campos de respuesta (`priority`, `is_overdue`, `overdue_hours`) y el nuevo endpoint (`POST /tickets/{id}/claim`, `*/sla-config/*`), además del nuevo 409 posible en `PATCH /tickets/{id}/assign`.
  - Indicar que `/auth/me` ahora incluye `default_window_months`.
  - Archivo sugerido: `docs/api-changes-tickets-flow-consolidation.md`.
  - _Refs: Rollout Strategy §2_

## Notes

- Las sub-tareas marcadas con `*` después del checkbox (`- [ ]*`) son opcionales: tests adicionales, documentación complementaria. El núcleo de implementación se ejecuta sin ellas.
- Cada bloque referencia los requisitos y, cuando aplica, las propiedades del design (P1–P14).
- Los checkpoints (T7, T19) son intencionalmente pausa para correr la suite y validar antes de seguir.
- La separación entre Fase 4 (refactor de la fachada) y Fases 5/6 (validaciones específicas) es deliberada: T6 entrega la fachada operativa con la matriz básica; T8/T9 atornillan las reglas finas (reopen_reason, capability) sobre esa misma fachada sin reabrirla.
- El orden respeta dependencias: migraciones → modelos → fachada de permisos → corrección de visibilidad → fachada de transición → reglas finas → claim/reasign con concurrencia → SLA → ventana 6m → property tests → CI.
- El refactor mantiene contratos API: solo se añaden campos y un nuevo 409 (race en `assign`/`claim`). El frontend sigue funcionando sin cambios obligatorios.
