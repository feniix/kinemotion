"""Request tracking middleware for structured logging."""

import time
import uuid
from collections.abc import Callable

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from kinemotion_backend.auth import SupabaseAuth

logger: structlog.stdlib.BoundLogger = structlog.get_logger(__name__)

# Initialize Supabase auth (optional - only if credentials provided)
supabase_auth: SupabaseAuth | None = None
try:
    supabase_auth = SupabaseAuth()
    logger.info("supabase_auth_initialized")
except ValueError:
    logger.warning("supabase_auth_not_configured", message="Supabase credentials not provided")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to add request tracking and logging."""

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with structured logging context.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware or endpoint handler

        Returns:
            HTTP response
        """
        # Generate request ID
        request_id = str(uuid.uuid4())

        # Clear any existing context and set new context
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            client_ip=request.client.host if request.client else "unknown",
        )

        # Extract and validate user email from Authorization header
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer ") and supabase_auth:
            token = auth_header.replace("Bearer ", "")
            auth_start = time.time()
            try:
                user_email = supabase_auth.get_user_email(token)
                auth_duration_ms = (time.time() - auth_start) * 1000

                # Bind user email to logging context
                structlog.contextvars.bind_contextvars(
                    email=user_email,
                )

                # Store in request state for use in endpoints
                request.state.email = user_email

                logger.info(
                    "user_authenticated",
                    email=user_email,
                    auth_duration_ms=round(auth_duration_ms, 2),
                )
            except Exception as e:
                auth_duration_ms = (time.time() - auth_start) * 1000
                logger.warning(
                    "auth_token_invalid",
                    error=str(e),
                    auth_duration_ms=round(auth_duration_ms, 2),
                )
                # Continue without user context - endpoints handle auth

        start_time = time.time()

        # Log incoming request
        logger.info(
            "request_started",
            user_agent=request.headers.get("user-agent", "unknown"),
            referer=request.headers.get("referer"),
        )

        try:
            # Process request
            response = await call_next(request)

            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000

            # Log successful response
            logger.info(
                "request_completed",
                status_code=response.status_code,
                duration_ms=round(duration_ms, 2),
            )

            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id

            return response

        except Exception as e:
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000

            # Log error
            logger.error(
                "request_failed",
                error=str(e),
                error_type=type(e).__name__,
                duration_ms=round(duration_ms, 2),
                exc_info=True,
            )

            # Re-raise to let FastAPI handle the error
            raise
