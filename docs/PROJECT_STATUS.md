# Project Status

## Current position

ProGesTec is in stabilization and product-audit phase. It is no longer treated as an academic prototype, but production readiness has not been certified.

## Implemented surfaces to verify

- Authentication, JWT and password-change flow.
- Role-based access for ADMIN, ADVISOR, TECHNICIAN and CLIENT.
- Ticket creation, assignment, status history, attachments and client tracking.
- Inventory dashboard, parts, movements and ticket parts.
- Invoices, invoice detail and payments.
- Client portal for tickets, devices and invoices.
- Angular SSR build and Docker-based database environment.

## Known validation gaps

- End-to-end coverage for login, roles, ticket lifecycle, inventory and billing.
- Angular spec files must be checked against current component class names and dependencies.
- Finance and billing workflows need a single clear operational model.
- Catalog service needs runtime and data-seeding verification.
- Audit trail, backups, retention, structured logs and deployment monitoring remain open.
- The current CORS policy is intentionally permissive for local development and is a production-hardening task, not a current defect.

## Source of truth

Code and executable checks take precedence over older planning documents. Update this file when a module is audited or its status changes.
