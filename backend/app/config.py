from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/erp_portal"
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    APP_NAME: str = "Meridian Campus ERP"
    DEBUG: bool = False
    SEED_RESET: bool = False
    DEMO_SANDBOX: bool = True
    DEMO_TENANT_TTL_HOURS: int = 24
    # Fixed personal/shared tenant when DEMO_SANDBOX is false
    MASTER_TENANT_ID: str = "00000000-0000-4000-8000-000000000001"
    CORS_ORIGINS: str = (
        "http://localhost:8501,http://127.0.0.1:8501,"
        "http://localhost:5173,http://127.0.0.1:5173"
    )
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
