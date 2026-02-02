"""FastAPI application factory for Kinemotion video analysis backend."""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from kinemotion.core.pose import MediaPipePoseTracker, PoseTrackerFactory

from ..analysis_api import router as database_analysis_router
from ..database import close_db_executor
from ..logging_config import get_logger, setup_logging
from ..routes import analysis_router, health_router, platform_router, ws_router
from ..utils.rate_limiting import setup_rate_limiter

# Initialize structured logging
setup_logging(
    json_logs=os.getenv("JSON_LOGS", "false").lower() == "true",
    log_level=os.getenv("LOG_LEVEL", "INFO"),
)

logger = get_logger(__name__)

# Global pose trackers for different quality presets
global_pose_trackers: dict[str, MediaPipePoseTracker] = {}
# Store the detected backend for health checks
detected_backend: str = "unknown"


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Manage application lifecycle and global resources."""
    global detected_backend

    logger.info("initializing_pose_trackers")
    detected_backend = "mediapipe"
    try:
        # MediaPipe uses confidence thresholds for quality presets
        global_pose_trackers["fast"] = PoseTrackerFactory.create(
            min_detection_confidence=0.3,
            min_tracking_confidence=0.3,
        )
        global_pose_trackers["balanced"] = PoseTrackerFactory.create(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        global_pose_trackers["accurate"] = PoseTrackerFactory.create(
            min_detection_confidence=0.6,
            min_tracking_confidence=0.6,
        )
        logger.info("pose_trackers_initialized")

        yield

    finally:
        # Clean up resources
        logger.info("closing_pose_trackers")
        for tracker in global_pose_trackers.values():
            tracker.close()
        global_pose_trackers.clear()

        # Close database thread pool executor
        logger.info("closing_db_executor")
        close_db_executor()


def create_application() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title="Kinemotion Backend API",
        description="Video-based kinematic analysis API for athletic performance",
        version="0.1.0",
        lifespan=lifespan,
    )

    # Set up rate limiting (before other middleware for proper order)
    setup_rate_limiter(app)

    # Add CORS middleware
    _add_cors_middleware(app)

    # Include routers
    app.include_router(database_analysis_router)  # Database-related analysis endpoints
    app.include_router(analysis_router)  # Main video analysis endpoints
    app.include_router(health_router)
    app.include_router(platform_router)
    app.include_router(ws_router)  # WebSocket connections

    # Add exception handlers
    _add_exception_handlers(app)

    # Add middleware
    _add_middleware(app)

    return app


def _add_cors_middleware(app: FastAPI) -> None:
    """Add CORS middleware to application."""
    from .config import settings

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_property,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )


def _add_exception_handlers(app: FastAPI) -> None:
    """Add exception handlers to application."""
    from fastapi import HTTPException, Request
    from fastapi.responses import JSONResponse

    async def http_exception_handler(_request: Request, exc: HTTPException) -> JSONResponse:
        """Handle HTTP exceptions."""
        return JSONResponse(
            status_code=exc.status_code,
            content={"message": exc.detail},
        )

    async def general_exception_handler(_request: Request, exc: Exception) -> JSONResponse:
        """Handle general exceptions."""
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"message": "Internal server error"},
        )

    app.add_exception_handler(HTTPException, http_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, general_exception_handler)


def _add_middleware(app: FastAPI) -> None:
    """Add custom middleware to application."""
    from ..middleware import RequestLoggingMiddleware

    app.add_middleware(RequestLoggingMiddleware)


# Create application instance
app = create_application()
