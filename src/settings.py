from pathlib import Path

import structlog
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = structlog.get_logger(__name__)


def create_path(folder_name: str) -> Path:
    """Creates and returns a path for storing data or logs."""
    path = Path(__file__).parent.resolve().parent / f"{folder_name}"
    path.mkdir(exist_ok=True)
    return path


class Settings(BaseSettings):
    """
    Global settings
    """

    gemini_api_key: str = ""

    input_path: Path = create_path("src")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


# Create a global settings instance
settings = Settings()
logger.debug("Settings have been initialized.", settings=settings.model_dump())
