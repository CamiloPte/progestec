---
name: Operaciones Docker de ProGesTec
description: "Usar al editar Dockerfiles, archivos Compose, scripts de inicio, configuracion de entorno o documentacion de despliegue."
applyTo: "Dockerfile, docker-compose.yml, docker-compose*.yml, scripts/**/*, .env.example, docs/OPERATIONS.md"
---

# Reglas de Docker y operaciones

- Mantén separado el comportamiento de desarrollo local del endurecimiento futuro de produccion.
- Conserva el CORS local intencional salvo que la tarea trate explicitamente la configuracion productiva.
- No confirmes secretos ni datos de clientes.
- Revisa juntos puertos, volumenes, health checks, reinicios y dependencias entre servicios.
- Nunca agregues un reset destructivo de base de datos a un comando normal de inicio.
- Valida la sintaxis Compose y el servicio afectado despues de editar.
