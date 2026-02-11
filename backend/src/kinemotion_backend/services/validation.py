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


CANONICAL_JUMP_TYPES: set[str] = {"cmj", "drop_jump", "sj"}

JUMP_TYPE_ALIASES: dict[str, str] = {
    "squat_jump": "sj",
}


def validate_jump_type(jump_type: str) -> str:
    """Validate and normalize jump type parameter (case-insensitive).

    Accepts canonical types ("cmj", "drop_jump", "sj") and known aliases
    ("squat_jump" -> "sj"). Returns the canonical form so downstream code
    only needs to handle three values.

    Args:
        jump_type: Jump type to validate

    Returns:
        Canonical jump type string (lowercase)

    Raises:
        ValueError: If jump type is invalid
    """
    normalized = jump_type.lower()
    normalized = JUMP_TYPE_ALIASES.get(normalized, normalized)
    if normalized not in CANONICAL_JUMP_TYPES:
        raise ValueError(
            f"Invalid jump type: {jump_type}. "
            f"Must be one of: {', '.join(sorted(CANONICAL_JUMP_TYPES))}"
        )
    return normalized


def is_test_password_valid(x_test_password: str | None = None) -> bool:
    """Check if test password is valid (for debugging backdoor).

    Args:
        x_test_password: Optional test password header

    Returns:
        True if test password is configured and matches
    """
    # Read directly from environment for test compatibility
    # (tests set env vars after module import)
    test_password = os.getenv("TEST_PASSWORD", "")
    return bool(test_password and x_test_password == test_password)


VALID_SEX_VALUES: set[str] = {"male", "female"}
VALID_TRAINING_LEVELS: set[str] = {
    "untrained",
    "recreational",
    "trained",
    "competitive",
    "elite",
}


def validate_demographics(
    sex: str | None,
    age: int | None,
    training_level: str | None,
) -> tuple[str | None, str | None]:
    """Validate and normalize demographic parameters.

    Args:
        sex: Biological sex (case-insensitive "male" or "female")
        age: Athlete age in years (1-120)
        training_level: Training level string

    Returns:
        Tuple of (normalized_sex, normalized_training_level), each lowercase or None.

    Raises:
        ValueError: If any parameter is invalid
    """
    if sex is not None and sex.lower() not in VALID_SEX_VALUES:
        raise ValueError(f"Invalid sex value '{sex}'. Must be 'male' or 'female'.")

    if age is not None and (age < 1 or age > 120):
        raise ValueError(f"Invalid age value {age}. Must be between 1 and 120.")

    if training_level is not None and training_level.lower() not in VALID_TRAINING_LEVELS:
        raise ValueError(
            f"Invalid training_level '{training_level}'. "
            f"Must be one of: {', '.join(sorted(VALID_TRAINING_LEVELS))}."
        )

    normalized_sex = sex.lower() if sex else None
    normalized_training_level = training_level.lower() if training_level else None
    return normalized_sex, normalized_training_level


def validate_referer(referer: str | None, x_test_password: str | None = None) -> None:
    """Validate request comes from authorized frontend.

    Args:
        referer: Referer header from request
        x_test_password: Optional test password header for debugging

    Raises:
        HTTPException: If referer is missing or not from allowed origins
    """
    from ..app.config import settings

    # Skip validation in test mode (read directly for test compatibility)
    if os.getenv("TESTING", "").lower() == "true":
        return

    # Allow bypass with test password (for curl testing, debugging)
    if is_test_password_valid(x_test_password):
        return

    if not referer:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Direct API access not allowed. Use the web interface.",
        )

    # Check if referer starts with any allowed origin
    referer_valid = any(
        referer.startswith(origin) for origin in settings.allowed_referers_property
    )

    if not referer_valid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Request must originate from authorized frontend",
        )
