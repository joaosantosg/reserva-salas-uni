from typing import List
from pydantic import SecretStr, PostgresDsn
from pydantic_settings import BaseSettings
from datetime import timedelta


class Settings(BaseSettings):
    """Configurações da aplicação usando Pydantic"""

    # Environment
    ENV: str = "dev"
    API_V1_STR: str = "/api/v1"

    # API
    PROJECT_NAME: str = "Reserva Salas UNI"
    DEBUG: bool = True if ENV == "dev" else False

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    ALLOW_CREDENTIALS: bool = True
    ALLOW_METHODS: List[str] = ["*"]
    ALLOW_HEADERS: List[str] = ["*"]

    # Mailgun
    MAILGUN_API_KEY: str
    MAILGUN_DOMAIN: str

    # Database - valores default que serão sobrescritos pelo .env
    DB: str
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str

    @property
    def DATABASE_URL(self) -> PostgresDsn:
        """Retorna a URL de conexão do banco de dados"""
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # JWT
    SECRET_KEY: SecretStr = (
        "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    )

    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 24 * 60  # 1 dia

    REFRESH_TOKEN_EXPIRE_MINUTES: int = 24 * 60 * 7
    # Timezone
    TIMEZONE: str = "America/Sao_Paulo"

    @property
    def access_token_expires(self) -> timedelta:
        """Retorna o tempo de expiração do token de acesso"""
        return timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)

    @property
    def refresh_token_expires(self) -> timedelta:
        """Retorna o tempo de expiração do token de refresh"""
        return timedelta(minutes=self.REFRESH_TOKEN_EXPIRE_MINUTES)

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"


# Instância global das configurações
settings = Settings()
