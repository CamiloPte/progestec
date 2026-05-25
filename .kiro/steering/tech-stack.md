# Stack Tecnológico

## Backend
- **Lenguaje**: Python 3.11 (Dockerfile). Local también puede ser 3.13/3.14 — el contenedor manda.
- **Framework**: FastAPI 0.115.x
- **ORM**: SQLAlchemy 2.0.x (estilo declarativo moderno con `Mapped[...]`)
- **Validación**: Pydantic 2.x + `pydantic-settings`
- **Migraciones**: Alembic
- **Auth**: JWT con `python-jose`; hashing con `passlib[bcrypt]`
- **Email**: `fastapi-mail` (configurado, sin uso real aún)
- **PDF**: servicio en `app/services/pdf_service.py`

## Base de datos
- **Principal**: MySQL 8.0 (servicio `db` en compose, puerto externo 3307, interno 3306)
- **Catálogo**: PostgreSQL 16 (servicio `catalog_db`, puerto 5432) — separado por diseño

## Microservicios
- **catalog-service**: Express.js (Node 22) — sirve fabricantes, modelos, variantes desde Postgres

## Frontend
- **Angular 20.3** con SSR habilitado
- **TypeScript 5.9**
- **RxJS 7.8** (consideramos migrar a signals donde tenga sentido, no obligatorio)
- **Estilos**: CSS plano con variables (`grays`, `shadows`, `radii`, `transitions`)
- **Fuente**: Inter

## Infraestructura
- **Contenedores**: Docker + docker-compose
- **Scripts Windows**: `.bat` en `scripts/` (atajos para arranque/parada en dev)
- **Storage**: filesystem local (`uploads/`) — montado como volumen en producción

## Herramientas a adoptar (decididas)
Cuando se incorporen, irán pinneadas a estas versiones mínimas:

### Backend
- **ruff** (lint + format) — un solo binario sustituye black, isort, flake8.
- **mypy** — type check estricto progresivo.
- **pytest** + **hypothesis** — tests unitarios y property-based.
- **schemathesis** — fuzzing de la API a partir del OpenAPI generado.
- **pre-commit** — corre ruff + mypy local antes del commit.

### Frontend
- **eslint** + **prettier** (los que ya trae Angular CLI) — verificar configuración consistente.
- **playwright** o **cypress** — E2E (decidir cuando lleguemos a esa spec).

### CI/CD
- **GitHub Actions** — workflows: `backend-ci.yml`, `frontend-ci.yml`.
- **Dependabot** — actualizaciones automáticas semanales.

## Versiones y reproducibilidad
- Las dependencias backend se pinean en `requirements.txt`.
- Las dependencias frontend en `package-lock.json`.
- Los Dockerfiles usan tags concretos (`python:3.11-slim`, `mysql:8.0`, `postgres:16`).
- Evitar `latest` en producción.

## Lo que NO usamos (y por qué)
- **Celery / RabbitMQ**: aún no hay carga asíncrona que lo justifique. Si llegan jobs largos (emails, PDFs masivos), evaluamos `BackgroundTasks` de FastAPI primero, después Celery o `arq`.
- **Redis**: no hay caché que lo justifique aún.
- **GraphQL**: REST cubre todos los casos actuales.
- **Frameworks UI pesados** en frontend: Angular ya da estructura suficiente. Si adoptamos componentes, será Spartan UI o CDK por ser ligeros.
