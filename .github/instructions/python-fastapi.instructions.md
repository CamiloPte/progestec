---
name: ProGesTec Python and FastAPI
description: "Use when editing Python, FastAPI routes, services, CRUD modules, schemas, models or tests."
applyTo: "app/**/*.py, tests/**/*.py, alembic/**/*.py, pyproject.toml"
---

# Python and FastAPI Rules

- Keep the existing routes -> services -> crud -> models/schemas architecture.
- Put authorization and business rules in services or dedicated security dependencies.
- Validate external data with Pydantic schemas and preserve stable response contracts.
- Use SQLAlchemy sessions through the existing database dependency.
- Keep migrations reversible and review generated SQL before applying them.
- Use the project logger instead of ad-hoc prints in application code.
- Add focused pytest coverage for changed business rules and permission boundaries.
- Run `ruff check .`, `ruff format --check .` and the relevant pytest selection.
