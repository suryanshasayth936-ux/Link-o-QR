"""Application configuration using Pydantic Settings."""

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application runtime and security settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "Link'o'QR"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Security & Validation
    MAX_URL_LENGTH: int = 2048
    ALLOWED_CORS_ORIGINS: List[str] = ["*"]

    # QR Default Settings
    DEFAULT_BOX_SIZE: int = 10
    DEFAULT_BORDER: int = 4
    DEFAULT_ERROR_CORRECTION: str = "M"
    DEFAULT_FILL_COLOR: str = "#000000"
    DEFAULT_BACK_COLOR: str = "#ffffff"


settings = Settings()
