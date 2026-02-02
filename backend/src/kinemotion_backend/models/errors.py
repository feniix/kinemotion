"""Unified error response models for kinemotion backend."""

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """Detailed error information."""

    field: str | None = Field(None, description="Field that caused the error")
    message: str = Field(..., description="Error message for the field")
    type: str | None = Field(None, description="Type of validation error")


class ErrorResponse(BaseModel):
    """Standard error response format for all API endpoints.

    Ensures consistent error structure across the application for better
    client-side error handling and logging.
    """

    status_code: int = Field(..., description="HTTP status code")
    message: str = Field(..., description="Human-readable error message")
    error_code: str | None = Field(None, description="Machine-readable error code")
    detail: str | None = Field(None, description="Detailed error information")
    path: str | None = Field(None, description="Request path where error occurred")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="ISO timestamp when error occurred",
    )
    extra: dict[str, Any] | None = Field(None, description="Additional error context")
    errors: list[ErrorDetail] = Field(
        default_factory=list,
        description="Field-specific validation errors",
    )
    retry_after: int | None = Field(None, description="Seconds until retry is allowed")


def create_error_response(
    *,
    status_code: int,
    message: str,
    error_code: str | None = None,
    detail: str | None = None,
    path: str | None = None,
    extra: dict[str, Any] | None = None,
    errors: list[ErrorDetail] | None = None,
    retry_after: int | None = None,
) -> ErrorResponse:
    """Factory function to create standardized error responses.

    Args:
        status_code: HTTP status code
        message: Human-readable error message
        error_code: Optional machine-readable error code
        detail: Optional detailed error information
        path: Optional request path
        extra: Optional additional context
        errors: Optional field-specific validation errors
        retry_after: Optional seconds until retry

    Returns:
        ErrorResponse instance
    """
    return ErrorResponse(
        status_code=status_code,
        message=message,
        error_code=error_code,
        detail=detail,
        path=path,
        extra=extra,
        errors=errors or [],
        retry_after=retry_after,
    )


# Common error code constants
ERROR_VALIDATION = "VALIDATION_ERROR"
ERROR_AUTHENTICATION = "AUTHENTICATION_ERROR"
ERROR_AUTHORIZATION = "AUTHORIZATION_ERROR"
ERROR_NOT_FOUND = "NOT_FOUND"
ERROR_RATE_LIMIT = "RATE_LIMIT_EXCEEDED"
ERROR_INTERNAL = "INTERNAL_ERROR"
