from typing import Any


class NoOpLimiter:
    """No-op limiter for testing."""

    def limit(self, limit_string: str) -> Any:  # type: ignore[no-untyped-def]
        """Decorator that does nothing."""

        def decorator(func: Any) -> Any:  # type: ignore[no-untyped-def]
            return func

        return decorator
