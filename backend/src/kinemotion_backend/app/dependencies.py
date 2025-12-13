"""FastAPI dependencies for kinemotion backend."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ..auth import SupabaseAuth

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
        return get_auth().get_user_id(credentials.credentials)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        ) from e
