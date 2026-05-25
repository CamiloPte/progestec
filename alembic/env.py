import os
import sys
from logging.config import fileConfig
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool

from alembic import context

# 1) Cargar variables de entorno
proj_root = Path(__file__).resolve().parent.parent
env_file = proj_root / ".env"
if env_file.exists():
    load_dotenv(env_file)

# 2) Incluir app en sys.path
sys.path.insert(0, str(proj_root))

# 3) Leer config de alembic.ini
config = context.config

# 4) Sobrescribir con DB_URL
db_url = os.getenv("DB_URL")
if not db_url:
    raise RuntimeError("La variable de entorno DB_URL no está definida")
config.set_main_option("sqlalchemy.url", db_url)

# 5) Logging
if config.config_file_name is not None:
    try:
        fileConfig(config.config_file_name)
    except KeyError:
        pass

# 6) Importar Base y todos los models
from app.db.base import Base  # <- IMPORTANTE: este ya importa todos los modelos vía __init__.py

target_metadata = Base.metadata


# 7) Métodos de migración
def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
