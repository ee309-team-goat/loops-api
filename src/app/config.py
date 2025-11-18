from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    app_name: str = "Loops API"
    app_version: str = "0.1.0"
    debug: bool = False

    # API settings
    api_v1_prefix: str = "/api/v1"

    # CORS settings
    allowed_origins: list[str] = ["*"]

    # Database settings
    database_url: str = "postgresql+asyncpg://user:password@localhost:5432/loops"
    database_echo: bool = False

    # JWT Authentication settings
    secret_key: str = (
        "your-secret-key-here-change-in-production"  # Change in production!
    )
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()
