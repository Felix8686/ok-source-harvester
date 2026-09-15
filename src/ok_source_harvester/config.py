from functools import lru_cache
from typing import Literal

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class CollectorSettings(BaseModel):
    concurrency: int = Field(default=8, ge=1, le=64)
    request_timeout_seconds: float = Field(default=15.0, gt=0, le=120)


class ValidatorSettings(BaseModel):
    request_timeout_seconds: float = Field(default=12.0, gt=0, le=120)
    max_retries: int = Field(default=2, ge=0, le=10)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="OSH_",
        env_file=".env",
        env_nested_delimiter="__",
        extra="ignore",
    )

    environment: Literal["development", "production", "test"] = "development"
    database_url: str = "sqlite:///data/harvester.db"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    user_agent: str = "ok-source-harvester/0.1"
    github_token: str | None = None
    collector: CollectorSettings = CollectorSettings()
    validator: ValidatorSettings = ValidatorSettings()


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
