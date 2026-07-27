"""Application configuration.

Settings are loaded from environment variables (and a local .env file if
present) using pydantic-settings. Keeping config in one typed object means
the rest of the app never reads os.environ directly.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed application settings loaded from the environment."""

    # Human-readable name surfaced in the docs and health payload.
    app_name: str = "Task Tracker API"

    # Deployment environment: "development" or "production".
    app_env: str = "development"

    # Port the server should listen on when run via `python -m app.main`.
    port: int = 8000

    # Load values from a .env file; ignore any variables we do not define.
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


# A single, importable settings instance used across the app.
settings = Settings()
