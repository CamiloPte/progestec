# ProGesTec

Sistema web para la gestión de servicio técnico de telefonía y laptops.

Monorepo con tres unidades:

| Carpeta | Stack | Puerto local |
|---|---|---|
| `app/` | FastAPI + SQLAlchemy + MySQL | 8000 |
| `progestec-front/` | Angular 20 (SSR) | 4200 |
| `catalog-service/` | Express + PostgreSQL | 5000 |

## Requisitos
- Docker Desktop
- Node 22+
- Python 3.11 (si quieres correr el backend fuera de Docker)

## Setup rápido (Windows)
```bat
:: 1) Variables de entorno
copy .env.example .env
:: edita .env con tus valores

:: 2) Arranque completo
scripts\start-all.bat
```

Esto levanta:
- MySQL y Postgres en contenedores
- API FastAPI en `http://localhost:8000` (Swagger en `/docs`)
- Catalog service en `http://localhost:5000`
- Frontend Angular en `http://localhost:4200`

## Setup manual
```bash
# Backend (sin Docker)
python -m venv .venv
.venv\Scripts\activate         # Windows
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload

# Frontend
cd progestec-front
npm install
ng serve

# Catálogo
cd catalog-service
npm install
node src/server.js
```

## Migraciones
```bash
alembic revision --autogenerate -m "verbo_objeto"
alembic upgrade head
alembic downgrade -1
```

## Estructura del proyecto
```
.
├── .kiro/                  # Specs y steering (reglas que guían el desarrollo)
├── alembic/                # Migraciones DB
├── app/                    # Backend FastAPI
│   ├── api/routes/         # Endpoints HTTP
│   ├── core/               # Config, security, logger
│   ├── crud/               # Acceso a datos
│   ├── models/             # Modelos SQLAlchemy
│   ├── schemas/            # Schemas Pydantic
│   └── services/           # Lógica de negocio
├── catalog-service/        # Microservicio Express
├── docs/                   # Documentación funcional del proyecto
├── progestec-front/        # Frontend Angular
└── scripts/                # Scripts .bat de arranque (Windows)
```

## Documentación
- `docs/DOCUMENTO_PROYECTO_ACTUALIZADO.md` — vista funcional del producto
- `docs/ESTADO_ACTUAL_PROYECTO.md` — qué está hecho y qué no
- `docs/OBJETIVOS_Y_PLAN_ACCION.md` — siguientes pasos
- `docs/FACTURACION_BACKEND.md` y `docs/FACTURACION_FRONTEND.md` — módulo facturación
- `.kiro/steering/` — reglas de arquitectura, convenciones y workflow

## Contribuir
Lee `.kiro/steering/git-workflow.md` para flujo de ramas y formato de commits.
Resumen:
- Una rama por tarea: `feat/...`, `fix/...`, `refactor/...`
- Conventional Commits (`feat(tickets): ...`)
- PRs pequeños, squash merge

## Licencia
Privado. Todos los derechos reservados.
