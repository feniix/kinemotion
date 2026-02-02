"""Data models package for kinemotion backend."""

# Database models
from .database import (
    AnalysisSessionCreate,
    AnalysisSessionResponse,
    AnalysisSessionWithFeedback,
    CoachFeedbackCreate,
    CoachFeedbackResponse,
    DatabaseError,
)

# Error models
from .errors import (
    ERROR_AUTHENTICATION,
    ERROR_AUTHORIZATION,
    ERROR_INTERNAL,
    ERROR_NOT_FOUND,
    ERROR_RATE_LIMIT,
    ERROR_VALIDATION,
    ErrorDetail,
    ErrorResponse,
    create_error_response,
)

# Extracted models
from .responses import AnalysisResponse
from .storage import R2StorageClient

__all__ = [
    # Database models
    "AnalysisSessionCreate",
    "AnalysisSessionResponse",
    "AnalysisSessionWithFeedback",
    "CoachFeedbackCreate",
    "CoachFeedbackResponse",
    "DatabaseError",
    # Extracted models
    "AnalysisResponse",
    "R2StorageClient",
    # Error models
    "ErrorResponse",
    "ErrorDetail",
    "create_error_response",
    "ERROR_VALIDATION",
    "ERROR_AUTHENTICATION",
    "ERROR_AUTHORIZATION",
    "ERROR_NOT_FOUND",
    "ERROR_RATE_LIMIT",
    "ERROR_INTERNAL",
]
