# Architecture

## Product shape

ProGesTec is a Windows-friendly monorepo with three deployable units:

- `app/`: FastAPI API with SQLAlchemy, Alembic and MySQL.
- `progestec-front/`: Angular 20 application with TypeScript, RxJS and SSR.
- `catalog-service/`: Express service with PostgreSQL for device master data.

The Angular application calls the API and catalog service. The API owns transactional data; the catalog owns manufacturers, models and variants.

## Backend boundaries

```text
api/routes -> services -> crud -> models
                  |          |
                  +-> schemas +-> db
```

- Routes translate HTTP input and output only.
- Services own business rules, permissions and multi-step operations.
- CRUD modules own persistence operations.
- Models describe SQLAlchemy tables and relations.
- Schemas define API contracts.
- `core/` contains configuration, security, roles, logging and shared rules.

Avoid SQL or business rules in routes, direct CRUD calls from routes when a service exists, and imports from schemas into models.

## Frontend boundaries

- `core/`: HTTP services, models, guards, interceptors, layouts and shared infrastructure.
- `auth/`: login and password-change flows.
- Feature folders: tickets, inventory, invoices, finance and client portal.
- `shared/`: reusable UI components and utilities.

Use the existing standalone Angular component style and lazy routes. Keep API contracts aligned with Pydantic schemas.

## Runtime boundaries

Docker Compose currently provides MySQL and PostgreSQL for development. The backend image is also built independently. Production deployment is not yet finalized and must use separate configuration, secrets, health checks, persistence and logging policies.
