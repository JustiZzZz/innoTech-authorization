from anyio.functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = 'innoTech-authorization'
    DEBUG: bool = False
    APP_BASE_URL: str = 'http://localhost:8000'

    SECRET_KEY: str = "super-secret-key-auth-min-32-chars-long-please-help-me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8

    DATABASE_URL: str = 'postgresql+asyncpg://postgres:postgres@localhost:5432/innotech_auth'

    SMTP_HOST: str = ''
    SMTP_PORT: str = ''
    SMTP_USER: str = ''
    SMTP_PASSWORD: str = ''
    SMTP_USE_TLS: bool = False

    EMAIL_SENDER_NAME: str = ''
    EMAIL_SENDER_ADDRESS: str = ''

@lru_cache
def get_settings():
    return Settings()
