# Base de Datos y Migraciones

## Reglas Alembic

### Crear migraciones
- Comando: `alembic revision --autogenerate -m "verbo_breve_descripcion"` (snake_case).
- **Siempre** revisar el archivo generado antes de aplicarlo. Alembic autogenera bien tablas y columnas, pero falla con:
  - Renombres de columnas (los detecta como drop+add → pierdes datos).
  - Cambios de tipo no triviales.
  - Constraints con nombres dependientes del dialecto.
- Si renombras una columna, edita la migración para usar `op.alter_column(..., new_column_name=...)` en lugar del drop+add.

### Mensajes
- Formato `verbo_objeto`: `add_invoices_tables`, `update_devices_model`, `add_inventory_tables`.
- Si una migración hace dos cosas, divídela.

### Heads múltiples
- Evitar a toda costa. Heads múltiples ocurren cuando dos branches generan migraciones en paralelo.
- Si pasa, crear merge migration con `alembic merge -m "merge_heads_X_Y"`.
- En este repo ya hay dos merges existentes (`d4ddc8e938f0_merge_expense_and_invoices`, `dfc1f9075a17_merge_inventory_and_devices_heads`). **Eso es señal de que el flujo de branches no estaba sincronizado.** Al refactorizar, intentar consolidar antes de seguir generando migraciones.

### Datos en migraciones
- Evitar lógica de negocio en `upgrade()`/`downgrade()`. Si necesitas seed de datos, usa `op.bulk_insert` con un schema mínimo y deja claro en el commit que es seed inicial.
- Datos maestros (roles, módulos, estados de ticket) van en migraciones de seed dedicadas, no mezcladas con cambios de schema.

### Downgrade
- **Siempre** implementar `downgrade()`. No es opcional.
- Probar el downgrade en local antes de subir.

## Modelos

### Foreign keys
- Especificar `ondelete` siempre. Las opciones razonables:
  - `CASCADE`: el hijo no tiene sentido sin el padre (ej. `ticket_history` → `tickets`).
  - `SET NULL`: el hijo sobrevive (ej. `tickets.assigned_to_id` → `users` cuando un usuario se elimina/desactiva).
  - `RESTRICT`: el padre no se puede eliminar si hay hijos (ej. `parts` con movimientos).
- Validar la elección con la lógica de negocio, no copiar de otro modelo.

### Índices
- Crear índice en columnas que se usan en `WHERE`, `ORDER BY`, o `JOIN` frecuente.
- Foreign keys: MySQL crea índice automáticamente; en PostgreSQL hay que crearlo manualmente.
- Índices compuestos cuando la query siempre filtra por dos columnas juntas.

### Soft delete vs hard delete
- Por defecto: **hard delete**. Es más simple y honesto.
- Soft delete (`deleted_at`) solo en entidades donde el histórico legal o de negocio lo justifica (ej. `invoices` por contabilidad, `users` por trazabilidad).
- Si una entidad usa soft delete, **todas** las queries y validaciones deben respetar `deleted_at IS NULL`.

## Decisiones de modelado pendientes (a resolver en specs)

Estos puntos son redundancias o ambigüedades detectadas. Cuando lleguemos a la spec correspondiente, hay que cerrarlas:

- **`expense` vs `transaction`**: ¿son lo mismo? ¿qué tabla manda?
- **`invoice` + `invoice_payment`** vs **`transaction`**: el flujo de pagos debería estar centralizado.
- **`part_movement`**: ¿registra solo movimientos de inventario, o también consumos por ticket? Si lo segundo, su relación con `ticket_part` necesita aclararse.
- **Catálogo externo**: tres FKs en `device` (`manufacturer_id`, `model_id`, `variant_id`) apuntan al microservicio. Debemos decidir si validamos referencias o solo guardamos.

## Convenciones SQL

- Nombres de tablas en plural: `tickets`, `users`, `invoice_payments`.
- Tablas pivote: nombres en singular concatenados o explícitos: `ticket_parts`, `module_roles`.
- Columnas booleanas con prefijo verbal: `is_active`, `must_change_password`, `has_attachment`.
- Timestamps siempre `*_at` (`created_at`, `updated_at`, `deleted_at`).
- Enumeraciones: usar `Enum` de SQLAlchemy con valores `UPPER_SNAKE_CASE`. Persistir como strings para portabilidad MySQL/Postgres.
