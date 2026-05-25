# app/db/base.py
from app.db.base_class import Base  
# Aquí importamos todos los modelos para que Alembic pueda detectarlos
from app.models import *
