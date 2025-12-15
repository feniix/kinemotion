"""API endpoints for analysis sessions and coach feedback."""

from typing import Any

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from kinemotion_backend.auth import SupabaseAuth
from kinemotion_backend.database import get_database_client
from kinemotion_backend.models import (
    AnalysisSessionCreate,
    AnalysisSessionResponse,
    AnalysisSessionWithFeedback,
    CoachFeedbackCreate,
    CoachFeedbackResponse,
    DatabaseError,
)

logger: structlog.stdlib.BoundLogger = structlog.get_logger()
router = APIRouter(prefix="/api/analysis", tags=["Analysis"])
security = HTTPBearer()
auth: SupabaseAuth | None = None


def get_auth() -> SupabaseAuth:
    """Get SupabaseAuth instance (lazy initialization)."""
    global auth
    if auth is None:
        auth = SupabaseAuth()
    return auth


async def get_current_user_email(
    credentials: HTTPAuthorizationCredentials = Depends(security),  # noqa: B008
) -> str:
    """Extract user email from JWT token."""
    try:
        return get_auth().get_user_email(credentials.credentials)
    except Exception as e:
        logger.warning("user_authentication_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        ) from e


@router.post(
    "/sessions",
    response_model=AnalysisSessionResponse,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": DatabaseError}, 500: {"model": DatabaseError}},
)
async def create_analysis_session(
    session_data: AnalysisSessionCreate,
    email: str = Depends(get_current_user_email),
) -> AnalysisSessionResponse:
    """Create a new analysis session record.

    This endpoint stores analysis metadata and results in the database.
    It's typically called after video analysis is completed.
    """
    try:
        db_client = get_database_client()
        session_record = await db_client.create_analysis_session(
            user_id=email,
            jump_type=session_data.jump_type,
            quality_preset=session_data.quality_preset,
            analysis_data=session_data.analysis_data,
            original_video_url=session_data.original_video_url,
            debug_video_url=session_data.debug_video_url,
            results_json_url=session_data.results_json_url,
            processing_time_s=session_data.processing_time_s,
            upload_id=session_data.upload_id,
        )

        logger.info(
            "analysis_session_api_created",
            session_id=session_record["id"],
            email=email,
            jump_type=session_data.jump_type,
        )

        return AnalysisSessionResponse(**session_record)

    except Exception as e:
        logger.error(
            "create_analysis_session_api_error",
            error=str(e),
            email=email,
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create analysis session: {str(e)}",
        ) from e


@router.get(
    "/sessions",
    response_model=list[AnalysisSessionResponse],
    responses={401: {"model": DatabaseError}, 500: {"model": DatabaseError}},
)
async def get_user_analysis_sessions(
    limit: int = 50,
    email: str = Depends(get_current_user_email),
) -> list[AnalysisSessionResponse]:
    """Get analysis sessions for the current user.

    Args:
        limit: Maximum number of sessions to return (default: 50)
    """
    try:
        if limit <= 0 or limit > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Limit must be between 1 and 100",
            )

        db_client = get_database_client()
        sessions = await db_client.get_user_analysis_sessions(user_id=email, limit=limit)

        logger.info(
            "user_analysis_sessions_api_retrieved",
            email=email,
            count=len(sessions),
        )

        return [AnalysisSessionResponse(**session) for session in sessions]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "get_user_analysis_sessions_api_error",
            error=str(e),
            email=email,
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve analysis sessions: {str(e)}",
        ) from e


@router.get(
    "/sessions/{session_id}",
    response_model=AnalysisSessionWithFeedback,
    responses={
        401: {"model": DatabaseError},
        404: {"model": DatabaseError},
        500: {"model": DatabaseError},
    },
)
async def get_analysis_session(
    session_id: str,
    email: str = Depends(get_current_user_email),
) -> AnalysisSessionWithFeedback:
    """Get a specific analysis session with feedback.

    Users can only access their own analysis sessions.
    """
    try:
        db_client = get_database_client()
        session = await db_client.get_analysis_session(session_id=session_id, user_id=email)

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Analysis session not found",
            )

        # Get feedback for this session
        feedback = await db_client.get_session_feedback(analysis_session_id=session_id)

        logger.info(
            "analysis_session_api_retrieved",
            session_id=session_id,
            email=email,
            feedback_count=len(feedback),
        )

        session_with_feedback = AnalysisSessionWithFeedback(**session)
        session_with_feedback.feedback = [CoachFeedbackResponse(**fb) for fb in feedback]

        return session_with_feedback

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "get_analysis_session_api_error",
            error=str(e),
            session_id=session_id,
            email=email,
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve analysis session: {str(e)}",
        ) from e


@router.get(
    "/database-status",
    response_model=dict[str, Any],
    responses={500: {"model": DatabaseError}},
)
async def get_database_status() -> dict[str, Any]:
    """Check if the database is connected and working."""
    try:
        db_client = get_database_client()

        # Try a simple query to test the connection
        # We'll test by trying to access the analysis_sessions table
        db_client.client.table("analysis_sessions").select("id").limit(1).execute()

        return {
            "database_connected": True,
            "tables_exist": True,
            "message": "Database connection successful",
        }

    except Exception as e:
        logger.error("database_status_check_failed", error=str(e), exc_info=True)
        return {
            "database_connected": False,
            "tables_exist": False,
            "message": f"Database connection failed: {str(e)}",
        }


@router.post(
    "/sessions/{session_id}/feedback",
    response_model=CoachFeedbackResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": DatabaseError},
        401: {"model": DatabaseError},
        404: {"model": DatabaseError},
        500: {"model": DatabaseError},
    },
)
async def create_coach_feedback(
    session_id: str,
    feedback_data: CoachFeedbackCreate,
    coach_email: str = Depends(get_current_user_email),
) -> CoachFeedbackResponse:
    """Add coach feedback to an analysis session.

    Any authenticated user can provide feedback on analysis sessions.
    """
    try:
        # Validate that the session exists
        db_client = get_database_client()
        session = await db_client.get_analysis_session(session_id=session_id, user_id=coach_email)

        if not session:
            # Try to get session without user restriction
            # (coaches can provide feedback on any session)
            # This would require modifying the database client
            # to allow unrestricted access for feedback
            # For now, we'll assume users can only provide feedback
            # on their own sessions
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Analysis session not found",
            )

        # Override the session_id from the URL to ensure consistency
        feedback_data.analysis_session_id = session_id

        feedback_record = await db_client.create_coach_feedback(
            analysis_session_id=session_id,
            coach_user_id=coach_email,
            notes=feedback_data.notes,
            rating=feedback_data.rating,
            tags=feedback_data.tags,
        )

        logger.info(
            "coach_feedback_api_created",
            feedback_id=feedback_record["id"],
            session_id=session_id,
            coach_email=coach_email,
        )

        return CoachFeedbackResponse(**feedback_record)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "create_coach_feedback_api_error",
            error=str(e),
            session_id=session_id,
            coach_email=coach_email,
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create coach feedback: {str(e)}",
        ) from e
