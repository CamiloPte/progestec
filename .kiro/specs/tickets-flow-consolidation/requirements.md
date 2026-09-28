# Requirements Document — Consolidación del flujo de tickets

## Introducción

ProGesTec ya implementa el ciclo de vida del ticket de servicio técnico al ~90%. Este spec **no crea funcionalidad nueva de cero**: consolida lo existente para cerrar tres frentes que hoy quedan inconsistentes:

1. **Validación uniforme de transiciones de estado** en todos los endpoints que modifican el campo `status_id` (no solo en `PUT /tickets/{id}`).
2. **Auto-asignación segura del técnico** sobre tickets sin asignar, con manejo explícito de carrera.
3. **SLAs y tiempos esperados por estado**, con visibilidad en el dashboard.
4. **Vistas filtradas por rol** revisadas y documentadas (qué ve cada rol y por cuánto tiempo).

El alcance **no incluye** implementar el envío de emails (eso queda en el spec de notificaciones, ya tiene los `TODO(notify)` anclados) ni rediseñar el modelo de datos más allá de los campos mínimos necesarios para SLA y concurrencia.

Las decisiones que afectan persistencia se listan en la sección **Decisiones pendientes** y deben confirmarse antes de pasar a diseño.

## Glosario

- **Sistema**: la API ProGesTec en su conjunto (FastAPI + MySQL).
- **Servicio_Tickets**: módulo `app/services/ticket_service.py` y endpoints en `app/api/routes/ticket.py`.
- **Validador_Transiciones**: módulo `app/core/ticket_status_transitions.py` con `is_valid_transition` y `get_allowed_transitions`.
- **Visibilidad_Estados**: módulo `app/core/ticket_status_visibility.py` con `STATUS_VISIBILITY_BY_ROLE`.
- **Servicio_Notificaciones**: módulo `app/services/ticket_notification_service.py` (envíos asíncronos por email).
- **Ticket**: instancia de `app.models.ticket.Ticket`.
- **Estado del ticket**: valor textual del código `RECEIVED | DIAGNOSING | WAITING_APPROVAL | REPAIRING | READY | DELIVERED | CLOSED | CANCELLED`.
- **Auto_Asignación**: operación por la cual un usuario con rol TECHNICIAN se asigna a sí mismo un ticket cuyo `assignee_user_id` es `NULL`.
- **SLA**: límite de tiempo esperado de permanencia de un ticket en un estado, configurable a nivel de sistema.
- **Ticket vencido**: ticket cuyo tiempo en su estado actual supera el SLA configurado para ese estado.
- **Roles**: códigos definidos en `app/core/roles.py` (`ADMIN`, `ADVISOR`, `TECHNICIAN`, `CLIENT`, `COURIER`).

## Requisitos

Los requisitos se agrupan por área. Las user stories están redactadas desde el rol que origina la necesidad. Los criterios de aceptación usan EARS (`WHEN`, `WHILE`, `IF...THEN`, `WHERE`, `THE ... SHALL`).

---

### Área 1 — Validación uniforme de transiciones de estado

#### Requisito 1.1: Validación centralizada en todos los endpoints

**User Story:** Como ADMIN, quiero que ningún endpoint pueda saltarse la tabla de transiciones, para garantizar que el flujo de estados sea íntegro independientemente de por dónde entre la petición.

##### Criterios de aceptación

1. WHEN un endpoint modifica el campo `status_id` de un Ticket, THE Servicio_Tickets SHALL invocar `Validador_Transiciones.is_valid_transition(estado_actual, estado_nuevo, rol_usuario)` antes de persistir el cambio.
2. IF `Validador_Transiciones.is_valid_transition` retorna `(False, mensaje)`, THEN THE Servicio_Tickets SHALL responder con HTTP 400 y el mensaje devuelto, sin alterar la base de datos.
3. THE Servicio_Tickets SHALL registrar una entrada en `ticket_history` por cada transición de estado aceptada, con `user_id` del actor, `status_id` destino y `note` descriptiva.
4. WHEN una transición de estado se acepta, THE Servicio_Tickets SHALL actualizar los timestamps correspondientes (`ready_at` al pasar a READY, `delivered_at` al pasar a DELIVERED, `closed_at` al pasar a CLOSED o CANCELLED).
5. IF un endpoint dedicado (por ejemplo `/tickets/{id}/quote-response`, `/tickets/{id}/assign`) requiere cambiar de estado, THEN THE Servicio_Tickets SHALL reutilizar la misma ruta de validación de `update_ticket` o un helper compartido equivalente, en lugar de mutar `status_id` directamente.

#### Requisito 1.2: Inventario de endpoints que afectan el estado

**User Story:** Como ADMIN, quiero un inventario explícito de todos los endpoints que pueden cambiar el estado de un ticket, para no volver a tener rutas que se salten la validación.

##### Criterios de aceptación

1. THE Servicio_Tickets SHALL exponer una sola función pública (`transition_status` o equivalente) que sea la única vía para mutar `status_id`.
2. WHEN se introduzca un nuevo endpoint que toque estado, THE Servicio_Tickets SHALL invocar dicha función o ser bloqueado por test de regresión.
3. THE documentación interna de `app/services/ticket_service.py` SHALL listar en su docstring de módulo los endpoints actuales que modifican estado (al cierre de este spec: `PUT /tickets/{id}`, `PATCH /tickets/{id}/assign`, `PATCH /tickets/{id}/quote-response`, y los que se introduzcan en este spec).

#### Requisito 1.3: Compatibilidad con tests existentes

**User Story:** Como mantenedor, quiero que los 60 tests actuales de transiciones sigan pasando tras la consolidación, para no introducir regresiones silenciosas.

##### Criterios de aceptación

1. THE Sistema SHALL conservar la firma y el comportamiento documentado de `is_valid_transition(current, new, role_name)` y `get_allowed_transitions(current, role_name)`.
2. THE Sistema SHALL conservar la semántica de `ROLE_ALLOWED_FROM` para CLIENT (solo desde WAITING_APPROVAL hacia REPAIRING o CANCELLED).
3. WHEN se ejecute `pytest tests/unit/core/test_ticket_status_transitions.py`, THE Sistema SHALL pasar los 60 tests sin modificación.

---

### Área 2 — Auto-asignación de técnicos

#### Requisito 2.1: Tomar un ticket sin asignar

**User Story:** Como TECHNICIAN, quiero poder tomar un ticket sin asignar para empezar a trabajarlo, sin tener que pedir al asesor que me lo asigne.

##### Criterios de aceptación

1. THE Servicio_Tickets SHALL exponer una operación `claim_ticket(ticket_id, user)` accesible vía endpoint REST (sugerido: `POST /tickets/{id}/claim`).
2. WHEN un usuario con rol TECHNICIAN invoca `claim_ticket` sobre un Ticket cuyo `assignee_user_id IS NULL` y cuyo estado pertenece a `{RECEIVED, DIAGNOSING}`, THE Servicio_Tickets SHALL asignar `assignee_user_id` al `id` del usuario y registrar entrada en `ticket_history`.
3. IF un usuario sin rol TECHNICIAN invoca `claim_ticket`, THEN THE Servicio_Tickets SHALL responder HTTP 403.
4. IF el Ticket ya tiene `assignee_user_id` distinto de `NULL`, THEN THE Servicio_Tickets SHALL responder HTTP 409 (Conflict) con mensaje "El ticket ya fue tomado por otro técnico".
5. IF el Ticket está en un estado fuera de `{RECEIVED, DIAGNOSING}`, THEN THE Servicio_Tickets SHALL responder HTTP 400 con mensaje indicando que solo se pueden tomar tickets en recepción o diagnóstico.
6. WHEN `claim_ticket` se completa con éxito, THE Sistema SHALL devolver el `TicketReadDetail` actualizado, idéntico al que devolvería un `GET /tickets/{id}` posterior.

#### Requisito 2.2: Concurrencia segura (lock optimista)

**User Story:** Como ADMIN, quiero que si dos técnicos hacen click simultáneamente en "tomar este ticket", solo uno gane y el otro reciba un error claro, para evitar pisar asignaciones.

##### Criterios de aceptación

1. WHEN dos invocaciones concurrentes de `claim_ticket` actúan sobre el mismo Ticket, THE Servicio_Tickets SHALL garantizar que solo una de ellas asigne al técnico exitosamente.
2. THE Servicio_Tickets SHALL implementar la asignación con un `UPDATE ... WHERE id = :id AND assignee_user_id IS NULL` y verificar que el número de filas afectadas sea `1`.
3. IF el `UPDATE` afecta `0` filas, THEN THE Servicio_Tickets SHALL responder HTTP 409 con mensaje "El ticket ya fue tomado por otro técnico".
4. THE Servicio_Tickets SHALL ejecutar la asignación dentro de una transacción que también registre la entrada en `ticket_history`, de forma que no haya estados intermedios visibles en la base.

#### Requisito 2.3: Devolver un ticket tomado

**User Story:** Como TECHNICIAN, quiero poder devolver un ticket que tomé si me doy cuenta de que requiere otra especialidad, para no bloquearlo.

> **Decisión D1 (cerrada):** El técnico SOLO puede devolver el ticket mientras esté en `{RECEIVED, DIAGNOSING}` y mientras él sea el `assignee_user_id` actual. Una vez en `WAITING_APPROVAL`, `REPAIRING` o posteriores, ya está comprometido (envió cotización, inició reparación) y la reasignación pasa a ser responsabilidad de ADMIN o ADVISOR.

##### Criterios de aceptación

1. WHEN un usuario con rol TECHNICIAN actualiza su propio Ticket asignado fijando `assignee_user_id = null` y el estado actual está en `{RECEIVED, DIAGNOSING}`, THE Servicio_Tickets SHALL aceptar la operación y dejar el Ticket sin asignar.
2. IF el estado actual está fuera de `{RECEIVED, DIAGNOSING}`, THEN THE Servicio_Tickets SHALL responder HTTP 400 con el mensaje ya implementado: "Solo puedes quitarte la asignación en estado Recibido o En diagnóstico".
3. WHEN un TECHNICIAN devuelve un Ticket, THE Servicio_Tickets SHALL registrar entrada en `ticket_history` con la nota "Técnico {nombre} liberó el ticket".

#### Requisito 2.4: Reasignación tras inicio de reparación

**User Story:** Como ADMIN/ADVISOR, quiero poder reasignar un ticket aunque ya esté en REPAIRING (vacaciones, baja, sobrecarga).

> **Decisión D4 (cerrada):** ADMIN y ADVISOR pueden cambiar el `assignee_user_id` en cualquier estado activo (no terminal). El cambio NO modifica el estado del ticket.

##### Criterios de aceptación

1. WHERE el rol del actor es ADMIN o ADVISOR, THE Servicio_Tickets SHALL permitir modificar `assignee_user_id` mientras el estado del ticket no sea `CLOSED` ni `CANCELLED`.
2. WHEN un ADMIN o ADVISOR reasigna un Ticket, THE Servicio_Tickets SHALL registrar entrada en `ticket_history` con la nota "Reasignado de {técnico_anterior} a {técnico_nuevo} por {actor}".
3. IF el `assignee_user_id` propuesto no corresponde a un usuario con rol TECHNICIAN, THEN THE Servicio_Tickets SHALL responder HTTP 400 (comportamiento ya existente).

#### Requisito 2.5: Carga por técnico y puntos de control para futuro límite

**User Story:** Como ADMIN, quiero ver la carga de tickets por técnico para no saturar a ninguno, y dejar preparados los puntos donde a futuro se imponga un límite duro.

> **Decisión D5 (cerrada):** En V1 **no hay límite duro**, solo visualización en dashboard. Sin embargo, los puntos donde se aplicaría un límite (`claim_ticket` y reasignación manual) deben quedar identificados con un `# TODO(carga-tecnico)` para que el control se conecte sin reescribir lógica.

##### Criterios de aceptación

1. THE Servicio_Tickets SHALL exponer en el dashboard la cantidad de tickets activos asignados a cada TECHNICIAN, segmentada por estado.
2. THE código de `claim_ticket` y de la reasignación manual SHALL marcar con comentario `# TODO(carga-tecnico): aplicar límite por usuario` el lugar exacto donde a futuro se valida el tope.
3. WHERE en una iteración futura se decida activar el límite, THE Servicio_Tickets SHALL bloquear con HTTP 409 y mensaje "Técnico al límite de tickets activos".

---

### Área 3 — SLAs y tiempos esperados

#### Requisito 3.1: Configuración de SLA por estado, tipo de equipo y prioridad — administrable desde panel admin

**User Story:** Como ADMIN del taller, quiero ajustar los tiempos esperados (SLA) **sin pedirle al desarrollador que toque código**, porque mi taller maneja sus propios tiempos y deben ser flexibles.

> **Decisión D6 (cerrada):** El SLA es función de tres dimensiones: `(estado, tipo_equipo, prioridad)`. La configuración vive **en base de datos**, no en código. El admin la administra desde un panel.
>
> **Estado del modelo actual** (verificado leyendo `app/models/`):
> - `device.type` ya existe (`PHONE | LAPTOP | TABLET | OTHER`). ✅ No se toca.
> - `tickets.priority` **no existe**. Se agregará como columna nueva.
> - Tabla `sla_config` **no existe**. Se creará.
>
> **Para el piloto**: la pantalla admin de SLA quedará accesible al rol que tenga el permiso `sla.manage` (ver dependencia con spec `rbac-fine-grained-permissions`).

##### Criterios de aceptación

1. THE modelo `Ticket` SHALL incluir un campo `priority` tipo enum (`LOW | NORMAL | HIGH | URGENT`) con default `NORMAL`. Migración Alembic señalizada en el design.
2. THE Sistema SHALL crear una tabla `sla_config` con columnas `(id, state_code, device_type, priority, max_hours, is_active, created_at, updated_at)`. Clave única compuesta: `(state_code, device_type, priority)`. Migración Alembic señalizada en el design.
3. WHEN se calcule el SLA aplicable a un Ticket, THE Sistema SHALL buscar la fila de `sla_config` activa que coincida con `(estado_actual, device.type, priority)`.
4. IF no existe fila exacta para esa combinación, THEN THE Sistema SHALL hacer fallback en este orden: misma `(estado, tipo)` con priority `NORMAL` → mismo `(estado)` con `device_type` NULL y priority `NORMAL` → sin SLA aplicable (Ticket nunca vencido por ese estado).
5. THE Sistema SHALL exponer la configuración vigente en `GET /tickets/sla-config` accesible por usuarios con permiso `sla.read` (por defecto: ADMIN, ADVISOR).
6. THE Sistema SHALL exponer endpoints CRUD para administrar la configuración:
   - `POST /tickets/sla-config` (crear o actualizar una entrada).
   - `PUT /tickets/sla-config/{id}` (modificar).
   - `DELETE /tickets/sla-config/{id}` (desactivar, soft delete).
   - Todos requieren permiso `sla.manage` (por defecto: ROOT y ADMIN; ADVISOR no por defecto).
7. THE Sistema SHALL incluir valores iniciales placeholder vía migración seed con `# TODO(sla-tuning)`. Estos valores son el punto de partida del piloto y se ajustan desde el panel admin con datos reales.
8. THE pantalla admin de gestión de SLA (frontend) queda **fuera del alcance de este spec backend**, pero los endpoints quedan listos para que la pantalla los consuma.

#### Requisito 3.2: Detección de tickets vencidos

**User Story:** Como ADVISOR, quiero ver claramente qué tickets están vencidos y por cuánto, para priorizarlos.

##### Criterios de aceptación

1. THE Servicio_Tickets SHALL calcular para cada Ticket activo dos campos derivados: `is_overdue: bool` y `overdue_hours: int` (0 si no está vencido).
2. WHEN el `TicketReadMinimal` o `TicketReadDetail` se serialice para ADMIN, ADVISOR o TECHNICIAN, THE Servicio_Tickets SHALL incluir `is_overdue` y `overdue_hours`.
3. THE Sistema SHALL exponer en el dashboard un contador de tickets vencidos por estado y por técnico asignado.
4. IF un Ticket está en estado terminal (`CLOSED`, `CANCELLED`), THEN THE Sistema SHALL reportar `is_overdue = false`.
5. THE cálculo de `overdue_hours` SHALL usar la diferencia entre `now()` y la fecha de la última entrada en `ticket_history` correspondiente al estado actual del ticket, comparada contra el SLA del Requisito 3.1.

#### Requisito 3.3: Visualización + notificación interna a ADMIN/ADVISOR

**User Story:** Como ADMIN/ADVISOR, quiero enterarme cuando un ticket cruza su SLA sin tener que estar mirando el dashboard.

> **Decisión D7 (cerrada):** Combinación de visualización (opción 1) y notificación interna (opción 2). Sin escalado automático ni cambio de estado en V1.

##### Criterios de aceptación

1. WHEN un Ticket cruza el umbral de SLA, THE Sistema SHALL marcarlo como `is_overdue = true` en respuestas API y dashboard.
2. THE Sistema SHALL **no** modificar `status_id`, `assignee_user_id` ni ningún otro campo del Ticket por causa del vencimiento.
3. WHEN un Ticket pasa de `is_overdue = false` a `is_overdue = true`, THE Sistema SHALL registrar una entrada en una tabla `internal_notification` (o equivalente) dirigida a ADMIN y ADVISOR, con motivo `SLA_BREACH`. El consumo (visual en panel, eventual email) queda fuera de alcance de este spec — solo se garantiza el registro.
4. THE Sistema SHALL evitar registros duplicados: una notificación `SLA_BREACH` por `(ticket_id, state_code, breach_at)` única.
5. THE Sistema SHALL **no** disparar emails al cliente derivados del vencimiento de SLA en V1 (ese gancho queda para spec posterior).

---

### Área 4 — Vistas filtradas por rol

#### Requisito 4.1: ADMIN ve todo

**User Story:** Como ADMIN, quiero ver cualquier ticket en cualquier estado, para tener supervisión total.

##### Criterios de aceptación

1. THE Servicio_Tickets SHALL devolver, en `list_tickets_for_user`, todos los tickets activos (`state = 1`) cuando el rol del actor sea ADMIN.
2. THE Servicio_Tickets SHALL permitir a ADMIN aplicar cualquier filtro de la query (`status`, `assigned`, `from_date`, `to_date`, `search`, `device_type`).

#### Requisito 4.2: ADVISOR ve todo (operativo)

**User Story:** Como ADVISOR, quiero ver todos los tickets activos para gestionarlos operativamente.

##### Criterios de aceptación

1. THE Servicio_Tickets SHALL devolver a ADVISOR los mismos tickets que a ADMIN.
2. THE Servicio_Tickets SHALL permitir a ADVISOR los mismos filtros que a ADMIN.

#### Requisito 4.3: TECHNICIAN ve sus tickets y los disponibles

**User Story:** Como TECHNICIAN, quiero ver tanto mis tickets asignados como los que están sin asignar, para poder tomarlos.

##### Criterios de aceptación

1. THE Servicio_Tickets SHALL devolver a TECHNICIAN los Tickets cuyo `assignee_user_id` sea `current_user.id` o `NULL`.
2. THE Servicio_Tickets SHALL filtrar los estados visibles a TECHNICIAN según `STATUS_VISIBILITY_BY_ROLE[ROLE_TECHNICIAN]` (es decir: `RECEIVED`, `DIAGNOSING`, `WAITING_APPROVAL`, `REPAIRING`, `READY`).
3. THE Servicio_Tickets SHALL aceptar los filtros `assigned=me`, `assigned=unassigned`, `assigned=all` y respetar la restricción del criterio 1.

#### Requisito 4.4: CLIENT ve solo los suyos, en cualquier estado de su flujo

**User Story:** Como CLIENT, quiero ver solamente los tickets de los dispositivos a mi nombre, en todos los estados del ciclo de vida.

> **Decisión D2 (cerrada):** Se corrige la inconsistencia detectada en `STATUS_VISIBILITY_BY_ROLE[ROLE_CLIENT]`. La lista debe incluir **todos los estados** (`RECEIVED`, `DIAGNOSING`, `WAITING_APPROVAL`, `REPAIRING`, `READY`, `DELIVERED`, `CLOSED`, `CANCELLED`). La restricción real para CLIENT es de **propiedad** (`device.owner_user_id`), no de estado.

##### Criterios de aceptación

1. THE Servicio_Tickets SHALL devolver a CLIENT solo los Tickets en los que `device.owner_user_id == current_user.id`.
2. THE constante `STATUS_VISIBILITY_BY_ROLE[ROLE_CLIENT]` SHALL contener todos los estados del flujo. La filtración por estado para CLIENT queda manejada por filtros de query (`status=`), no por restricción dura.
3. THE Servicio_Tickets SHALL respetar adicionalmente el corte temporal del Requisito 5.1 (6 meses por defecto).

#### Requisito 4.4-bis: Auto-aprobación del presupuesto por personal interno autorizado

**User Story:** Como ADVISOR, ADMIN, o TECHNICIAN autorizado, quiero poder aprobar la cotización en nombre del cliente cuando éste no tiene acceso al portal o autoriza por otro canal (teléfono, presencial), para no atascar el flujo. En el piloto, el dueño del taller suele ejercer ambos roles (técnico y asesor), y debe poder operar la aprobación.

> **Decisión D2 (cerrada):** La capacidad de auto-aprobar la cotización **no se ata directamente al rol** sino a un permiso fino llamado `tickets.approve_quote`. Por defecto:
>
> - `ADMIN` y `ADVISOR` tienen el permiso por su rol.
> - `TECHNICIAN` no lo tiene por defecto, pero el `ROOT`/`ADMIN` puede otorgárselo a usuarios técnicos específicos (caso del piloto: dueño-técnico que también ejerce como asesor).
> - `CLIENT` aprueba como acción nativa (no requiere el permiso, es la transición del propio cliente).
>
> El **sistema de permisos finos** (tabla `permissions`, `user_permissions`, jerarquía `ROOT` ↔ `ADMIN`) se diseña en el spec dedicado **`rbac-fine-grained-permissions`** (a crear). En este spec se asume su existencia conceptual y se prepara el código para consultarlo:
>
> - Si el spec de RBAC fino aún no está implementado al codear este, se usará un fallback temporal: `tickets.approve_quote` se considera "concedido" si el rol del actor es `ADMIN` o `ADVISOR`. El TECHNICIAN no podrá auto-aprobar hasta que aterrice el spec de RBAC.
> - El código que verifica el permiso se centralizará en una función `user_can(user, "tickets.approve_quote")` para que el cambio sea de un solo punto cuando llegue el RBAC fino.

##### Criterios de aceptación

1. WHEN un usuario ejecuta la transición `WAITING_APPROVAL → REPAIRING` o `WAITING_APPROVAL → CANCELLED`, THE Servicio_Tickets SHALL aceptar la operación si y solo si:
   - El usuario es `CLIENT` propietario del dispositivo del ticket, **o**
   - El usuario tiene el permiso `tickets.approve_quote` (vía rol o vía permiso individual).
2. THE Servicio_Tickets SHALL invocar `user_can(user, "tickets.approve_quote")` para resolver la autorización en el caso no-cliente. La función actuará como fachada: hoy retorna `True` si el rol es `ADMIN` o `ADVISOR`; cuando exista `rbac-fine-grained-permissions`, consultará la tabla de permisos.
3. THE entrada de `ticket_history` correspondiente SHALL contener una nota distinguible:
   - Si el actor es `CLIENT`: `"Cliente {nombre} aprobó/rechazó el presupuesto"`.
   - Si el actor es personal interno: `"Auto-aprobado por {rol} {nombre} en nombre del cliente"` (o `"Auto-rechazado..."`).
4. THE schema `TicketUpdate` y la operación de transición SHALL aceptar un campo opcional `acted_on_behalf_of_client: bool` que, cuando es `true`, fuerza el formato de nota anterior. Si es `false` o ausente y el actor no es CLIENT, se asume implícitamente `true`.
5. IF un usuario sin el permiso intenta esta transición, THEN THE Servicio_Tickets SHALL responder HTTP 403 con mensaje "No tienes permiso para aprobar cotizaciones en nombre del cliente".

#### Requisito 4.5: COURIER fuera de alcance en este spec

**User Story:** Como ADMIN, quiero entender el flujo de COURIER, pero sé que no está completo y debe revisarse aparte.

> **Decisión D8 (cerrada):** El módulo de domiciliario (`delivery_order`) no está completo y requiere una reestructuración previa. **Queda fuera del alcance de este spec.** Los tickets en estado `READY` y `DELIVERED` siguen siendo gestionados por ADVISOR en V1. Cuando se aborde el spec del módulo de domiciliario, se revisitará la matriz de transiciones y permisos para incluir a COURIER.

##### Criterios de aceptación

1. THE Sistema SHALL conservar el comportamiento actual de COURIER (lo que sea que esté hoy) sin cambios funcionales en este spec.
2. THE Servicio_Tickets SHALL **no** introducir nuevos endpoints, transiciones ni validaciones para COURIER en este spec.
3. THE backlog de specs SHALL contener una entrada `delivery-flow-rework` (a crear) que abordará el módulo en su totalidad.

---

### Área 5 — Visibilidad histórica para CLIENT

#### Requisito 5.1: Filtro por defecto de 6 meses para CLIENT

**User Story:** Como CLIENT, quiero ver mi historial reciente sin verme inundado por tickets viejos, pero con la opción de ver el historial completo si lo necesito.

> **Decisión D3 (cerrada):** El portal del cliente muestra por defecto los tickets de los últimos **6 meses**. Tickets más antiguos están disponibles vía filtro explícito de fecha o vista "Historial completo".

##### Criterios de aceptación

1. WHEN un CLIENT solicita `GET /tickets/` sin filtros explícitos de fecha, THE Servicio_Tickets SHALL devolver los Tickets cuyo `created_at >= now() - 6 months` o cuyo estado no sea terminal (`CLOSED`/`CANCELLED`).
2. WHERE el CLIENT pase explícitamente `from_date` y/o `to_date`, THE Servicio_Tickets SHALL respetar el rango sin aplicar el límite por defecto.
3. THE Servicio_Tickets SHALL incluir tickets `CANCELLED` en la respuesta a CLIENT salvo que se filtre explícitamente lo contrario.
4. THE Sistema SHALL exponer al frontend la flag `default_window_months = 6` en el endpoint de configuración pública del cliente, para que el portal muestre el corte vigente.

### Área 6 — Reapertura por ADMIN con motivo obligatorio

#### Requisito 6.1: Motivo obligatorio en reapertura

**User Story:** Como ADMIN, cuando reabra un ticket cerrado o cancelado, debo justificarlo con un motivo claro para dejar trazabilidad de la decisión.

> **Decisión D9 (cerrada):** La transición `CLOSED → RECEIVED` o `CANCELLED → RECEIVED` (permitida solo a ADMIN según `ADMIN_ONLY_TRANSITIONS`) requiere un campo `reopen_reason` con mínimo 10 caracteres.

##### Criterios de aceptación

1. WHEN un ADMIN solicita una transición desde estado terminal a `RECEIVED`, THE Servicio_Tickets SHALL exigir un campo `reopen_reason: str` en el payload.
2. IF `reopen_reason` está ausente o tiene longitud menor a 10 caracteres, THEN THE Servicio_Tickets SHALL responder HTTP 400 con mensaje "Debes indicar un motivo de reapertura de al menos 10 caracteres".
3. WHEN la reapertura se acepta, THE Servicio_Tickets SHALL guardar el `reopen_reason` en el campo `note` de `ticket_history`, con prefijo `"Reapertura por {nombre admin}: "`.
4. THE schema `TicketUpdate` SHALL aceptar `reopen_reason` como campo opcional. La validación de obligatoriedad se hace en el service en función del par `(estado_actual, estado_destino)`.

### Área 7 — Concurrencia: criterios para elegir lock

#### Requisito 7.1: Mapa de operaciones y estrategia de lock

**User Story:** Como mantenedor del backend, quiero un criterio claro de cuándo usar lock optimista y cuándo pesimista, para no decidir caso por caso.

> **Decisión D10 (cerrada):** Las dos estrategias coexisten. Cada operación crítica se documenta con su elección y razón.

##### Criterios de aceptación

1. THE design del refactor SHALL incluir una sección "Estrategia de concurrencia" con una tabla `operación → estrategia → razón`.
2. THE operación `claim_ticket` SHALL usar lock optimista (`UPDATE ... WHERE assignee_user_id IS NULL`) y verificar `rowcount == 1` (ver Requisito 2.2).
3. THE operación de reasignación manual por ADMIN/ADVISOR SHALL usar lock optimista equivalente: `UPDATE ... WHERE assignee_user_id = :expected_old_id` con verificación de rowcount.
4. WHEN una operación deba mutar más de una tabla en una transacción crítica (ejemplos potenciales: cierre de ticket que descuenta stock + emite factura), THE diseño SHALL evaluar lock pesimista (`SELECT ... FOR UPDATE`). Esa decisión queda fuera del alcance de este spec, pero el criterio queda asentado aquí.
5. THE comentario `# CONCURRENCY: <estrategia> — <razón>` SHALL acompañar cada bloque de código que aplique lock explícito.

---

## Propiedades de correctitud (invariantes)

Estas propiedades son la base para los tests property-based del módulo (alineado con `.kiro/steering/testing.md`). Deben mantenerse para **toda** entrada generada.

### P1. Conservación del flujo

> Para todo Ticket `t` y toda secuencia de operaciones legales `ops`, el `status` final de `t` corresponde a un estado alcanzable desde el inicial siguiendo aristas de `VALID_TRANSITIONS ∪ ADMIN_ONLY_TRANSITIONS`.

### P2. Coherencia entre `is_valid_transition` y `get_allowed_transitions`

> Para todo `(estado_actual, estado_nuevo, rol)`, `is_valid_transition(estado_actual, estado_nuevo, rol)[0] == True` si y solo si `estado_nuevo in get_allowed_transitions(estado_actual, rol)` o `estado_nuevo == estado_actual`.

### P3. Identidad reflexiva

> Para todo `(estado, rol)`, `is_valid_transition(estado, estado, rol) == (True, "")`. (Cambiar a sí mismo siempre es válido y no requiere registro en historia.)

### P4. CLIENT solo desde WAITING_APPROVAL

> Para todo `estado != "WAITING_APPROVAL"` y todo `nuevo`, `is_valid_transition(estado, nuevo, "CLIENT")[0] == False`.

### P5. Estados terminales son absorbentes (excepto admin)

> Para todo `nuevo` y todo `rol != "ADMIN"`, `is_valid_transition("CLOSED", nuevo, rol)[0] == False` y `is_valid_transition("CANCELLED", nuevo, rol)[0] == False`.

### P6. Auto-asignación es exclusiva (no reasignación encubierta)

> Para todo Ticket `t`, si `claim_ticket(t.id, user_a)` retorna éxito, entonces para todo `user_b ≠ user_a` ejecutado de forma concurrente, `claim_ticket(t.id, user_b)` retorna HTTP 409.

### P7. Idempotencia del registro de historia

> Para toda transición aceptada, exactamente **una** fila se inserta en `ticket_history` con `(ticket_id, status_id, user_id, created_at)` correspondientes al evento. Reintentos de la misma operación que no cambian el estado no insertan filas duplicadas (ver D9).

### P8. Soft delete y visibilidad

> Para todo Ticket `t` con `t.state != 1`, `list_tickets_for_user(...)` no incluye `t` para ningún rol.

### P9. SLA es derivado, no persistido

> Para todo Ticket `t`, `is_overdue(t)` se calcula a partir de `ticket_history` y `SLA_BY_STATUS`. Cambios en `SLA_BY_STATUS` afectan la respuesta de inmediato sin migración de datos.

### P10. Visibilidad por estado y por propiedad son independientes

> Para CLIENT, un Ticket es visible si y solo si: `device.owner_user_id == current_user.id` **AND** `status.code in STATUS_VISIBILITY_BY_ROLE[ROLE_CLIENT]`. Quitar uno solo de los dos no es suficiente.

---

## Restricciones de alcance

- **No incluido**: implementación de envío de email; los `TODO(notify)` siguen anclados, este spec no los desbloquea.
- **No incluido**: rediseño profundo del modelo `delivery_order`. Solo se referencia para vista de COURIER.
- **No incluido**: notificaciones push, webhooks, multi-tenant.
- **Compatibilidad obligatoria**: los 60 tests de `tests/unit/core/test_ticket_status_transitions.py` deben seguir verdes sin cambios.
- **API pública**: cualquier cambio que rompa contrato (status code, payload) en endpoints existentes (`GET/POST/PUT /tickets`, `PATCH /tickets/{id}/assign`, `PATCH /tickets/{id}/quote-response`) debe quedar listado en el `design.md` como cambio intencional.
- **Migraciones**: si se introducen columnas para SLA o concurrencia, deben quedar señalizadas como TODO de migración Alembic en el `design.md`. Esta spec no decide migraciones.

---

## Decisiones cerradas

Todas las zonas grises identificadas en la fase de descubrimiento se resolvieron. Se documentan aquí con su decisión final para referencia futura.

| ID | Tema | Decisión |
|----|------|----------|
| D1 | Devolución por TECHNICIAN | Solo en `RECEIVED` y `DIAGNOSING`. Después, requiere ADMIN/ADVISOR. |
| D2 | Visibilidad CLIENT y auto-aprobación | CLIENT ve todos los estados de su flujo (corregir `STATUS_VISIBILITY_BY_ROLE`). La auto-aprobación se ata al permiso `tickets.approve_quote`, no al rol. ADMIN/ADVISOR lo tienen por defecto; TECHNICIAN puede recibirlo individualmente vía spec `rbac-fine-grained-permissions`. Fallback temporal: `True` si rol es ADMIN o ADVISOR. |
| D3 | Corte temporal en portal cliente | 6 meses por defecto, con filtro explícito para historial completo. |
| D4 | Reasignación tras inicio | ADMIN y ADVISOR pueden reasignar en cualquier estado no terminal. |
| D5 | Límite por técnico | Sin límite duro en V1. Solo dashboard con carga. Puntos de control marcados con `# TODO(carga-tecnico)`. |
| D6 | SLA dimensiones | Por estado × tipo de equipo × prioridad. Tabla `sla_config` administrable desde panel admin (no hardcoded). Endpoints CRUD protegidos por permiso `sla.manage`. |
| D7 | Consecuencia de vencimiento | Visualización + notificación interna a ADMIN/ADVISOR (registro en `internal_notification`). Sin escalado automático ni email al cliente. |
| D8 | Módulo domiciliario | Fuera de alcance. Spec dedicado pendiente. |
| D9 | Motivo en reapertura | Obligatorio, mínimo 10 caracteres, persistido en `ticket_history.note`. |
| D10 | Estrategia de lock | Mixta. Optimista para `claim_ticket` y reasignación. Pesimista reservado para operaciones multi-tabla (criterio documentado, casos puntuales fuera de este spec). |

---

## Mejoras anotadas para iteraciones futuras (fuera de alcance)

Aspectos detectados durante el descubrimiento que **no se atacan en este spec** pero quedan documentados para no perderse:

- **`rbac-fine-grained-permissions`** (spec dedicado, prioritario): sistema de permisos finos con tabla `permissions`, `user_permissions`, capacidades por nombre (`tickets.approve_quote`, `sla.manage`, `sla.read`, etc.) y jerarquía de administradores `ROOT` ↔ `ADMIN`. Este spec **desbloquea el caso del piloto** donde el dueño-técnico necesita auto-aprobar cotizaciones, y el caso donde el ADMIN del taller debe poder configurar sin tener acceso a operaciones del ROOT (el dev). Hasta que aterrice, el código de tickets usa un fallback documentado en el Requisito 4.4-bis.
- **Acortar `tracking_code`**: el código actual es muy largo. Se acortará en un spec dedicado, con miras a integración futura con impresoras de stickers/QR y app móvil.
- **App móvil**: visión a futuro. Con el tracking corto y los endpoints REST que ya hay, queda factible.
- **Pantalla admin de SLA (frontend)**: el backend queda completo en este spec, pero la UI se aborda en el spec de design system / dashboard admin.
- **Notificaciones por email al cliente**: matriz documentada en `.kiro/steering/notifications.md`. Spec dedicado pendiente. Los `TODO(notify)` siguen anclados en el código.
- **Módulo domiciliario (`delivery_order`)**: requiere reestructuración. Spec dedicado pendiente.
- **SLA con escalado automático**: en V1 no se aplica. Si en producción se valida la necesidad, se añadirá en iteración futura.

---

## Trazabilidad de cambios respecto al estado actual

Esta tabla documenta qué partes de los requisitos requieren código nuevo, qué partes consolidan código existente, y qué queda fuera.

| Área | Tipo | Archivo principal afectado |
|------|------|----------------------------|
| 1.1 Validación uniforme | Refactor (consolidación) | `app/services/ticket_service.py`, `app/api/routes/ticket.py` |
| 1.2 Inventario | Documentación + tests | docstrings + `tests/integration/test_ticket_flow.py` (nuevo) |
| 1.3 Compatibilidad tests | Garantía no-regresión | `tests/unit/core/test_ticket_status_transitions.py` (sin tocar) |
| 2.1 Claim ticket | Funcionalidad nueva | endpoint `POST /tickets/{id}/claim`, service, crud |
| 2.2 Concurrencia (claim) | Funcionalidad nueva | crud (nueva función `claim_atomic`) |
| 2.3 Devolución | Consolidación de lógica existente | `app/services/ticket_service.py::update_ticket` |
| 2.4 Reasignación | Consolidación + tests | service + tests integración |
| 2.5 Carga + control futuro | Solo dashboard + comentarios anchor | `app/services/dashboard_service.py`, `claim_ticket` y reasignación con `# TODO(carga-tecnico)` |
| 3.1 SLA por estado×tipo×prioridad | Funcionalidad nueva + migración | nuevo campo `priority` en `tickets`, nueva tabla `sla_config`, endpoints config |
| 3.2 Detección vencidos | Funcionalidad nueva | service + schemas (`is_overdue`, `overdue_hours`) |
| 3.3 Visualización + notif. interna | Funcionalidad nueva | nueva tabla `internal_notification` (registro), service |
| 4.1–4.4 Visibilidad | Consolidación + ajuste de `STATUS_VISIBILITY_BY_ROLE[ROLE_CLIENT]` | `app/core/ticket_status_visibility.py`, service |
| 4.4-bis Auto-aprobación | Funcionalidad nueva | schema `TicketUpdate`, service (formato de nota) |
| 4.5 COURIER fuera de alcance | Sin cambios | — |
| 5.1 Filtro 6 meses | Funcionalidad nueva | `list_tickets_for_user` |
| 6.1 Motivo de reapertura | Funcionalidad nueva | schema `TicketUpdate`, service (validación contextual) |
| 7.1 Estrategia de lock | Documentación + criterio | comentarios `# CONCURRENCY:` en service, sección dedicada en `design.md` |

---

**Estado del documento:** requirements cerrado. Todas las decisiones pendientes (D1–D10) resueltas. Listo para pasar a `design.md`.
