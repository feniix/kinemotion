"""Route modules for kinemotion backend."""

from .analysis import router as analysis_router
from .health import router as health_router
from .platform import router as platform_router

__all__ = ["analysis_router", "health_router", "platform_router"]
