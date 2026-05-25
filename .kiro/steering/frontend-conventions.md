# Convenciones del Frontend

## Estructura
```
src/app/
├── core/
│   ├── services/       # Servicios HTTP (uno por dominio)
│   ├── models/          # Interfaces TypeScript (refleja schemas backend)
│   ├── guards/          # Route guards
│   ├── interceptors/    # HTTP interceptors (auth, errors)
│   └── layouts/         # Layouts compartidos
├── auth/
├── tickets/
├── devices/
├── finance/
├── inventory/
├── client-portal/
└── shared/
    ├── components/      # Componentes reutilizables (loading, badge, modal)
    ├── pipes/
    └── directives/
```

## Naming
- Componentes: `kebab-case` para selector y archivo, `PascalCase` para clase. Sufijo `.component.ts` (estándar Angular CLI).
- Servicios: `*.service.ts`, clase `*Service`.
- Modelos/interfaces: `*.model.ts` o `*.ts` agrupados por dominio. Usar `interface Ticket`, **no** `interface ITicket`.
- Selectores de componentes: prefijo del proyecto `app-` (default Angular CLI).

## Componentes
- Standalone components por defecto (Angular 20).
- Plantilla, estilos y lógica en archivos separados (no inline) salvo componentes triviales.
- `OnPush` change detection donde sea viable.
- Inputs con tipos explícitos. Outputs con `EventEmitter<T>` tipado.
- Evitar lógica de negocio en componentes. Si la lógica crece, extraer a service.

## Estado y datos
- Servicios HTTP retornan `Observable<T>` (RxJS) por ahora; signals son aceptables para estado local del componente.
- No mezclar `subscribe` manual con `async` pipe en la misma plantilla.
- Cancelar suscripciones manuales con `takeUntilDestroyed()` (Angular 16+) o `Subject<void>` con `OnDestroy`.

## HTTP
- Un `HttpClient` por service.
- Centralizar el `baseUrl` de la API en `environments/environment.ts`.
- Un `AuthInterceptor` añade `Authorization: Bearer <token>` automáticamente.
- Un `ErrorInterceptor` mapea `error.error.message` y emite via `NotificationService` (toast/snackbar).

## Estilos
- CSS plano + variables globales en un único archivo (ej. `src/styles.css` o `src/styles/_tokens.css`).
- Tokens definidos:
  - Colores: paleta institucional (verde `#1a5c3a`, dorado `#c9a227`) + grays.
  - Sombras: `--shadow-sm`, `--shadow-md`, `--shadow-lg`.
  - Radii: `--radius-sm`, `--radius-md`, `--radius-lg`, `--radius-pill`.
  - Transiciones: `--transition-base`, `--transition-fast`.
- No hardcodear colores ni medidas mágicas en componentes; usar variables.
- Iconos: SVG inline en plantillas o sprite global. **No** emojis en UI seria.

## Accesibilidad
- Botones siempre como `<button>`, no `<div>` clicable.
- `aria-label` en iconos sin texto.
- Foco visible (no `outline: none` sin reemplazo).
- Contraste mínimo AA en texto sobre color.

## Formularios
- Reactive forms para todo lo que no sea trivial.
- Validadores de Angular (`Validators.*`) + validadores custom cuando aplique.
- Mensajes de error renderizados al lado del campo, no en alertas.

## Performance
- Lazy loading por feature module donde sea posible.
- `trackBy` en `*ngFor` con listas largas.
- Imágenes: `loading="lazy"` y dimensiones explícitas.
