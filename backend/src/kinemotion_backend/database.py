"""Supabase database integration for kinemotion backend."""

import os
from typing import Any

import structlog
from supabase import Client, create_client

logger: structlog.stdlib.BoundLogger = structlog.get_logger()


class DatabaseClient:
    """Supabase database client with async support."""

    def __init__(self) -> None:
        """Initialize Supabase client."""
        self.supabase_url = os.getenv("SUPABASE_URL", "")

        # Prefer modern keys, fall back to legacy for compatibility
        # Check which key source is being used for debugging
        supabase_publishable_key = os.getenv("SUPABASE_PUBLISHABLE_KEY")
        supabase_secret_key = os.getenv("SUPABASE_SECRET_KEY")
        supabase_anon_key = os.getenv("SUPABASE_ANON_KEY")
        supabase_key = os.getenv("SUPABASE_KEY")

        self.supabase_key = (
            supabase_publishable_key or supabase_secret_key or supabase_anon_key or supabase_key
        )

        if not self.supabase_url:
            raise ValueError("SUPABASE_URL must be set")

        if not self.supabase_key:
            raise ValueError(
                "No Supabase API key found. Set one of: "
                "SUPABASE_PUBLISHABLE_KEY, SUPABASE_SECRET_KEY, "
                "SUPABASE_ANON_KEY, or SUPABASE_KEY"
            )

        # Log which key source is being used (without exposing the actual key)
        key_source = "unknown"
        if supabase_publishable_key:
            key_source = "SUPABASE_PUBLISHABLE_KEY"
        elif supabase_secret_key:
            key_source = "SUPABASE_SECRET_KEY"
        elif supabase_anon_key:
            key_source = "SUPABASE_ANON_KEY"
        elif supabase_key:
            key_source = "SUPABASE_KEY"

        self.client: Client = create_client(self.supabase_url, self.supabase_key)
        logger.info(
            "database_client_initialized",
            supabase_url=self.supabase_url,
            key_source=key_source,
        )

    async def create_analysis_session(
        self,
        user_id: str,
        jump_type: str,
        quality_preset: str,
        analysis_data: dict[str, Any],
        original_video_url: str | None = None,
        debug_video_url: str | None = None,
        results_json_url: str | None = None,
        processing_time_s: float | None = None,
        upload_id: str | None = None,
    ) -> dict[str, Any]:
        """Create a new analysis session record.

        Args:
            user_id: Email of the user who performed the analysis
            jump_type: Type of jump ('cmj' or 'drop_jump')
            quality_preset: Analysis quality preset
            analysis_data: JSON analysis results
            original_video_url: R2 URL for original video
            debug_video_url: R2 URL for debug video
            results_json_url: R2 URL for results JSON
            processing_time_s: Processing time in seconds
            upload_id: Upload ID from analysis system

        Returns:
            Created session record

        Raises:
            Exception: If database operation fails
        """
        try:
            session_data = {
                "user_id": user_id,
                "jump_type": jump_type,
                "quality_preset": quality_preset,
                "original_video_url": original_video_url,
                "debug_video_url": debug_video_url,
                "results_json_url": results_json_url,
                "analysis_data": analysis_data,
                "processing_time_s": processing_time_s,
                "upload_id": upload_id,
            }

            response = self.client.table("analysis_sessions").insert(session_data).execute()

            if response.data:
                session_data = response.data[0]
                if isinstance(session_data, dict) and "id" in session_data:
                    logger.info(
                        "analysis_session_created",
                        user_id=user_id,
                        jump_type=jump_type,
                        session_id=session_data["id"],
                    )
                    return session_data
                else:
                    raise Exception("Invalid data format returned from database")
            else:
                raise Exception("No data returned from database insert")

        except Exception as e:
            logger.error(
                "create_analysis_session_failed",
                error=str(e),
                user_id=user_id,
                jump_type=jump_type,
                exc_info=True,
            )
            raise

    async def get_user_analysis_sessions(
        self, user_id: str, limit: int = 50
    ) -> list[dict[str, Any]]:
        """Get analysis sessions for a specific user.

        Args:
            user_id: Email of the user
            limit: Maximum number of sessions to return

        Returns:
            List of analysis sessions

        Raises:
            Exception: If database operation fails
        """
        try:
            response = (
                self.client.table("analysis_sessions")
                .select("*")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )

            logger.info(
                "user_analysis_sessions_retrieved",
                user_id=user_id,
                count=len(response.data or []),
            )
            return response.data or []

        except Exception as e:
            logger.error(
                "get_user_analysis_sessions_failed",
                error=str(e),
                user_id=user_id,
                exc_info=True,
            )
            raise

    async def get_analysis_session(self, session_id: str, user_id: str) -> dict[str, Any] | None:
        """Get a specific analysis session.

        Args:
            session_id: UUID of the analysis session
            user_id: Email of the user (for authorization)

        Returns:
            Analysis session data or None if not found

        Raises:
            Exception: If database operation fails
        """
        try:
            response = (
                self.client.table("analysis_sessions")
                .select("*")
                .eq("id", session_id)
                .eq("user_id", user_id)  # Ensure user can only access their own sessions
                .single()
                .execute()
            )

            logger.info(
                "analysis_session_retrieved",
                session_id=session_id,
                user_id=user_id,
                found=response.data is not None,
            )
            return response.data

        except Exception as e:
            logger.error(
                "get_analysis_session_failed",
                error=str(e),
                session_id=session_id,
                user_id=user_id,
                exc_info=True,
            )
            raise

    async def create_coach_feedback(
        self,
        analysis_session_id: str,
        coach_user_id: str,
        notes: str | None = None,
        rating: int | None = None,
        tags: list[str] | None = None,
    ) -> dict[str, Any]:
        """Create coach feedback for an analysis session.

        Args:
            analysis_session_id: UUID of the analysis session
            coach_user_id: Email of the coach providing feedback
            notes: Coach notes
            rating: Rating from 1-5
            tags: List of tags

        Returns:
            Created feedback record

        Raises:
            Exception: If database operation fails
        """
        try:
            feedback_data = {
                "analysis_session_id": analysis_session_id,
                "coach_user_id": coach_user_id,
                "notes": notes,
                "rating": rating,
                "tags": tags or [],
            }

            response = self.client.table("coach_feedback").insert(feedback_data).execute()

            if response.data:
                feedback_data = response.data[0]
                if isinstance(feedback_data, dict) and "id" in feedback_data:
                    logger.info(
                        "coach_feedback_created",
                        analysis_session_id=analysis_session_id,
                        coach_user_id=coach_user_id,
                        feedback_id=feedback_data["id"],
                    )
                    return feedback_data
                else:
                    raise Exception("Invalid data format returned from database")
            else:
                raise Exception("No data returned from database insert")

        except Exception as e:
            logger.error(
                "create_coach_feedback_failed",
                error=str(e),
                analysis_session_id=analysis_session_id,
                coach_user_id=coach_user_id,
                exc_info=True,
            )
            raise

    async def get_session_feedback(self, analysis_session_id: str) -> list[dict[str, Any]]:
        """Get all feedback for an analysis session.

        Args:
            analysis_session_id: UUID of the analysis session

        Returns:
            List of feedback records

        Raises:
            Exception: If database operation fails
        """
        try:
            response = (
                self.client.table("coach_feedback")
                .select("*")
                .eq("analysis_session_id", analysis_session_id)
                .order("created_at", desc=True)
                .execute()
            )

            logger.info(
                "session_feedback_retrieved",
                analysis_session_id=analysis_session_id,
                count=len(response.data or []),
            )
            return response.data or []

        except Exception as e:
            logger.error(
                "get_session_feedback_failed",
                error=str(e),
                analysis_session_id=analysis_session_id,
                exc_info=True,
            )
            raise


# Global database client instance
db_client: DatabaseClient | None = None


def get_database_client() -> DatabaseClient:
    """Get the global database client instance."""
    global db_client
    if db_client is None:
        db_client = DatabaseClient()
    return db_client
