---
name: ProGesTec Accessibility
description: "Use when editing web UI, forms, dialogs, navigation, tables or responsive layouts in ProGesTec."
applyTo: "progestec-front/**/*.html, progestec-front/**/*.css, progestec-front/**/*.ts"
---

# Accessibility Rules

- Use semantic landmarks, headings and native controls before ARIA.
- Every form control needs a visible or programmatic label and an understandable error state.
- Dialogs must manage focus, support Escape where appropriate and return focus to the trigger.
- All actions must work with keyboard navigation and have visible focus.
- Do not communicate state by color alone.
- Respect reduced-motion preferences and keep touch targets usable on small screens.
- Check empty, loading, error, disabled and success states during UI reviews.
