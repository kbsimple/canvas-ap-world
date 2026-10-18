"""Configuration loaded from environment variables."""

import os

from dotenv import load_dotenv

load_dotenv()


class ConfigError(Exception):
    """Raised when required configuration is missing."""


def _require(name: str) -> str:
    value = os.environ.get(name, "")
    if not value:
        raise ConfigError(
            f"Missing required environment variable: {name}. "
            "Copy .env.example to .env and fill it in."
        )
    return value


class Config:
    """Canvas connection settings."""

    def __init__(self) -> None:
        self.api_url = _require("CANVAS_API_URL").rstrip("/")
        self.api_token = _require("CANVAS_API_TOKEN")
        self.course_id = os.environ.get("CANVAS_COURSE_ID", "")

    def ensure_course_id(self) -> str:
        """Return the configured course id, raising if it is missing."""
        if not self.course_id:
            raise ConfigError(
                "Missing required environment variable: CANVAS_COURSE_ID."
            )
        return self.course_id