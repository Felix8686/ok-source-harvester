from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class CollectorSettings(BaseModel):
    concurrency: int = Field(default=8, ge=1, le=64)
    request_timeout_seconds: float = Field(default=15.0, gt=0, le=120)


class GitHubCollectorSettings(BaseModel):
    code_search_enabled: bool = True
    per_page: int = Field(default=30, ge=1, le=100)
    max_pages: int = Field(default=2, ge=1, le=10)
    max_repositories_per_query: int = Field(default=20, ge=1, le=100)
    max_files_per_repository: int = Field(default=12, ge=1, le=100)
    rate_limit_reserve: int = Field(default=5, ge=0, le=100)
    search_queries: tuple[str, ...] = (
        "TVBox 配置",
        "TVBox 接口",
        "OK影视",
        "影视仓 接口",
        "猫影视 配置",
        "catvod config",
    )
    candidate_path_terms: tuple[str, ...] = (
        "tvbox",
        "config",
        "api",
        "source",
        "影视",
        "接口",
    )


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
    github: GitHubCollectorSettings = GitHubCollectorSettings()
    validator: ValidatorSettings = ValidatorSettings()

    def sqlite_path(self) -> Path:
        prefix = "sqlite:///"
        if not self.database_url.startswith(prefix):
            raise ValueError("Phase 1 CLI currently requires a sqlite:/// database URL")
        return Path(self.database_url.removeprefix(prefix))


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
