# Producto: ProGesTec

## Qué es
Sistema web para la gestión de servicio técnico de telefonía y laptops. Cliente piloto: Fedecafé Barranquilla. Es a la vez un proyecto de grado y un prototipo en producción incremental.

## Problema que resuelve
Los talleres técnicos sin software estructurado sufren de:
- Pérdida de trazabilidad en órdenes de servicio
- Inventario de repuestos descontrolado
- Comunicación reactiva con clientes (llamadas, WhatsApp manual)
- Cobros y gastos sin registro contable
- Imposibilidad de medir desempeño por técnico o por tipo de equipo

## Actores y roles
- **ADMIN**: control total. Gestiona usuarios, supervisa todo, ve finanzas.
- **ADVISOR** (asesor): recibe equipos, crea tickets, asigna técnicos, factura, cobra.
- **TECHNICIAN**: trabaja tickets asignados o sin asignar; consume repuestos; documenta el trabajo.
- **CLIENT**: portal de seguimiento; aprueba/rechaza presupuestos; ve facturas e historial.
- **COURIER**: gestiona recogidas y entregas a domicilio (modelo presente, flujo en evolución).

## Módulos principales
1. **Tickets** — ciclo de vida del servicio técnico (eje del sistema).
2. **Dispositivos** — equipos de clientes con catálogo externo (manufacturers/models/variants).
3. **Inventario** — repuestos, stock, movimientos.
4. **Finanzas** — facturas, pagos, gastos.
5. **Dashboard** — KPIs por rol.
6. **Portal cliente** — vista propia de tickets, dispositivos, facturas.
7. **Usuarios y permisos** — RBAC con módulos y roles.

## Estado actual (resumen)
Ver `docs/ESTADO_ACTUAL_PROYECTO.md` para detalle. Aproximado:
- Tickets: ~90% (falta consolidar transiciones por rol y SLAs)
- Inventario: ~80% (falta integración completa con catálogo externo)
- Finanzas: ~90% (falta reportes y unificar modelos contables)
- Notificaciones: ~20% (SMTP por implementar)
- Auditoría: pendiente

## Foco actual
Refactor enfocado en:
1. Eliminar redundancias entre modelos (`expense`, `invoice`, `transaction`, `part_movement`).
2. Validar transiciones de estado con reglas claras por rol.
3. Pulir UX (búsquedas en vivo, overlays, validaciones).
4. Versionar el código en GitHub y establecer CI mínimo.
5. Unificar el design system del frontend.

## Lo que NO es este proyecto
- No es un ERP completo. No reemplaza contabilidad fiscal.
- No es un CRM. La relación con cliente está al servicio del ticket, no al revés.
- No persigue multi-tenant en V1.
