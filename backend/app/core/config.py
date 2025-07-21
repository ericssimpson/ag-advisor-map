"""Application settings and configuration."""

import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Constants
LONG_QUERY_THRESHOLD = 200


class Settings(BaseModel):
    """Application settings."""

    openrouter_api_key: str
    app_url: str = "http://localhost:3000"
    allowed_origins: list[str]

    # Model settings
    default_model: str = "opengvlab/internvl3-2b:free"
    advanced_model: str = "google/gemini-2.0-flash-exp:free"
    fallback_model: str = "meta-llama/llama-3.2-3b-instruct:free"
    max_tokens: int = 1800
    token_safety_margin: int = 200


def load_settings() -> Settings:
    """Load settings from environment variables."""
    env_path = Path(__file__).parents[3] / "config" / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        logger.info("Loaded environment from %s", env_path)
    else:
        logger.warning("No .env file in config folder; using environment variables.")

    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
    if not openrouter_api_key:
        error_msg = "OPENROUTER_API_KEY environment variable is not set."
        logger.error(error_msg)
        raise ValueError(error_msg)

    allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000")
    allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",")]

    return Settings(
        openrouter_api_key=openrouter_api_key,
        app_url=os.getenv("APP_URL", "http://localhost:3000"),
        allowed_origins=allowed_origins,
    )


settings = load_settings()
