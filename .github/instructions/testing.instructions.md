---
name: ProGesTec Testing
description: "Use when adding, reviewing or running tests for backend, Angular, API contracts or browser workflows."
applyTo: "tests/**/*, progestec-front/**/*.spec.ts, **/package.json, pyproject.toml"
---

# Testing Rules

- Test user-visible behavior and business invariants, not implementation details only.
- Cover happy paths, validation failures, permission failures and boundary values.
- Prioritize login, roles, ticket lifecycle, inventory, invoices, payments and client visibility.
- Keep unit tests fast and isolated; use integration or E2E tests for cross-service behavior.
- Do not weaken or delete a failing test to make a check pass.
- Report unavailable infrastructure separately from code failures.
