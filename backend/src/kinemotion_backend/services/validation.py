import os
from pathlib import Path

from fastapi import HTTPException, UploadFile, status


def validate_video_file(file: UploadFile) -> None:
    """Validate uploaded video file.

    Args:
        file: Uploaded file to validate

    Raises:
        ValueError: If file is invalid
    """
    if not file.filename:
        raise ValueError("File must have a name")

    # Check file extension
    valid_extensions = {".mp4", ".avi", ".mov", ".mkv", ".flv", ".wmv"}
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in valid_extensions:
        raise ValueError(
            f"Invalid video format: {file_ext}. Supported formats: {', '.join(valid_extensions)}"
        )

    # Check file size if available (UploadFile.size is often None in test client)
    # We'll rely on the analysis service to check actual content size
    if file.size and file.size > 500 * 1024 * 1024:
        raise ValueError("File size exceeds maximum of 500MB")


def validate_jump_type(jump_type: str) -> str:
    """Validate jump type parameter (case-insensitive).

    Args:
        jump_type: Jump type to validate

    Returns:
        Normalized jump type (lowercase)

    Raises:
        ValueError: If jump type is invalid
    """
    normalized = jump_type.lower()
    valid_types: set[str] = {"drop_jump", "cmj"}
    if normalized not in valid_types:
        raise ValueError(
            f"Invalid jump type: {jump_type}. Must be one of: {', '.join(valid_types)}"
        )
    return normalized


def is_test_password_valid(x_test_password: str | None = None) -> bool:
    """Check if test password is valid (for debugging backdoor).

    Args:
        x_test_password: Optional test password header

    Returns:
        True if test password is configured and matches
    """
    test_password = os.getenv("TEST_PASSWORD")
    return bool(test_password and x_test_password == test_password)


def validate_referer(referer: str | None, x_test_password: str | None = None) -> None:
    """Validate request comes from authorized frontend.

    Args:
        referer: Referer header from request
        x_test_password: Optional test password header for debugging

    Raises:
        HTTPException: If referer is missing or not from allowed origins
    """
    # Skip validation in test mode
    if os.getenv("TESTING", "").lower() == "true":
        return

    # Allow bypass with test password (for curl testing, debugging)
    if is_test_password_valid(x_test_password):
        return  # Bypass referer check

    allowed_referers = [
        "https://kinemotion.vercel.app",
        "http://localhost:5173",
        "http://localhost:8888",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8888",
    ]

    # Allow additional referers from env var
    referer_env = os.getenv("ALLOWED_REFERERS", "").strip()
    if referer_env:
        additional = [r.strip() for r in referer_env.split(",")]
        allowed_referers.extend(additional)

    if not referer:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Direct API access not allowed. Use the web interface.",
        )

    # Check if referer starts with any allowed origin
    referer_valid = any(referer.startswith(origin) for origin in allowed_referers)

    if not referer_valid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Request must originate from authorized frontend",
        )
