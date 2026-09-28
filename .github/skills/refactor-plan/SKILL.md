---
name: refactor-plan
description: 'Plan a safe multi-file ProGesTec refactor. Use for finance simplification, role redesign, workflow changes, module restructuring or frontend architecture changes before implementation.'
argument-hint: 'Refactor target and desired outcome'
user-invocable: true
disable-model-invocation: true
---

# Refactor Plan

1. Map callers, data contracts, permissions and tests.
2. Identify the current behavior that must remain stable.
3. Split the work into reversible slices.
4. Define regression tests and rollback points.
5. List files, risks and explicit non-goals.
6. Stop after the plan and wait for approval before editing.
