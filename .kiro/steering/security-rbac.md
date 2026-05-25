# Seguridad y RBAC

## Principios
1. **Negar por defecto**: si una ruta no declara explícitamente quién puede usarla, nadie puede.
2. **Defensa en capas**: la validación de rol vive en el backend (autoridad). El frontend la respeta para UX, no para seguridad.
3. **Token mínimo**: el JWT lleva solo lo necesario (`user_id`, `role_name`, `exp`). Datos del usuario se resuelven en cada request.
4. **Trazabilidad**: cualquier mutación crítica deja registro (history o audit log).

## Roles definidos
Codificados en `app/core/roles.py`:
- `ADMIN`
- `ADVISOR`
- `TECHNICIAN`
- `CLIENT`
- `COURIER`

## Matriz de permisos
La fuente canónica es `docs/ESTADO_ACTUAL_PROYECTO.md` sección 3.2. Resumen:

| Acción | ADMIN | ADVISOR | TECHNICIAN | CLIENT | COURIER |
|--------|:-----:|:-------:|:----------:|:------:|:-------:|
| Ver todos los tickets | ✅ | ✅ | ❌ | ❌ | ❌ |
| Ver tickets propios (cliente) | ✅ | ✅ | — | ✅ | — |
| Crear ticket | ✅ | ✅ | ❌ | ❌ | ❌ |
| Asignar técnico | ✅ | ✅ | ❌ | ❌ | ❌ |
| Auto-asignarse ticket | ❌ | ❌ | ✅ | ❌ | ❌ |
| Cambiar estado de ticket | ✅ | ✅ | ✅* | ❌* | ❌ |
| Aprobar/rechazar presupuesto | ❌ | ❌ | ❌ | ✅ | ❌ |
| Generar factura | ✅ | ✅ | ❌ | ❌ | ❌ |
| Registrar pago | ✅ | ✅ | ❌ | ❌ | ❌ |
| Registrar gasto | ✅ | ✅ | ❌ | ❌ | ❌ |
| CRUD usuarios | ✅ | ❌ | ❌ | ❌ | ❌ |
| Ver dashboard financiero | ✅ | ✅ | ❌ | ❌ | ❌ |

\* Sujeto a transiciones permitidas. Ver `app/core/ticket_status_transitions.py`.

## Transiciones de estado de ticket
Definidas en `app/core/ticket_status_transitions.py`. Reglas resumidas:
- Flujo principal: `RECEIVED → DIAGNOSING → WAITING_APPROVAL → REPAIRING → READY → DELIVERED → CLOSED`.
- `CANCELLED` se puede alcanzar desde casi cualquier estado activo.
- `CLIENT` solo puede transitar `WAITING_APPROVAL → REPAIRING` (aprobar) o `WAITING_APPROVAL → CANCELLED` (rechazar).
- `ADMIN` tiene rutas excepcionales (reabrir cerrados, retroceder de DELIVERED a READY).
- Cualquier endpoint que cambie estado **debe** pasar por `is_valid_transition(...)`.

## Implementación

### Dependencia base
```python
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    ...
```

### Helper de roles
```python
def require_roles(*allowed: str):
    def checker(user: User = Depends(get_current_user)) -> User:
        if not user_has_role(user, *allowed):
            raise HTTPException(403, "No tienes permiso para esta acción")
        return user
    return checker
```

### Uso en routes
```python
@router.post("/", response_model=TicketRead, status_code=201)
def create_ticket(
    payload: TicketCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(ROLE_ADMIN, ROLE_ADVISOR)),
):
    return ticket_service.create(db, payload, created_by=user)
```

## Datos sensibles
- Contraseñas: hash con `passlib[bcrypt]`. Nunca log, nunca devolver en schema Read.
- Tokens: nunca log. No persistir refresh tokens en plano si los implementamos (hash o cifrado).
- PII (cédulas, teléfonos): tratar con cuidado en logs y respuestas amplias.

## Subida de archivos
- Validar `content-type` y extensión.
- Limitar tamaño en el route con `Form`/`UploadFile` y check explícito.
- Guardar con UUID como nombre, **nunca** con el nombre original (evita path traversal).
- Servir solo a usuarios autorizados (el `StaticFiles` actual es público; si hay archivos sensibles, mover a endpoint con auth).

## Auditoría (a implementar)
A definir en spec dedicada. Mínimo:
- Tabla `audit_log` con `user_id`, `action`, `entity_type`, `entity_id`, `before`, `after`, `at`.
- Acciones críticas: cambio de rol, eliminación de usuario, cancelación de factura, modificación de pago.

## Variables de entorno sensibles
- `JWT_SECRET_KEY`: aleatorio, mínimo 32 chars. Rotar si hay sospecha de compromiso.
- `MAIL_PASSWORD`: app-password (Gmail) o credencial dedicada.
- `DB_PASSWORD`: nunca por defecto en producción.
- Ningún `.env` real va al repo. Solo `.env.example` con placeholders.
