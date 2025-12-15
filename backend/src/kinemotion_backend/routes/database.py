"""Database and analysis session endpoints."""

import os
import uuid
from typing import Any

import structlog
from fastapi import APIRouter, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel

logger: structlog.stdlib.BoundLogger = structlog.get_logger()
router = APIRouter(prefix="/api/analysis", tags=["Analysis"])


class DatabaseStatus(BaseModel):
    """Database connection status response."""

    database_connected: bool
    message: str


class AnalysisSession(BaseModel):
    """Analysis session stored in database."""

    id: str
    jump_type: str
    quality_preset: str
    analysis_data: dict[str, Any] | None = None
    original_video_url: str | None = None
    debug_video_url: str | None = None
    results_json_url: str | None = None
    processing_time_s: float | None = None


class SessionCreateRequest(BaseModel):
    """Request to create an analysis session."""

    jump_type: str
    quality_preset: str
    analysis_data: dict[str, Any] | None = None
    original_video_url: str | None = None
    debug_video_url: str | None = None
    results_json_url: str | None = None
    processing_time_s: float | None = None


class FeedbackRequest(BaseModel):
    """Request to save feedback for an analysis session."""

    notes: str
    rating: int | None = None
    tags: list[str] | None = None


# Simple in-memory storage for sessions (would be replaced with database)
_sessions: dict[str, AnalysisSession] = {}
_feedback: dict[str, list[dict[str, Any]]] = {}


@router.get("/database-status")
async def get_database_status() -> JSONResponse:
    """Get database connection status.

    Returns information about whether the database is available
    for storing analysis sessions and feedback.
    """
    # Check if database is configured (would check real DB connection)
    db_url = os.getenv("SUPABASE_URL")
    db_key = os.getenv("SUPABASE_ANON_KEY")

    database_connected = bool(db_url and db_key)

    return JSONResponse(
        content={
            "database_connected": database_connected,
            "message": (
                "Database connection available"
                if database_connected
                else "Database not configured"
            ),
        }
    )


@router.post("/sessions")
async def create_analysis_session(
    request: SessionCreateRequest, authorization: str | None = Header(None)
) -> JSONResponse:
    """Create a new analysis session.

    Stores metadata about an analysis for later feedback and tracking.
    Requires authentication via Supabase token in Authorization header.
    """
    if not authorization:
        return JSONResponse(
            status_code=401,
            content={"error": "Unauthorized: Authorization header required"},
        )

    # Extract token (would validate with Supabase in production)
    # For now, just check that token exists
    if not authorization.startswith("Bearer "):
        return JSONResponse(
            status_code=401,
            content={"error": "Unauthorized: Invalid authorization format"},
        )

    session_id = str(uuid.uuid4())

    session = AnalysisSession(
        id=session_id,
        jump_type=request.jump_type,
        quality_preset=request.quality_preset,
        analysis_data=request.analysis_data,
        original_video_url=request.original_video_url,
        debug_video_url=request.debug_video_url,
        results_json_url=request.results_json_url,
        processing_time_s=request.processing_time_s,
    )

    _sessions[session_id] = session
    _feedback[session_id] = []

    logger.info("analysis_session_created", session_id=session_id)

    return JSONResponse(
        status_code=201,
        content={"id": session_id},
    )


@router.post("/sessions/{session_id}/feedback")
async def save_session_feedback(
    session_id: str,
    request: FeedbackRequest,
    authorization: str | None = Header(None),
) -> JSONResponse:
    """Save feedback for an analysis session.

    Stores coach feedback, ratings, and tags for a completed analysis.
    Requires authentication via Supabase token in Authorization header.
    """
    if not authorization:
        return JSONResponse(
            status_code=401,
            content={"error": "Unauthorized: Authorization header required"},
        )

    if session_id not in _sessions:
        return JSONResponse(
            status_code=404,
            content={"error": "Analysis session not found"},
        )

    feedback_item = {
        "notes": request.notes,
        "rating": request.rating,
        "tags": request.tags or [],
    }

    _feedback[session_id].append(feedback_item)

    logger.info("feedback_saved", session_id=session_id)

    return JSONResponse(
        status_code=201,
        content={"id": session_id, "feedback_count": len(_feedback[session_id])},
    )
