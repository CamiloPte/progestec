# app/db/session.py

import time
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings

# ======================================================================
# 1. Crear el engine con reintentos
# ======================================================================

engine = None

# Número máximo de intentos para conectarse a la base de datos
MAX_RETRIES = 10
RETRY_DELAY_SECONDS = 3

for attempt in range(MAX_RETRIES):
    try:
        if not settings.DB_URL:
            raise ValueError("DB_URL is not set in the configuration.")

        # pool_pre_ping=True: chequea que la conexión esté viva antes de usarla
        # echo=False: si quieres debug SQL en consola, pon True
        engine = create_engine(
            settings.DB_URL,
            pool_pre_ping=True,
            echo=False,
        )

        # Abrimos y cerramos una conexión de prueba.
        with engine.connect() as connection:
            print("✅ Database connection established.")
        break

    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print(f"🔄 Retrying in {RETRY_DELAY_SECONDS} seconds... ({attempt + 1}/{MAX_RETRIES})")
        time.sleep(RETRY_DELAY_SECONDS)
else:
    # Si salimos del bucle sin break -> no hubo conexión exitosa
    raise ConnectionError("❌ Could not connect to the database after several attempts.")


# ======================================================================
# 2. Crear SessionLocal enlazada al engine
# ======================================================================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# ======================================================================
# 3. Dependencia para FastAPI: get_db()
# ======================================================================

def get_db() -> Generator[Session, None, None]:
    """
    Proporciona una sesión de base de datos para usar en rutas y servicios.
    Asegura que la sesión se cierre correctamente después del uso.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
