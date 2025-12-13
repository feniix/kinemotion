"""Health check routes for kinemotion backend."""

import os

import structlog
from fastapi import APIRouter

logger = structlog.get_logger()
router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint.

    Returns:
        Dict with health status information
    """
    return {
        "status": "healthy",
        "service": "kinemotion-backend",
        "version": "0.1.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
    }
