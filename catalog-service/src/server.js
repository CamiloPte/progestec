import dotenv from 'dotenv';
import express from 'express';
import cors from 'cors';
import pkg from 'pg';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Forzamos la ruta al .env dentro de catalog-service
dotenv.config({ path: path.join(__dirname, '../.env') });

const { Pool } = pkg;

// Usa la variable de entorno DATABASE_URL de Supabase
if (!process.env.DATABASE_URL) {
  console.error('DATABASE_URL not set. Please configure .env correctly.');
  process.exit(1);
}

console.log('Connecting to DB host:', new URL(process.env.DATABASE_URL).hostname);

// SSL solo si la URL contiene sslmode=require o es un host remoto (supabase, etc.)
// Para Postgres local (localhost) no se necesita SSL
const dbHost = new URL(process.env.DATABASE_URL).hostname;
const isLocalDb = dbHost === 'localhost' || dbHost === '127.0.0.1' || dbHost === 'catalog_db';

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: isLocalDb ? false : { rejectUnauthorized: false },
});

// No tumbar el servidor si la conexión de PG emite un error no manejado
pool.on('error', (err) => {
  console.error('Unexpected PG error', err);
});

const app = express();
app.use(cors());
app.use(express.json());

app.get('/health', (_req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

//obtenemos 
app.get('/manufacturers', async (_req, res) => {
  try {
    const { rows } = await pool.query(
      `select id, name, country, created_at
       from manufacturers
       order by name asc`
    );
    res.json(rows);
  } catch (err) {
    console.error('Error fetching manufacturers', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});


app.get('/models', async (req, res) => {
  const { manufacturer_id } = req.query;
  try {
    const params = [];
    let where = '';
    if (manufacturer_id) {
      params.push(Number(manufacturer_id));
      where = 'where manufacturer_id = $1';
    }
    const { rows } = await pool.query(
      `select id, manufacturer_id, name, category, released_year, created_at
       from device_models
       ${where}
       order by name asc`,
      params
    );
    res.json(rows);
  } catch (err) {
    console.error('Error fetching models', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.get('/variants', async (req, res) => {
  const { model_id } = req.query;
  if (!model_id) {
    return res.status(400).json({ error: 'model_id is required' });
  }
  try {
    console.log('DB URL:', process.env.DATABASE_URL);

    const { rows } = await pool.query(
      `select id, model_id, variant_name, sku, notes, storage_gb, ram_gb, color, created_at
       from device_variants
       where model_id = $1
       order by variant_name asc`,
      [Number(model_id)]
    );
    res.json(rows);
  } catch (err) {
    console.error('Error fetching variants', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

const PORT = process.env.PORT || 4000;
app.listen(PORT, () => {
  console.log(`Catalog service running on port ${PORT}`);
});
