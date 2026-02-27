from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Base de données
    DATABASE_URL: str = "postgresql+asyncpg://gescom:gescom_password@localhost:5432/gescom"
    DATABASE_URL_SYNC: str = "postgresql://gescom:gescom_password@localhost:5432/gescom"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Sécurité
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    # Application
    APP_NAME: str = "GesCom"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
