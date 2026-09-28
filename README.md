# ProGesTec

ProGesTec es una plataforma web para administrar un servicio tecnico de telefonos,
laptops y otros dispositivos. Centraliza la recepcion de equipos, el seguimiento de
reparaciones, el inventario, la facturacion y el portal del cliente.

El repositorio es un monorepo con tres unidades:

| Carpeta | Stack | Puerto local |
|---|---|---|
| `app/` | FastAPI, SQLAlchemy, Alembic y MySQL | `http://localhost:8000` |
| `progestec-front/` | Angular 20, TypeScript, RxJS y SSR | `http://localhost:4200` |
| `catalog-service/` | Express, Node.js y PostgreSQL | `http://localhost:5000` |

## Estado actual

El sistema se encuentra en estabilizacion y auditoria antes de pasar a produccion.
Tickets, roles, portal cliente, inventario y facturacion tienen implementacion activa,
pero deben validarse de extremo a extremo y simplificarse algunos flujos.

Consulta [docs/PROJECT_STATUS.md](docs/PROJECT_STATUS.md) para el estado por modulo y
[docs/ROADMAP.md](docs/ROADMAP.md) para el orden de trabajo.

## Requisitos

- Docker Desktop
- Node.js 22 o superior
- Python 3.11 o superior para ejecutar el backend fuera de Docker

## Inicio con Docker

Docker Compose proporciona MySQL y PostgreSQL. Los scripts del repositorio arrancan la
API, el catalogo y el frontend segun el flujo de desarrollo local.

```bat
copy .env.example .env
scripts\start-all.bat
```

```bash
docker compose ps
```

La API expone Swagger en `http://localhost:8000/docs`.

## Inicio manual

Backend:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

Frontend:

```powershell
cd progestec-front
npm install
npm start
```

Catalogo:

```powershell
cd catalog-service
npm install
npm run dev
```

## Migraciones
```bash
alembic revision --autogenerate -m "verbo_objeto"
alembic upgrade head
alembic downgrade -1
```

## Pruebas y calidad

```bash
pytest
ruff check .
ruff format --check .
```

```powershell
cd progestec-front
npm test -- --watch=false --browsers=ChromeHeadless
npm run build
```

La estrategia de pruebas y las brechas conocidas estan en
[docs/OPERATIONS.md](docs/OPERATIONS.md).

## Estructura

```
app/                 API FastAPI y logica de negocio
alembic/             Migraciones de base de datos
catalog-service/     Catalogo independiente de dispositivos
progestec-front/     Aplicacion Angular SSR
tests/               Pruebas backend
scripts/             Automatizacion local para Windows
docs/                Documentacion canonica del producto
.github/             Configuracion compartida de Copilot y CI
```

La arquitectura esta en [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md), los roles en
[docs/ROLES.md](docs/ROLES.md) y el flujo financiero en [docs/FINANCE.md](docs/FINANCE.md).
Las variables sensibles deben vivir en `.env`; nunca se deben confirmar secretos,
tokens, dumps o archivos subidos por usuarios.

## Flujo de trabajo

Cada cambio debe desarrollarse en una rama de tarea, validarse localmente y enviarse
mediante Pull Request. Se usan Conventional Commits y revisiones pequenas. La
configuracion de Copilot del repositorio define las reglas para agentes, skills,
instrucciones y hooks.

## Licencia
Privado. Todos los derechos reservados.
