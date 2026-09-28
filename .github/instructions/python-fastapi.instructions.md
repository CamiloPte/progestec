---
name: Python y FastAPI de ProGesTec
description: "Usar al editar Python, rutas FastAPI, services, modulos CRUD, schemas, models o pruebas."
applyTo: "app/**/*.py, tests/**/*.py, alembic/**/*.py, pyproject.toml"
---

# Reglas de Python y FastAPI

- Conserva la arquitectura existente routes -> services -> crud -> models/schemas.
- Coloca autorizacion y reglas de negocio en services o dependencias de seguridad dedicadas.
- Valida datos externos con schemas Pydantic y conserva contratos de respuesta estables.
- Usa sesiones SQLAlchemy mediante la dependencia de base de datos existente.
- Mantén las migraciones reversibles y revisa el SQL generado antes de aplicarlas.
- Usa el logger del proyecto en vez de prints improvisados en la aplicacion.
- Agrega cobertura pytest enfocada en reglas de negocio y limites de permisos modificados.
- Ejecuta `ruff check .`, `ruff format --check .` y la seleccion relevante de pytest.
