from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/ff"
    redis_url: str = "redis://localhost:6379/0"
    cache_ttl_seconds: int = 10


settings = Settings()
