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

    # Supabase settings (New API Key System - 2025+)
    supabase_url: str = "https://your-project.supabase.co"
    supabase_publishable_key: str = "sb_publishable_xxx"
    # Secret key: for admin operations (user deletion, password reset, etc.)
    supabase_secret_key: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore extra fields in .env
    )


settings = Settings()
