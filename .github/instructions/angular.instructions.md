---
name: ProGesTec Angular
description: "Use when editing Angular, TypeScript, HTML or CSS in the ProGesTec frontend."
applyTo: "progestec-front/**/*.ts, progestec-front/**/*.html, progestec-front/**/*.css"
---

# Angular Rules

- Keep Angular 20 standalone components and SSR compatibility.
- Keep route-level lazy loading and existing core/feature/shared boundaries.
- Guard browser-only APIs with the existing platform checks.
- Keep HTTP access in core services and preserve typed models.
- Prefer observable or signal state that matches nearby code; do not introduce a new state library casually.
- Use accessible labels, focus states, keyboard operation and explicit loading/error/empty states.
- Add or update a focused Jasmine test for behavior changes.
- Run the frontend unit test and production build after changes.
