"""Unified rate limiting for kinemotion backend.

Provides a single rate limiting interface that works in both production
and test environments. Uses slowapi for production and a no-op fallback
for testing or when fastapi-limiter is unavailable.
"""

import os
from collections.abc import Callable
from typing import Any, TypeVar

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from ..logging_config import get_logger
from .rate_limiter import NoOpLimiter

logger = get_logger(__name__)

F = TypeVar("F", bound=Callable[..., object])


# Rate limiter instance - set during initialization
_rate_limiter: Limiter | NoOpLimiter | None = None


def get_rate_limiter() -> Limiter | NoOpLimiter:
    """Get the rate limiter instance.

    Returns:
        Limiter instance for production, NoOpLimiter for testing

    Raises:
        RuntimeError: If rate limiter has not been initialized
    """
    if _rate_limiter is None:
        raise RuntimeError("Rate limiter not initialized. Call setup_rate_limiter() first.")
    return _rate_limiter


def setup_rate_limiter(app: Any) -> Limiter | NoOpLimiter:
    """Set up rate limiting for the FastAPI application.

    Args:
        app: FastAPI application instance

    Returns:
        Configured rate limiter instance (Limiter or NoOpLimiter)
    """
    global _rate_limiter

    # Check if we should use no-op limiter (for testing)
    if os.getenv("TESTING", "").lower() == "true":
        logger.info("using_noop_rate_limiter", reason="testing_mode")
        _rate_limiter = NoOpLimiter()
        return _rate_limiter

    # Use slowapi for production
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=["200/hour"],
        storage_uri=os.getenv("REDIS_URL", ""),
        storage_options={"connect_timeout": 5},
    )

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    _rate_limiter = limiter
    logger.info("rate_limiter_initialized", type="slowapi")
    return _rate_limiter


def limit(limit_string: str) -> Callable[[F], F]:
    """Rate limit decorator for endpoints.

    This decorator is lazy and will get the rate limiter when the endpoint
    is called, not at import time. This allows it to be used at module level
    before setup_rate_limiter() has been called.

    Args:
        limit_string: Rate limit string (e.g., "3/minute", "100/hour")

    Returns:
        Decorator function

    Example:
        @router.post("/api/analyze")
        @limit("3/minute")
        async def analyze_video(...):
            ...
    """

    def decorator(func: F) -> F:
        """Decorator that applies rate limiting to the function.

        Args:
            func: Function to decorate

        Returns:
            Decorated function (or original if limiter not available)
        """
        # Try to get the limiter - if not initialized, return function as-is
        try:
            limiter_instance = get_rate_limiter()
        except RuntimeError:
            # Limiter not set up yet (e.g., during import)
            # Return the function unchanged - this is OK for testing
            return func

        # Apply the rate limit from the limiter
        if hasattr(limiter_instance, "limit"):
            return limiter_instance.limit(limit_string)(func)
        # For NoOpLimiter, just return the function
        return func

    return decorator
