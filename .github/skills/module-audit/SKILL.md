---
name: module-audit
description: 'Auditar un modulo de ProGesTec de extremo a extremo. Usar para tickets, inventario, finanzas, facturas, usuarios, portal cliente, catalogo o autenticacion y comparar rutas, services, interfaz, permisos, pruebas y documentacion.'
argument-hint: 'Modulo o flujo que se desea auditar'
user-invocable: true
---

# Auditoria de modulos

1. Identifica rutas backend, services, CRUD, models y schemas.
2. Identifica rutas Angular, componentes, services, guards y templates.
3. Traza los flujos principales y los limites por rol.
4. Localiza pruebas y ejecuta las comprobaciones disponibles mas pequeñas.
5. Compara la implementacion con los documentos canonicos.
6. Reporta comportamiento confirmado, faltantes, problemas estructurales, fricciones UX y acciones priorizadas.

No edites archivos salvo que el usuario cambie explicitamente la solicitud de auditoria a implementacion.
