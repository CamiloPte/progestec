# Operations and Quality

## Development services

- API: `http://localhost:8000`
- API documentation: `http://localhost:8000/docs`
- Angular SSR development server: `http://localhost:4200`
- Catalog service: `http://localhost:5000`
- MySQL: Docker service `db`
- PostgreSQL: Docker service `catalog_db`

## Baseline checks

```bash
docker compose config
pytest
ruff check .
ruff format --check .
```

```powershell
Set-Location progestec-front
npm test -- --watch=false --browsers=ChromeHeadless
npm run build
```

## Critical flows to test

1. Login, forced password change, logout and expired token.
2. Permission boundaries for every role.
3. Ticket intake, assignment, diagnosis, approval, repair, delivery and closure.
4. Attachment upload, download and authorization.
5. Inventory movement and stock invariants.
6. Invoice creation, totals, partial payments and settlement.
7. Client portal visibility boundaries.
8. Catalog lookup and failure handling.

## Production hardening backlog

- Separate development and production Compose configuration.
- Remove backend reload mode from production images.
- Require secrets and production URLs from environment variables.
- Restrict CORS only when the production domains are known.
- Add health checks, backups, restore drills, log rotation and monitoring.
- Define file-upload limits, allowed types and storage retention.
- Add migration review and rollback procedures.
