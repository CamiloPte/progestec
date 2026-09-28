---
name: Pruebas de ProGesTec
description: "Usar al agregar, revisar o ejecutar pruebas de backend, Angular, contratos API o flujos del navegador."
applyTo: "tests/**/*, progestec-front/**/*.spec.ts, **/package.json, pyproject.toml"
---

# Reglas de pruebas

- Prueba el comportamiento visible para el usuario y los invariantes de negocio, no solo detalles internos.
- Cubre caminos exitosos, fallos de validacion, fallos de permisos y valores limite.
- Prioriza login, roles, ciclo de vida de tickets, inventario, facturas, pagos y visibilidad del cliente.
- Mantén las pruebas unitarias rapidas y aisladas; usa integracion o E2E entre servicios.
- No debilites ni elimines una prueba fallida para hacer pasar una comprobacion.
- Reporta por separado la infraestructura no disponible y los fallos del codigo.
