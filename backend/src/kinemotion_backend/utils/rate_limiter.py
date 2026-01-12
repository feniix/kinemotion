from collections.abc import Callable
from typing import TypeVar

F = TypeVar("F", bound=Callable[..., object])


class NoOpLimiter:
    """No-op rate limiter for testing and environments without fastapi_limiter."""

    def limit(self, _limit_string: str) -> Callable[[F], F]:
        """Return a decorator that passes through the function unchanged."""

        def decorator(func: F) -> F:
            return func

        return decorator
