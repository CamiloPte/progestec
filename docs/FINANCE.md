# Finance and Billing

Finance is split into two related concerns:

- **Invoices:** charges generated from tickets, parts, labor, discounts, taxes and payments.
- **Expenses:** operational costs and purchase records used for financial reporting.

## Current product flow

1. A permitted staff user reviews a ticket and its used parts.
2. The system creates one invoice for the ticket.
3. Labor, discount and tax values are reviewed before confirmation.
4. Staff records partial or complete payments.
5. The client can read their own invoice and payment state.
6. Finance users review invoices and expenses through protected views.

## Audit priorities

- Define the canonical lifecycle for invoice and expense statuses.
- Prevent duplicate invoices for one ticket.
- Enforce positive payments and never allow payments above the outstanding balance.
- Recalculate totals on the backend; frontend previews are not authoritative.
- Confirm that only authorized roles can create invoices, edit drafts and register payments.
- Keep money calculations decimal and covered by regression tests.
- Separate operational expenses from customer charges in reports.
- Verify that client and technician views expose only permitted data.

The detailed implementation must be verified against `app/services/invoice_service.py`, finance services, schemas, routes and Angular invoice/finance components. Older documents are historical notes and are not authoritative.
