"""Configuration settings for Kinemotion backend.

Uses Pydantic for validation and environment variable loading.
Settings are loaded at import time but without mutating class attributes.
"""

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _parse_list_env(value: str | None) -> list[str]:
    """Parse comma-separated environment variable into list.

    Args:
        value: Comma-separated string or None

    Returns:
        List of non-empty stripped strings
    """
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


class Settings(BaseSettings):
    """Application settings with Pydantic validation.

    Settings are loaded from environment variables with sensible defaults.
    No class-level mutations occur - all list processing happens at instance creation.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # ========== CORS Settings ==========
    CORS_ORIGINS_ENV: str | None = Field(
        default=None,
        alias="CORS_ORIGINS",
        description="Comma-separated list of additional CORS origins",
    )

    # ========== R2 Storage Settings ==========
    R2_ENDPOINT: str = Field(default="", description="Cloudflare R2 endpoint URL")
    R2_ACCESS_KEY: str = Field(default="", description="R2 access key")
    R2_SECRET_KEY: str = Field(default="", description="R2 secret key")
    R2_BUCKET_NAME: str = Field(default="kinemotion", description="R2 bucket name")
    R2_PUBLIC_BASE_URL: str = Field(
        default="",
        description="Public base URL for R2 objects (optional)",
    )
    R2_PRESIGN_EXPIRATION_S: int = Field(
        default=604800,
        description="Presigned URL expiration in seconds (default 7 days)",
    )

    # ========== Security Settings ==========
    TESTING: bool = Field(default=False, description="Test mode flag")
    TEST_PASSWORD: str = Field(default="", description="Test password for development")

    ALLOWED_REFERERS_ENV: str | None = Field(
        default=None,
        alias="ALLOWED_REFERERS",
        description="Comma-separated list of additional allowed referers",
    )

    # ========== Logging Settings ==========
    JSON_LOGS: bool = Field(default=False, description="Enable JSON log output")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")

    # ========== Environment ==========
    ENVIRONMENT: str = Field(default="development", description="Environment name")

    # Computed fields (set by model_validator)
    cors_origins: list[str] = Field(default_factory=list)
    allowed_referers: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _parse_list_fields(self) -> "Settings":
        """Parse list fields from environment variables.

        This runs after all individual field validation, so we have
        access to all field values.
        """
        # Parse CORS origins
        origins = [
            "http://localhost:3000",
            "http://localhost:5173",
            "http://localhost:8080",
            "http://localhost:8888",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:8080",
            "http://127.0.0.1:8888",
        ]
        if self.CORS_ORIGINS_ENV:
            origins.extend(_parse_list_env(self.CORS_ORIGINS_ENV))
        self.cors_origins = origins

        # Parse allowed referers
        referers = [
            "https://kinemotion.vercel.app",
            "http://localhost:5173",
            "http://localhost:8888",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:8888",
        ]
        if self.ALLOWED_REFERERS_ENV:
            referers.extend(_parse_list_env(self.ALLOWED_REFERERS_ENV))
        self.allowed_referers = referers

        return self

    @field_validator("R2_PUBLIC_BASE_URL", mode="before")
    @classmethod
    def _strip_public_base_url(cls, v: str) -> str:
        """Remove trailing slash from public base URL."""
        return v.rstrip("/")

    @field_validator("TESTING", mode="before")
    @classmethod
    def _parse_testing(cls, v: bool | str) -> bool:
        """Parse TESTING from string or bool."""
        if isinstance(v, bool):
            return v
        return str(v).lower() == "true"

    @field_validator("JSON_LOGS", mode="before")
    @classmethod
    def _parse_json_logs(cls, v: bool | str) -> bool:
        """Parse JSON_LOGS from string or bool."""
        if isinstance(v, bool):
            return v
        return str(v).lower() == "true"

    @property
    def cors_origins_property(self) -> list[str]:
        """Get CORS origins list."""
        return self.cors_origins

    @property
    def allowed_referers_property(self) -> list[str]:
        """Get allowed referers list."""
        return self.allowed_referers


# Global settings instance
settings = Settings()
