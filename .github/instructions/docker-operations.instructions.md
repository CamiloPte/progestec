---
name: ProGesTec Docker Operations
description: "Use when editing Dockerfiles, Compose files, startup scripts, environment configuration or deployment documentation."
applyTo: "Dockerfile, docker-compose.yml, docker-compose*.yml, scripts/**/*, .env.example, docs/OPERATIONS.md"
---

# Docker and Operations Rules

- Keep local development behavior separate from future production hardening.
- Preserve intentional local CORS behavior unless the task explicitly targets production configuration.
- Do not commit secrets or customer data.
- Review ports, volumes, health checks, restart behavior and service dependencies together.
- Never add destructive database reset behavior to a normal startup command.
- Validate Compose syntax and the affected service after changes.
