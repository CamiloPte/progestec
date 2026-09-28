# ProGesTec Copilot Instructions

- Treat this repository as a production-bound product, not an academic prototype.
- Read the relevant code, tests and canonical docs before editing.
- Keep changes small, explicit and limited to the requested area.
- Preserve the monorepo boundaries: FastAPI/MySQL, Angular SSR, and catalog Express/PostgreSQL.
- Do not introduce AEM, HTL, React, Vue, Tailwind or unrelated frameworks.
- Backend flow: routes -> services -> crud -> models/schemas. Keep business rules in services.
- Frontend uses Angular 20 standalone components, lazy routes, TypeScript and RxJS.
- Backend and frontend contracts must be checked together for API changes.
- CORS is intentionally permissive for local development. Do not change it during unrelated tasks.
- Never expose secrets, tokens, uploads, database dumps or real customer data.
- Do not run destructive migrations, resets, deletes or production actions without explicit confirmation.
- After edits, run the narrowest relevant test, lint or build before expanding scope.
- Update the canonical docs when behavior, architecture, operations or roadmap changes.
- Prefer Spanish user-facing text and ASCII in source files unless the existing file requires another encoding.
