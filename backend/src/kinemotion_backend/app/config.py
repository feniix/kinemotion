"""Configuration settings for Kinemotion backend."""

import os


class Settings:
    """Application settings."""

    # CORS settings
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
        "http://localhost:8888",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080",
        "http://127.0.0.1:8888",
    ]

    # Add production origins from environment variable if configured
    cors_origins_env = os.getenv("CORS_ORIGINS", "").strip()
    if cors_origins_env:
        # Split by comma and strip whitespace from each origin
        prod_origins = [origin.strip() for origin in cors_origins_env.split(",")]
        CORS_ORIGINS.extend(prod_origins)

    # R2 Storage settings
    R2_ENDPOINT: str = os.getenv("R2_ENDPOINT", "")
    R2_ACCESS_KEY: str = os.getenv("R2_ACCESS_KEY", "")
    R2_SECRET_KEY: str = os.getenv("R2_SECRET_KEY", "")
    R2_BUCKET_NAME: str = os.getenv("R2_BUCKET_NAME", "kinemotion")
    R2_PUBLIC_BASE_URL: str = os.getenv("R2_PUBLIC_BASE_URL", "").rstrip("/")
    R2_PRESIGN_EXPIRATION_S: int = int(os.getenv("R2_PRESIGN_EXPIRATION_S", "604800"))  # 7 days

    # Security settings
    TESTING: bool = os.getenv("TESTING", "").lower() == "true"
    TEST_PASSWORD: str = os.getenv("TEST_PASSWORD", "")
    ALLOWED_REFERERS: list[str] = [
        "https://kinemotion.vercel.app",
        "http://localhost:5173",
        "http://localhost:8888",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8888",
    ]

    # Add additional referers from environment variable
    referers_env = os.getenv("ALLOWED_REFERERS", "").strip()
    if referers_env:
        additional = [r.strip() for r in referers_env.split(",")]
        ALLOWED_REFERERS.extend(additional)

    # Logging settings
    JSON_LOGS: bool = os.getenv("JSON_LOGS", "false").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")


settings = Settings()
