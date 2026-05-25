## Catalog Service (Express + Supabase)

Microservicio para catálogo de dispositivos (fabricantes, modelos, variantes) que se alimenta de la base Postgres en Supabase.

### Configuración
1. Copia `.env.example` a `.env` y reemplaza `DATABASE_URL` con tu URI de Supabase (Primary Database, formato `postgresql://...`).
2. Instala dependencias:
   ```bash
   cd catalog-service
   npm install
   ```
3. Ejecuta en desarrollo:
   ```bash
   npm run dev
   ```
   En producción:
   ```bash
   npm start
   ```

### Rutas
- `GET /health` → estado del servicio.
- `GET /manufacturers` → lista de fabricantes.
- `GET /models?manufacturer_id={id}` → modelos (si no envías id, retorna todos).
- `GET /variants?model_id={id}` → variantes de un modelo (obligatorio model_id).

### Notas
- SSL está activado para Supabase (`rejectUnauthorized: false`).
- El seed inicial en Supabase incluye storage/ram/color en `device_variants`.

