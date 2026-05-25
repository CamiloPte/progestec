# Scripts de despliegue — ProGesTec

Todos los `.bat` se ejecutan haciendo doble clic o desde cmd.

## Primera vez (setup inicial)

Ejecuta en este orden:

1. **`01-start-docker.bat`** — Levanta los contenedores (FastAPI + MySQL + Postgres)
2. **`02-init-db.bat`** — Crea tablas y carga datos iniciales (roles, estados, admin)
3. **`03-restore-catalog.bat`** — Restaura el backup del catálogo de Supabase
   (solo si tienes un archivo `.backup` en la carpeta `backup/`)
4. **`04-start-catalog.bat`** — Arranca el microservicio de catálogo (puerto 5000)
5. **`05-start-frontend.bat`** — Arranca Angular (puerto 4200)

Los pasos 4 y 5 abren dos ventanas que deben quedar abiertas mientras uses el sistema.

## Uso diario

Después del setup inicial, cada vez que quieras usar el sistema:

- **`start-all.bat`** — Levanta Docker + abre catalog y frontend en ventanas separadas
- **`stop-all.bat`** — Detiene los contenedores Docker (los Node hay que cerrarlos con Ctrl+C)

## Otros

- **`reset-db.bat`** — Borra toda la base de datos de ProGesTec y la recrea desde cero.
  No afecta al catálogo. Útil cuando algo se corrompe.

## Credenciales por defecto

Después de correr `02-init-db.bat`:

- **Email:** `admin@progestec.com`
- **Password:** `Admin123!`

## URLs

| Servicio | URL local |
|----------|-----------|
| Frontend | http://localhost:4200 |
| Backend API | http://localhost:8000 |
| Swagger | http://localhost:8000/docs |
| Catalog | http://localhost:5000 |

Para que otros equipos se conecten en la red, reemplaza `localhost` por tu IP
(mostrada al arrancar el frontend).
