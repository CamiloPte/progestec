# app/core/logger.py
import logging
import os
from logging.handlers import RotatingFileHandler

# Ruta del archivo de logs
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
LOG_FILE = os.path.join(LOG_DIR, "app.log")

# Crear el directorio de logs si no existe
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Configurar el logger
logger = logging.getLogger("app_logger")
logger.setLevel(logging.INFO)

# Evitar múltiples handlers al importar varias veces
if not logger.handlers:
    # Handler para archivo (con rotación)
    file_handler = RotatingFileHandler(LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3)
    file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Handler para consola
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter("%(levelname)s - %(message)s")
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
