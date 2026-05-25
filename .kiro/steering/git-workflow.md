# Git Workflow

## Branching
Modelo simple, una rama larga (`main`) + ramas cortas por tarea.

- `main` — siempre desplegable. Protegida (no push directo).
- `feat/<scope>-<descr>` — nueva funcionalidad. Ej: `feat/tickets-auto-assign`.
- `fix/<scope>-<descr>` — bugfix. Ej: `fix/invoice-totals-rounding`.
- `chore/<descr>` — mantenimiento sin cambio funcional. Ej: `chore/update-deps`.
- `refactor/<scope>-<descr>` — cambios internos sin cambiar comportamiento.
- `docs/<descr>` — documentación.

## Commits (Conventional Commits)
Formato: `<tipo>(<scope opcional>): <descripción imperativa>`

Tipos:
- `feat`: nueva funcionalidad
- `fix`: corrección de bug
- `refactor`: cambio interno sin alterar comportamiento
- `chore`: mantenimiento (deps, config, scripts)
- `docs`: documentación
- `test`: tests
- `style`: formato (espacios, punto y coma) sin cambio funcional
- `perf`: mejora de performance
- `build`: cambios en sistema de build o dependencias
- `ci`: CI/CD

Ejemplos:
```
feat(tickets): permitir auto-asignación a técnico
fix(finance): corregir redondeo en totales de factura
refactor(invoice): unificar invoice_payment con transaction
docs(readme): actualizar instrucciones de setup local
```

Reglas:
- Imperativo en presente: "agregar", "corregir", no "agregado", "agregando".
- Primera línea ≤ 72 caracteres.
- Cuerpo opcional explica el _porqué_, no el _qué_.

## Pull Requests
- Título sigue el mismo formato de commit.
- Descripción incluye: qué cambia, por qué, cómo probarlo, riesgos.
- PRs pequeños mejor que PRs grandes. Si supera ~400 líneas cambiadas, dividir si es posible.
- CI verde antes de mergear.
- Squash merge por defecto: 1 PR = 1 commit en `main`. Mantiene el historial limpio.

## Tags y versiones
Semantic Versioning (`MAJOR.MINOR.PATCH`).
- `MAJOR`: cambios incompatibles en la API o rupturas mayores.
- `MINOR`: funcionalidad nueva compatible.
- `PATCH`: bugfixes compatibles.

Tags: `v1.0.0`, `v1.1.0`, `v1.1.1`. Crear desde `main` después del merge:
```bash
git tag -a v1.0.0 -m "Release 1.0.0: módulo finanzas completo"
git push origin v1.0.0
```

## Qué NO subir
- `.env`, `.env.local` y similares (cubierto por `.gitignore`).
- `node_modules/`, `.angular/cache/`, `dist/`, builds.
- Logs (`app/logs/*.log`).
- Backups de DB (`backup/*.backup`, `*.sql`).
- Uploads de usuarios (`uploads/`, `media/`).
- Datos personales reales (PII) en seeds o tests.

## Hooks (a futuro)
Cuando se incorpore `pre-commit`:
- `ruff check --fix` y `ruff format` en archivos `.py` modificados.
- `mypy` sobre archivos modificados.
- `eslint --fix` y `prettier --write` en `.ts`/`.html`/`.css` del frontend.
- `--no-verify` solo en emergencias y dejar registro en el commit.

## Flujo típico
```bash
# Empezar tarea
git checkout main
git pull
git checkout -b feat/tickets-sla-rules

# Trabajar, commits frecuentes
git add app/core/ticket_status_transitions.py
git commit -m "feat(tickets): añadir validación de SLA por tipo de equipo"

# Subir y abrir PR
git push -u origin feat/tickets-sla-rules
# Abrir PR en GitHub web

# Tras merge
git checkout main
git pull
git branch -d feat/tickets-sla-rules
```
