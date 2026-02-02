"""FastAPI dependencies for kinemotion backend."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ..auth import SupabaseAuth
from ..logging_config import get_logger
from ..services.analysis_service import AnalysisService

logger = get_logger(__name__)
security = HTTPBearer()
auth: SupabaseAuth | None = None


def get_auth() -> SupabaseAuth:
    """Get SupabaseAuth instance (lazy initialization)."""
    global auth
    if auth is None:
        auth = SupabaseAuth()
    return auth


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),  # noqa: B008
) -> str:
    """Extract user ID from JWT token."""
    try:
        return await get_auth().get_user_id(credentials.credentials)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        ) from e


async def get_current_user_email(
    credentials: HTTPAuthorizationCredentials = Depends(security),  # noqa: B008
) -> str:
    """Extract user email from JWT token.

    This is the shared authentication dependency for most endpoints.
    For endpoints that need test password bypass, use get_user_email_for_analysis
    from routes/analysis.py instead.

    Args:
        credentials: HTTP bearer credentials from Authorization header

    Returns:
        User email from validated JWT token

    Raises:
        HTTPException: If token is invalid or email not found
    """
    try:
        return await get_auth().get_user_email(credentials.credentials)
    except HTTPException:
        raise
    except Exception as e:
        logger.warning("user_authentication_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        ) from e


def get_analysis_service() -> AnalysisService:
    """Get AnalysisService instance.

    Returns:
        New AnalysisService instance for dependency injection

    Note:
        Returns a new instance each time since AnalysisService is lightweight
        and holds no expensive connections.
    """
    return AnalysisService()
