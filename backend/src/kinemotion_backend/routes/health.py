"""Health check routes for kinemotion backend."""

import os
from datetime import datetime, timezone

import structlog
from fastapi import APIRouter

logger = structlog.get_logger()
router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check() -> dict[str, str | bool]:
    """Health check endpoint.

    Returns:
        Dict with health status information
    """
    # Check R2 configuration
    r2_configured = bool(
        os.getenv("R2_ENDPOINT")
        and os.getenv("R2_ACCESS_KEY")
        and os.getenv("R2_SECRET_KEY")
    )

    return {
        "status": "healthy",
        "service": "kinemotion-backend",
        "version": "0.1.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "r2_configured": r2_configured,
    }
