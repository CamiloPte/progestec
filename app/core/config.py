# app/core/config.py
# [Revisión] Ver CHANGELOG_REVISION.md -> "app/core/config.py"

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # === Seguridad ===
    JWT_SECRET_KEY: str = "supersecretkey123"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # === Base de datos ===
    DB_HOST: str = "db"
    DB_PORT: int = 3306
    DB_USER: str = "user"
    DB_PASSWORD: str = "password"
    DB_NAME: str = "progestec_db"

    # Lo proporciona la URL completa de la base de datos. Si está vacío, se construye a partir de los otros parámetros.
    DB_URL: str = Field(default="", alias="DB_URL")

    # === Archivos / media ===
    MEDIA_ROOT: str = "uploads"
    MEDIA_URL: str = "/uploads"

    # === Email / SMTP ===
    MAIL_USERNAME: str = ""
    MAIL_PASSWORD: str = ""
    MAIL_FROM: str = ""
    MAIL_FROM_NAME: str = "ProGesTec - Servicio Técnico"
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    MAIL_USE_CREDENTIALS: bool = True
    MAIL_VALIDATE_CERTS: bool = True

    # === Configuración de la empresa ===
    COMPANY_NAME: str = "ProGesTec"
    COMPANY_PHONE: str = "+57 301 255-4106"
    COMPANY_EMAIL: str = ""
    COMPANY_ADDRESS: str = "Barranquilla, Colombia"
    COMPANY_WEBSITE: str = "https://progestec.com"

    # === Frontend URL (para links en emails) ===
    FRONTEND_URL: str = "http://localhost:4200"

    # === CORS ===
    ALLOW_ALL_ORIGINS: bool = True
    CORS_ORIGINS: str = "http://localhost:4200,http://127.0.0.1:4200"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.DB_URL:
            self.DB_URL = (
                f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}"
                f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            )
        Path(self.MEDIA_ROOT).mkdir(parents=True, exist_ok=True)

    @property
    def mail_enabled(self) -> bool:
        """Verifica si el email está configurado correctamente"""
        return bool(self.MAIL_USERNAME and self.MAIL_PASSWORD)


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
