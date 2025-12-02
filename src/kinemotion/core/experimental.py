"""Decorators for marking experimental and unused features.

These decorators help identify code that is implemented but not yet
integrated into the main pipeline, making it easier to track features
for future enhancement or cleanup.
"""

import functools
import warnings
from collections.abc import Callable
from typing import TypeVar

F = TypeVar("F", bound=Callable)


def experimental(
    reason: str, *, issue: int | None = None, since: str | None = None
) -> Callable[[F], F]:
    """Mark a feature as experimental/not fully integrated.

    Experimental features are working implementations that haven't been
    fully integrated into the main pipeline. They emit warnings when called
    to alert developers they're using untested/unstable APIs.

    Args:
        reason: Why this is experimental (e.g., "API unstable", "needs validation")
        issue: Optional GitHub issue number for tracking integration
        since: Optional version when this became experimental

    Example:
        >>> @experimental("API may change", issue=123, since="0.34.0")
        ... def new_feature():
        ...     pass

    Returns:
        Decorated function that warns on use
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):  # type: ignore
            msg = f"{func.__name__} is experimental: {reason}"
            if issue:
                msg += f" (GitHub issue #{issue})"
            if since:
                msg += f" [since v{since}]"
            warnings.warn(msg, FutureWarning, stacklevel=2)
            return func(*args, **kwargs)

        # Add metadata for documentation/tooling
        wrapper.__experimental__ = True  # type: ignore[attr-defined]
        wrapper.__experimental_reason__ = reason  # type: ignore[attr-defined]
        if issue:
            wrapper.__experimental_issue__ = issue  # type: ignore[attr-defined]
        if since:
            wrapper.__experimental_since__ = since  # type: ignore[attr-defined]

        return wrapper  # type: ignore[return-value]

    return decorator


def unused(
    reason: str, *, remove_in: str | None = None, since: str | None = None
) -> Callable[[F], F]:
    """Mark a feature as implemented but not integrated into pipeline.

    Unused features are fully working implementations that aren't called
    by the main analysis pipeline. Unlike @experimental, these don't emit
    warnings when called (they work fine), but are marked for tracking.

    Use this for:
    - Features awaiting CLI integration
    - Alternative implementations not yet exposed
    - Code kept for backward compatibility

    Args:
        reason: Why this is unused (e.g., "awaiting CLI parameter")
        remove_in: Optional version when this might be removed if not integrated
        since: Optional version when this became unused

    Example:
        >>> @unused("Not called by pipeline", remove_in="1.0.0", since="0.34.0")
        ... def calculate_adaptive_threshold():
        ...     pass

    Returns:
        Original function with metadata attached (no runtime behavior change)
    """

    def decorator(func: F) -> F:
        # Don't wrap - we don't want warnings when calling it
        # Just attach metadata for documentation/cleanup tools
        func.__unused__ = True  # type: ignore[attr-defined]
        func.__unused_reason__ = reason  # type: ignore[attr-defined]
        if remove_in:
            func.__unused_remove_in__ = remove_in  # type: ignore[attr-defined]
        if since:
            func.__unused_since__ = since  # type: ignore[attr-defined]

        return func

    return decorator
