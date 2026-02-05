"""Configuration settings for Clora service."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # GLM API
    glm_api_key: str = ""
    glm_api_base_url: str = "https://api.z.ai/api/coding/paas/v4"
    glm_model: str = "glm-4.7"
    glm_vision_model: str = "glm-4.6v"

    # Database
    database_url: str = "sqlite+aiosqlite:///./clora.db"

    # ChromaDB
    chroma_persist_dir: str = "./chroma_db"

    # JWT
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False

    # AI Settings
    default_max_tokens: int = 4096
    default_temperature: float = 0.7
    thinking_mode: str = "enabled"  # "enabled" or "disabled"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
