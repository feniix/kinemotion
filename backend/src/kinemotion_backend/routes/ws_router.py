"""WebSocket router for kinemotion backend."""

from fastapi import APIRouter, Header, WebSocket

from ..auth import SupabaseAuth
from .websockets import websocket_connection

router = APIRouter(prefix="/ws", tags=["WebSocket"])


@router.websocket("/analyze/{upload_id}")
async def analyze_video_websocket(
    websocket: WebSocket,
    upload_id: str,
    authorization: str = Header(..., description="Bearer token"),
):
    """WebSocket endpoint for real-time analysis progress updates.

    Connect to this endpoint before starting an analysis to receive
    live progress updates. The upload_id must match the one used
    in the analysis request.

    Args:
        websocket: WebSocket connection
        upload_id: Unique identifier for the upload (must match analysis request)
        authorization: Bearer JWT token for authentication

    Example:
        # Connect with upload_id
        ws = websocket.connect("ws://localhost:8000/ws/analyze/{upload_id}",
                              headers={"Authorization": "Bearer {token}"})

        # Receive messages
        while True:
            message = ws.recv()
            # Messages have format: {"type": "progress", "stage": "...", "progress": 50}
    """
    auth = SupabaseAuth()

    # Extract token from Authorization header
    if not authorization.startswith("Bearer "):
        await websocket.close(code=1008, reason="Missing Bearer token")
        return

    token = authorization.replace("Bearer ", "")

    # Use context manager for connection lifecycle
    async with websocket_connection(websocket, upload_id, auth, token):
        # Send initial connection message
        await websocket.send_json(
            {
                "type": "connected",
                "upload_id": upload_id,
                "message": "WebSocket connection established",
            }
        )

        # Keep connection alive and handle incoming messages
        try:
            while True:
                # Wait for client messages (could be used for cancellation, etc.)
                data = await websocket.receive_json()

                # Handle client requests
                if data.get("action") == "ping":
                    await websocket.send_json({"type": "pong"})
                elif data.get("action") == "cancel":
                    # Could implement cancellation here
                    await websocket.send_json(
                        {
                            "type": "cancelled",
                            "upload_id": upload_id,
                        }
                    )
                    break

        except Exception as e:
            import structlog

            logger = structlog.get_logger(__name__)
            logger.info("websocket_message_loop_ended", upload_id=upload_id, error=str(e))
