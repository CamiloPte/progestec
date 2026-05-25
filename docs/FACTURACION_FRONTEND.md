# Integración Frontend – Módulo de Facturación

## 1. Resumen de cambios
- Se agregó `InvoiceService` en `src/app/core/services` con métodos para crear, listar y administrar facturas y pagos.
- Se definieron las interfaces `Invoice`, `InvoiceCreateDto`, `InvoicePayment`, etc. en `src/app/core/models/invoice.ts`.
- Se incorporó la gestión de facturas dentro del detalle de ticket (`ticket-detail.component`), incluyendo generación, resumen y acceso rápido al detalle.
- Se añadieron tres componentes standalone:
  - `invoices/invoice-list`: listado administrativo con filtros.
  - `invoices/invoice-detail`: detalle completo de factura y registro de pagos.
  - `invoices/client-invoices`: listado simplificado para clientes.
- Se actualizó la navegación con nuevas rutas protegidas (`/facturacion`, `/mis-facturas`).
- Se documentaron los flujos para ADMIN/ADVISOR y CLIENTE.

## 2. Servicios y modelos
### InvoiceService
| Método | Endpoint backend | Descripción |
| --- | --- | --- |
| `createInvoiceFromTicket(ticketId, payload)` | `POST /invoices/from-ticket/{ticket_id}` | Genera una factura para el ticket indicado. |
| `getInvoice(invoiceId)` | `GET /invoices/{invoice_id}` | Recupera una factura específica. |
| `listInvoices(filters)` | `GET /invoices` | Permite filtrar por estado, cliente, rango de fechas y saldo. |
| `registerPayment(invoiceId, payload)` | `POST /invoices/{invoice_id}/payments` | Registra un pago y retorna la factura actualizada. |
| `listPayments(invoiceId)` | `GET /invoices/{invoice_id}/payments` | Lista pagos históricos de la factura. |

### Interfaces relevantes
- `Invoice`: refleja `InvoiceRead` con totales, status y pagos.
- `InvoiceCreateDto`: datos requeridos para generar una factura (mano de obra, descuento, impuestos, vencimiento, notas).
- `InvoicePayment` / `InvoicePaymentCreateDto`.
- `InvoiceFilters` para `listInvoices`.

## 3. Componentes y vistas
### TicketDetailComponent
- Nueva tarjeta “Facturación” muestra el estado actual de la factura del ticket, costos y pagos.
- Modal para ADMIN/ADVISOR que permite generar factura calculando subtotal/impuestos a partir de repuestos (`ticket_parts`).
- Enlaces directos al detalle de factura (`/facturacion/:id` o `/mis-facturas/:id` según rol).

### InvoiceListComponent (`/facturacion`)
- Visibilidad: ADMIN/ADVISOR (guard `financeGuard`).
- Contiene filtros por estado, cliente, fechas y saldo pendiente. Tabla con número, cliente, totales y estado.

### InvoiceDetailComponent (`/facturacion/:id` y `/mis-facturas/:id`)
- Muestra información completa de la factura, costos y pagos.
- ADMIN/ADVISOR: formulario para registrar pagos.
- CLIENT: vista solo lectura.

### ClientInvoicesComponent (`/mis-facturas`)
- Tabla resumida con facturas del cliente autenticado. Reutiliza el mismo componente de detalle.

## 4. Rutas y guards
| Ruta | Roles | Descripción |
| --- | --- | --- |
| `/facturacion` | ADMIN/ADVISOR (`financeGuard`) | Listado general de facturas. |
| `/facturacion/:id` | ADMIN/ADVISOR | Detalle editable. |
| `/mis-facturas` | CLIENT (`clientGuard`) | Listado personal del cliente. |
| `/mis-facturas/:id` | CLIENT | Detalle en modo lectura. |
| `/tickets/:id` | Todos los roles permitidos | Ahora incluye sección de facturación integrada. |

## 5. Flujo básico
1. **Generar factura desde un ticket**
   - ADMIN/ADVISOR en detalle de ticket → botón “Generar factura”.
   - Se abre modal con mano de obra, descuento, impuestos. Se muestran costos de repuestos y total estimado.
   - Al confirmar se llama `InvoiceService.createInvoiceFromTicket` y la tarjeta se actualiza con el nuevo estado.
2. **Consultar facturas**
   - ADMIN/ADVISOR entran a `/facturacion`, aplican filtros y abren cualquier fila para ver detalle o registrar pagos.
   - CLIENT entra a `/mis-facturas` para ver sus facturas y el detalle sin controles de pago.
3. **Registrar pagos**
   - Desde `/facturacion/:id`, formulario “Registrar pago” envía `registerPayment` y refresca la factura.
4. **Permisos**
   - TECHNICIAN ve la tarjeta informativa dentro del ticket (solo lectura).
   - CLIENT visualiza únicamente facturas relacionadas a sus tickets mediante las rutas dedicadas.

