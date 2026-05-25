# Módulo de Facturación – Backend ProGesTec

Este documento resume los cambios realizados para habilitar la capa financiera del proyecto.  
La implementación sigue la arquitectura existente (modelos → CRUD → services → routers) y respeta los roles actuales.

---

## 1. Resumen de lo implementado

- **Modelos SQLAlchemy:** `Invoice` e `InvoicePayment` con sus relaciones a `Ticket`, `User` y pagos.
- **Migración Alembic:** crea tablas `invoices` y `invoice_payments` con claves foráneas e índices.
- **Schemas Pydantic:** estructuras de entrada/salida para facturas y pagos (`InvoiceCreate`, `InvoiceRead`, `InvoicePaymentCreate`, etc.).
- **Servicio de dominio:** `InvoiceService` encapsula la lógica financiera (cálculos, reglas de negocio, permisos y registro de pagos).
- **CRUDs:** `invoice_crud` y `invoice_payment_crud` para operaciones persistentes y filtros (incluye `with_debt`).
- **Router FastAPI:** `/invoices` con endpoints para generar facturas, listarlas, consultar detalle y registrar/listar pagos.
- **Documentación** (este archivo) para que otros equipos puedan consumir el módulo y preparar integraciones (Angular/Power BI).

---

## 2. Modelo de datos

### 2.1. Tabla `invoices`

| Campo | Tipo | Descripción |
| --- | --- | --- |
| `id` | PK | Identificador interno. |
| `ticket_id` | FK → `tickets.id` (CASCADE/RESTRICT) | Cada ticket tiene como máximo una factura (constraint unique). |
| `client_id` | FK → `users.id` | Cliente propietario del dispositivo/ticket. |
| `invoice_number` | `VARCHAR(40)` único | Formato `INV-YYYYMMDD-TRACKING`. |
| `issue_date` | `DATETIME` | Fecha de emisión. |
| `due_date` | `DATETIME` opcional | Fecha de vencimiento. |
| `parts_cost` | `DECIMAL(12,2)` | Suma de `ticket_parts.total_cost`. |
| `labor_cost` | `DECIMAL(12,2)` | Mano de obra ingresada al generar la factura. |
| `discount_amount` | `DECIMAL(12,2)` | Descuentos manuales. |
| `subtotal` | `DECIMAL(12,2)` | `parts_cost + labor_cost - discount_amount`. |
| `tax_percentage` / `tax_amount` | `DECIMAL` | Porcentaje aplicado y monto resultante. |
| `total` | `DECIMAL(12,2)` | `subtotal + tax_amount`. |
| `status` | `VARCHAR(20)` | `PENDING`, `PAID`, `CANCELLED`… |
| `created_by_id` | FK → `users.id` | Usuario que generó la factura. |
| `paid_at` | `DATETIME` | Fecha en la que quedó totalmente pagada. |
| `notes` | `TEXT` | Observaciones. |
| `state`, `created_at`, `updated_at` | Mixins estándar. |

### 2.2. Tabla `invoice_payments`

| Campo | Tipo | Descripción |
| --- | --- | --- |
| `id` | PK | Identificador. |
| `invoice_id` | FK → `invoices.id` (CASCADE) | Pago asociado. |
| `amount` | `DECIMAL(12,2)` | Monto del pago. |
| `payment_method` | `VARCHAR(30)` | `CASH`, `CARD`, `BANK_TRANSFER`, etc. |
| `reference` | `VARCHAR(100)` | Número de recibo o referencia externa. |
| `paid_at` | `DATETIME` | Fecha registrada del pago. |
| `created_by_id` | FK → `users.id` | Usuario que registró el pago. |
| `state`, `created_at`, `updated_at` | Mixins estándar. |

Relaciones principales:
- `Ticket.invoice` (uno a uno) y `Invoice.ticket`.
- `Invoice.payments` (uno a muchos) y `InvoicePayment.invoice`.
- `Invoice.client` (usuario propietario) y `Invoice.creator` (usuario que la generó).

---

## 3. Servicio `InvoiceService`

Archivo: `app/services/invoice_service.py`

### Métodos clave

- **`generate_invoice_for_ticket`**
  - Roles permitidos: `ADMIN`, `ADVISOR`.
  - Valida que el ticket exista, esté activo y tenga cliente.
  - Suma `ticket_parts.total_cost` para calcular `parts_cost`.
  - Aplica mano de obra, descuento y porcentaje de impuestos → calcula subtotal, impuestos y total.
  - Genera `invoice_number` (basado en fecha y tracking del ticket) y crea el registro con estado `PENDING`.

- **`get_invoice` / `list_invoices`**
  - Control de permisos:
    - `ADMIN/ADVISOR`: acceso completo y filtros server-side.
    - `TECHNICIAN`: solo facturas de sus tickets (filtros in-memory).
    - `CLIENT`: únicamente facturas donde él es `client_id`.
  - `InvoiceRead` devuelve totales, pagos, saldo pendiente y datos del ticket/cliente.

- **`register_payment`**
  - Solo `ADMIN/ADVISOR`.
  - Verifica que el monto sea positivo y no exceda el saldo.
  - Registra `InvoicePayment`.
  - Actualiza estado de factura (`PAID` cuando cubre el total) y `paid_at`.

- **`list_payments_for_invoice`**
  - Devuelve historial de pagos ordenado por fecha (`paid_at`/`created_at`).

Helpers adicionales:
- `_sum_payments` obtiene el total abonado.
- `_apply_in_memory_filters` replica filtros para técnicos cuando la consulta no incluye joins adicionales.

---

## 4. Endpoints FastAPI

Router: `app/api/routes/invoice.py` (registrado en `main.py`)

| Método y ruta | Descripción | Roles |
| --- | --- | --- |
| `POST /invoices/from-ticket/{ticket_id}` | Genera factura para un ticket. Body: `InvoiceCreate`. | ADMIN, ADVISOR |
| `GET /invoices/{invoice_id}` | Obtiene detalle completo (`InvoiceRead`). | ADMIN/ADVISOR, TECHNICIAN (solo propios), CLIENT (solo propios) |
| `GET /invoices` | Lista facturas con filtros: `status`, `client_id`, `from_date`, `to_date`, `with_debt`. | ADMIN/ADVISOR (todas), TECHNICIAN (solo sus tickets), CLIENT (solo propios) |
| `POST /invoices/{invoice_id}/payments` | Registra pago parcial o total. Body: `InvoicePaymentCreate`. | ADMIN, ADVISOR |
| `GET /invoices/{invoice_id}/payments` | Historial de pagos (`InvoicePaymentRead`). | Misma regla de lectura que la factura. |

### Ejemplos

**Crear factura:**
```json
POST /invoices/from-ticket/12
{
  "ticket_id": 12,
  "labor_cost": 80.0,
  "discount_amount": 10,
  "tax_percentage": 19,
  "due_date": "2025-12-01T00:00:00",
  "notes": "Trabajo autorizado por el cliente"
}
```

**Registrar pago:**
```json
POST /invoices/5/payments
{
  "invoice_id": 5,
  "amount": 120.00,
  "payment_method": "CARD",
  "reference": "POS-45871"
}
```

---

## 5. Guía rápida para reportes (Power BI / SQL)

Totales pueden calcularse directamente desde las tablas nuevas:

```sql
-- Ventas facturadas (total)
SELECT COALESCE(SUM(total), 0) AS total_facturado
FROM invoices
WHERE state = 1;

-- Costo de repuestos utilizados
SELECT COALESCE(SUM(parts_cost), 0) AS costo_repuestos
FROM invoices
WHERE state = 1;

-- Mano de obra total
SELECT COALESCE(SUM(labor_cost), 0) AS costo_mano_obra
FROM invoices
WHERE state = 1;

-- Pagos recibidos / saldo global
SELECT
    COALESCE(SUM(i.total), 0) AS total_facturas,
    COALESCE(SUM(p.amount), 0) AS total_pagado,
    COALESCE(SUM(i.total), 0) - COALESCE(SUM(p.amount), 0) AS saldo_pendiente
FROM invoices i
LEFT JOIN invoice_payments p ON p.invoice_id = i.id AND p.state = 1
WHERE i.state = 1;
```

**Margen aproximado** por factura/ticket:

```
margen = total - parts_cost - labor_cost
```

Puedes exponerlo a BI sumando por rango de fechas o por cliente.

---

## 6. Consideraciones finales

- El módulo no modifica la lógica original de tickets ni inventario; sólo consume `ticket_parts.total_cost`.
- Cada ticket puede tener **una** factura (constraint `unique=True` en `ticket_id`).
- Los estados de factura son controlados por `InvoiceService`; se pueden ampliar en fases futuras (`PARTIALLY_PAID`, anulaciones, etc.).
- El router ya está disponible en Swagger/OpenAPI junto con los modelos utilizados en el frontend y futuras integraciones (correo, Power BI, etc.).

Con esto el backend queda listo para conectar la UI de facturación y alimentar dashboards financieros.
