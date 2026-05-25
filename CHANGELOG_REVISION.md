# Revisión técnica del proyecto ProGesTec

Este documento resume los errores detectados durante la revisión del backend y los cambios aplicados para corregirlos. Cada archivo modificado incluye en su encabezado una referencia corta (`[Revisión] Ver CHANGELOG_REVISION.md -> "<sección>"`) que apunta aquí para evitar ensuciar el código con comentarios largos.

---

## Resumen de cambios aplicados

| # | Archivo                               | Tipo              | Estado     |
|---|---------------------------------------|-------------------|------------|
| 1 | `app/db/__init.py` → `app/db/__init__.py` | Bug / estructura  | Corregido  |
| 2 | `Dockerfile`                          | Bug / build       | Corregido  |
| 3 | `alembic.ini`                         | Configuración     | Corregido  |
| 4 | `app/core/config.py`                  | Configuración     | Corregido  |
| 5 | `app/main.py`                         | Configuración     | Corregido  |
| 6 | `app/core/exceptions.py`              | Mejora / UX       | Mejorado   |

---

## 1. `app/db/__init__.py` (antes `app/db/__init.py`)

### Problema
El archivo estaba mal nombrado: `__init.py` en lugar de `__init__.py` (faltaba un guion bajo). Python no reconocía `app/db` como paquete, lo que podía romper imports (`from app.db ...`) y el descubrimiento de módulos por parte de Alembic.

### Cambio aplicado
Renombrado a `app/db/__init__.py`. El archivo queda vacío (se usa solo como marcador de paquete, el resto del setup vive en `app/db/base.py`, `app/db/base_class.py` y `app/db/session.py`).

### Efecto
- `from app.db.base import Base` y similares quedan garantizados.
- `alembic/env.py` puede importar correctamente `Base` para autogenerar migraciones.

---

## 2. `Dockerfile`

### Problema
Había dos defectos:

1. `COPY ./app /app` copiaba el **contenido** de la carpeta `app/` a `/app`, lo que rompía la estructura de paquete: `uvicorn app.main:app` espera encontrar un paquete Python llamado `app` dentro de `PYTHONPATH`, pero al copiar así, los módulos (`main.py`, `core/`, `api/`, …) quedaban sueltos en `/app` y no en `/app/app/`.
2. La imagen no incluía `alembic/` ni `alembic.ini`, así que dentro del contenedor no se podían correr migraciones sin el bind mount del `docker-compose.yml`.

Esto no se notaba en desarrollo porque `docker-compose.yml` monta toda la raíz con `volumes: - .:/app`, "tapando" la imagen. Pero la imagen por sí sola quedaba inservible (problema para producción o despliegues sin bind mount).

### Cambio aplicado
```dockerfile
COPY ./app /app/app
COPY ./alembic /app/alembic
COPY alembic.ini /app/alembic.ini
```

- `./app` se copia como subcarpeta `/app/app`, preservando la estructura del paquete Python.
- Se incluyen `alembic/` y `alembic.ini` para que `alembic upgrade head` funcione dentro de la imagen.

### Efecto
- `uvicorn app.main:app` resuelve correctamente sin depender del volumen de compose.
- Las migraciones funcionan dentro del contenedor también en producción.
- El flujo actual (`docker compose up` con bind mount) sigue igual.

### Notas
- Se descartó agregar dependencias del sistema (`build-essential`, `libffi-dev`, `default-libmysqlclient-dev`) para no engordar la imagen: `PyMySQL` es puro Python y las wheels precompiladas de `cryptography`/`bcrypt` ya cubren `python:3.11-slim`.
- No se agregó `COPY . /app` para evitar que la imagen del backend incluyera `progestec-front/`, `catalog-service/`, `docs/`, `backup/`, etc.

---

## 3. `alembic.ini`

### Problema
El archivo estaba incompleto y contenía una directiva inválida:

```ini
[alembic]
script_location = alembic

log_file = alembic.log
logfile = True
```

- `logfile = True` no es una directiva reconocida por Alembic.
- Faltaba la sección `[loggers]` y relacionadas, que normalmente acompañan al `alembic.ini` para que la configuración de logging no falle.
- `sqlalchemy.url` no estaba declarado (aunque `alembic/env.py` lo sobrescribe vía `DB_URL`, dejarlo vacío explícito evita warnings).

### Cambio aplicado
Se reemplazó por una versión mínima y estándar:

```ini
[alembic]
script_location = alembic
sqlalchemy.url =

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARNING
handlers = console
qualname =

[logger_sqlalchemy]
level = WARNING
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

### Efecto
- Sin directivas inválidas.
- Logging de Alembic configurado correctamente.
- La URL sigue inyectándose en tiempo de ejecución desde `alembic/env.py` a partir de la variable `DB_URL`.

---

## 4. `app/core/config.py`

### Problema
La configuración de CORS estaba hardcodeada en `app/main.py` (flag `allow_all_origins = True` y una IP local `192.168.1.60`). No era ajustable por entorno.

### Cambio aplicado
Se añadieron dos settings al `Settings` de Pydantic y un helper:

```python
# === CORS ===
ALLOW_ALL_ORIGINS: bool = True
CORS_ORIGINS: str = "http://localhost:4200,http://127.0.0.1:4200"

@property
def cors_origins_list(self) -> list[str]:
    return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]
```

### Efecto
- En desarrollo sigue funcionando igual porque el default es `True`.
- En producción basta con definir en `.env`:
  ```
  ALLOW_ALL_ORIGINS=false
  CORS_ORIGINS=https://app.progestec.com,https://admin.progestec.com
  ```
- Se elimina la dependencia de una IP local concreta dentro del código.

---

## 5. `app/main.py`

### Problema
- Tenía código muerto / IP local hardcodeada (`192.168.1.60`).
- Duplicaba lógica que ya cabe en `settings`.
- Mezclaba la definición de orígenes con el middleware.

### Cambio aplicado
- La construcción del middleware CORS ahora toma los valores desde `settings`:
  ```python
  app.add_middleware(
      CORSMiddleware,
      allow_origins=["*"] if settings.ALLOW_ALL_ORIGINS else settings.cors_origins_list,
      allow_credentials=True,
      allow_methods=["*"],
      allow_headers=["*"],
  )
  ```
- Se eliminaron los comentarios obsoletos y la lista `origins` hardcodeada.
- Se reordenaron los imports (agrupando FastAPI/Starlette primero, luego internos del proyecto).

### Efecto
- `main.py` queda claramente enfocado en montar la app, middlewares, routers y handlers.
- Para ajustar CORS ya no hay que editar código, solo `.env`.

---

## 6. `app/core/exceptions.py`

### Problema
Los exception handlers devolvían respuestas inconsistentes:
- Solo un campo `{"detail": "..."}` sin estructura clara.
- No diferenciaban tipos de error para el frontend (401 vs 403 vs 404 vs 500).
- Los errores de validación de Pydantic (422) no tenían handler dedicado, mostrando el formato crudo de FastAPI.
- Faltaba timestamp y path para correlacionar errores con logs.

### Cambio aplicado
Se reestructuraron los tres handlers:

**1. `http_exception_handler` (401, 403, 404, etc.)**
```json
{
  "error": {
    "type": "Unauthorized",
    "code": 401,
    "message": "Invalid credentials",
    "timestamp": "2025-05-07T14:32:10.123456Z",
    "path": "/auth/login"
  }
}
```

**2. `validation_exception_handler` (422 - errores de Pydantic)**
```json
{
  "error": {
    "type": "ValidationError",
    "code": 422,
    "message": "Validation failed",
    "details": [
      {
        "field": "body -> email",
        "message": "value is not a valid email address",
        "type": "value_error.email"
      }
    ],
    "timestamp": "2025-05-07T14:32:10.123456Z",
    "path": "/auth/register"
  }
}
```

**3. `generic_exception_handler` (500 - errores inesperados)**
```json
{
  "error": {
    "type": "InternalServerError",
    "code": 500,
    "message": "An unexpected error occurred. Please try again later.",
    "timestamp": "2025-05-07T14:32:10.123456Z",
    "path": "/tickets/123"
  }
}
```

Se agregó función helper `_build_error_response()` para mantener consistencia.

### Efecto
- **Frontend recibe formato predecible**: siempre `error.type`, `error.code`, `error.message`.
- **Errores de validación claros**: el campo `details` lista exactamente qué campos fallaron y por qué.
- **Mejor debugging**: `timestamp` y `path` permiten correlacionar con logs del backend.
- **Mapeo de tipos**: 401 → "Unauthorized", 403 → "Forbidden", 404 → "NotFound", etc.
- **Logging mejorado**: incluye método HTTP y path en cada log.

### Integración en `main.py`
Se registró el nuevo handler:
```python
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)
```

---

## Recomendaciones pendientes (no aplicadas aún)

Estos puntos se detectaron pero no se tocaron para mantener los cambios mínimos. Se sugiere atacarlos en una siguiente iteración:

1. **Secretos versionados (`.env`)**
   - `JWT_SECRET_KEY=supersecretkey123` es trivial; debe ser una clave aleatoria fuerte (`openssl rand -hex 32`).
   - La contraseña de Gmail (`MAIL_PASSWORD`) está expuesta en el repositorio.
   - No existe `.gitignore` en la raíz; `.env` podría ser commiteado sin querer.
   - **Acción sugerida**: crear `.env.example` (sin secretos), agregar `.gitignore` con `.env`, rotar las credenciales expuestas.

2. **Validaciones en `POST /auth/register`**
   - No valida fuerza de contraseña (el endpoint acepta cualquier string; solo `/auth/set-password` exige mínimo 6 caracteres).
   - No valida que `role_id` exista ni que el solicitante tenga permiso para asignarlo (un cliente podría auto-asignarse ADMIN).
   - No valida unicidad de `identification`.

3. **Manejo transaccional en `BootstrapService.bootstrap`**
   - Si una inserción falla a la mitad, no hay rollback explícito y el estado de la base puede quedar inconsistente.

4. **`docker-compose.yml`**
   - Contraseñas triviales (`user`/`password`, `rootpassword`, `catalog`/`catalog`) hardcodeadas; conviene sacarlas a `.env`.
   - El puerto MySQL externo es 3307 pero `DB_PORT=3306` interno: documentar para evitar confusión al conectar con cliente externo.

5. **Consistencia de tipos en migraciones**
   - Algunas migraciones usan `sa.Integer()` para `state` y otras `mysql.TINYINT(1)`. No rompe nada, pero conviene uniformar.
