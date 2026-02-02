"""WebSocket endpoints for real-time analysis updates.

Provides WebSocket connections for live progress updates during
video analysis processing.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

import structlog
from fastapi import WebSocket, status

from ..auth import SupabaseAuth

logger: structlog.stdlib.BoundLogger = structlog.get_logger()


class ConnectionManager:
    """Manages active WebSocket connections."""

    def __init__(self) -> None:
        """Initialize connection manager."""
        self._active_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, upload_id: str) -> None:
        """Accept and register a new WebSocket connection.

        Args:
            websocket: WebSocket connection
            upload_id: Unique identifier for the upload
        """
        await websocket.accept()
        self._active_connections[upload_id] = websocket
        logger.info(
            "websocket_connected",
            upload_id=upload_id,
            total_connections=len(self._active_connections),
        )

    def disconnect(self, upload_id: str) -> None:
        """Remove a WebSocket connection.

        Args:
            upload_id: Unique identifier for the upload
        """
        if upload_id in self._active_connections:
            del self._active_connections[upload_id]
            logger.info(
                "websocket_disconnected",
                upload_id=upload_id,
                total_connections=len(self._active_connections),
            )

    async def send_personal_message(self, message: dict[str, Any], upload_id: str) -> bool:
        """Send a message to a specific connection.

        Args:
            message: Message data to send
            upload_id: Target upload identifier

        Returns:
            True if message sent successfully, False otherwise
        """
        websocket = self._active_connections.get(upload_id)
        if websocket:
            try:
                await websocket.send_json(message)
                return True
            except Exception as e:
                logger.warning(
                    "websocket_send_failed",
                    upload_id=upload_id,
                    error=str(e),
                )
                self.disconnect(upload_id)
        return False

    async def broadcast(self, message: dict[str, Any]) -> None:
        """Broadcast a message to all active connections.

        Args:
            message: Message data to broadcast
        """
        disconnected = []
        for upload_id, websocket in self._active_connections.items():
            try:
                await websocket.send_json(message)
            except Exception:
                disconnected.append(upload_id)

        # Clean up disconnected connections
        for upload_id in disconnected:
            self.disconnect(upload_id)


# Global connection manager instance
_manager: ConnectionManager | None = None


def get_connection_manager() -> ConnectionManager:
    """Get the global connection manager instance.

    Returns:
        ConnectionManager singleton
    """
    global _manager
    if _manager is None:
        _manager = ConnectionManager()
    return _manager


@asynccontextmanager
async def websocket_connection(
    websocket: WebSocket,
    upload_id: str,
    auth: SupabaseAuth,
    token: str,
) -> AsyncGenerator[None, None]:
    """Context manager for WebSocket connection lifecycle.

    Args:
        websocket: WebSocket connection
        upload_id: Unique identifier for the upload
        auth: SupabaseAuth instance for token validation
        token: JWT token for authentication

    Yields:
        None when connection is established

    Raises:
        HTTPException: If authentication fails
    """
    manager = get_connection_manager()

    # Authenticate the WebSocket connection
    try:
        await auth.get_user_email(token)
    except Exception as e:
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION,
            reason=f"Authentication failed: {str(e)}",
        )
        logger.warning("websocket_authentication_failed", upload_id=upload_id, error=str(e))
        raise

    # Connect and yield
    await manager.connect(websocket, upload_id)
    try:
        yield
    finally:
        manager.disconnect(upload_id)


async def send_progress_update(upload_id: str, stage: str, progress: int) -> bool:
    """Send a progress update for an analysis.

    Args:
        upload_id: Unique identifier for the upload
        stage: Current processing stage
        progress: Progress percentage (0-100)

    Returns:
        True if message sent successfully
    """
    manager = get_connection_manager()
    message = {
        "type": "progress",
        "stage": stage,
        "progress": progress,
        "upload_id": upload_id,
    }
    return await manager.send_personal_message(message, upload_id)


async def send_analysis_complete(
    upload_id: str,
    results: dict[str, Any],
) -> bool:
    """Send completion message with analysis results.

    Args:
        upload_id: Unique identifier for the upload
        results: Analysis results data

    Returns:
        True if message sent successfully
    """
    manager = get_connection_manager()
    message = {
        "type": "complete",
        "progress": 100,
        "upload_id": upload_id,
        "results": results,
    }
    return await manager.send_personal_message(message, upload_id)


async def send_analysis_error(
    upload_id: str,
    error_message: str,
) -> bool:
    """Send error message for failed analysis.

    Args:
        upload_id: Unique identifier for the upload
        error_message: Error description

    Returns:
        True if message sent successfully
    """
    manager = get_connection_manager()
    message = {
        "type": "error",
        "upload_id": upload_id,
        "error": error_message,
    }
    return await manager.send_personal_message(message, upload_id)
