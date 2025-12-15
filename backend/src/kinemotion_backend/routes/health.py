"""Health check routes for kinemotion backend."""

import os
from datetime import datetime, timezone
from importlib.metadata import version

import structlog
from fastapi import APIRouter

logger: structlog.stdlib.BoundLogger = structlog.get_logger()
router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check() -> dict[str, str | bool]:
    """Health check endpoint.

    Returns:
        Dict with health status information
    """
    # Check R2 configuration
    r2_configured = bool(
        os.getenv("R2_ENDPOINT") and os.getenv("R2_ACCESS_KEY") and os.getenv("R2_SECRET_KEY")
    )

    # Get kinemotion version safely
    try:
        kinemotion_version = version("kinemotion")
    except Exception:
        kinemotion_version = "unknown"

    # Check database connection
    database_connected = False
    try:
        from kinemotion_backend.database import get_database_client

        db_client = get_database_client()
        # Try to access analysis_sessions table with select limit to test connectivity
        # This will return data if accessible, or raise if table doesn't exist or RLS blocks it
        response = db_client.client.table("analysis_sessions").select("id").limit(1).execute()
        # If we get here, the database connection worked
        # Note: response.data could be empty if table is empty, but that's still success
        database_connected = True
        logger.info(
            "database_health_check_succeeded",
            rows_returned=len(response.data or []),
        )
    except Exception as db_error:
        logger.warning(
            "database_health_check_failed",
            error=str(db_error),
            error_type=type(db_error).__name__,
            exc_info=True,
        )

    return {
        "status": "healthy",
        "service": "kinemotion-backend",
        "version": "0.1.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "kinemotion_version": kinemotion_version,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "r2_configured": r2_configured,
        "database_connected": database_connected,
    }
