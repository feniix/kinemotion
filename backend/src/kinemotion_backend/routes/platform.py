"""Platform information routes for kinemotion backend."""

import os

import structlog
from fastapi import APIRouter

logger: structlog.stdlib.BoundLogger = structlog.get_logger()
router = APIRouter(prefix="/api", tags=["Platform"])


@router.get("/platform")
async def get_platform_info() -> dict[str, str]:
    """Get platform information and capabilities.

    Returns:
        Dict with platform information
    """
    return {
        "name": "Kinemotion API",
        "version": "0.1.0",
        "description": "Video-based kinematic analysis for athletic performance",
        "supported_jump_types": "drop_jump,cmj",
        "supported_formats": "mp4,avi,mov,mkv,flv,wmv",
        "max_file_size": "500MB",
        "environment": os.getenv("ENVIRONMENT", "development"),
    }
