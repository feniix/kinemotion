"""Custom exceptions for kinemotion backend."""


class KinemotionError(Exception):
    """Base exception for kinemotion application."""

    pass


class VideoProcessingError(KinemotionError):
    """Exception raised when video processing fails."""

    pass


class ValidationError(KinemotionError):
    """Exception raised when input validation fails."""

    pass


class StorageError(KinemotionError):
    """Exception raised when storage operations fail."""

    pass
