"""Custom exceptions for kinemotion backend."""


class KinemotionError(Exception):
    """Base exception for kinemotion application."""


class VideoProcessingError(KinemotionError):
    """Exception raised when video processing fails."""


class ValidationError(KinemotionError):
    """Exception raised when input validation fails."""


class StorageError(KinemotionError):
    """Exception raised when storage operations fail."""
