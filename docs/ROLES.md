# Roles and Scope

Role names and permissions must be confirmed against the backend implementation before release. This document is the product-level target, not a substitute for authorization checks.

| Role | Primary responsibility | Must not do |
| --- | --- | --- |
| `ADMIN` | Configuration, users, modules, all operational and financial actions | Bypass audit or production controls |
| `ADVISOR` | Customer intake, ticket coordination, assignment, budgets and invoices | Change system configuration outside assigned scope |
| `TECHNICIAN` | Diagnose and repair assigned tickets, record work and parts used | Access unrelated customer data or register payments |
| `CLIENT` | View own tickets, devices and invoices; approve budgets when allowed | View other clients or operate internal modules |
| `COURIER` | Delivery-related actions when enabled | Modify diagnosis, prices, inventory or payments |

## Rules for implementation

- Enforce permissions in the backend; frontend guards are navigation aids only.
- Check object ownership for tickets, devices, invoices, payments and attachments.
- Keep role names centralized in `app/core/roles.py` and permission logic in dedicated services/dependencies.
- Document every role-sensitive workflow with a positive and negative test.
- Do not add a role or permission only in the frontend.
