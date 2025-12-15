"""Video analysis routes for kinemotion backend."""

import os
import time

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    Header,
    HTTPException,
    Request,
    UploadFile,
    status,
)
from fastapi.responses import JSONResponse

try:
    from fastapi_limiter.depends import RateLimiter

    fastapi_limiter_available = True
except ImportError:
    fastapi_limiter_available = False
    RateLimiter = None  # type: ignore[assignment]

from ..auth import SupabaseAuth
from ..logging_config import get_logger
from ..models.responses import AnalysisResponse
from ..services import AnalysisService, is_test_password_valid, validate_referer
from ..utils import NoOpLimiter

logger = get_logger(__name__)
router = APIRouter(prefix="/api", tags=["Analysis"])

# Rate limiting (use NoOpLimiter for testing or when fastapi_limiter unavailable)
_testing = False  # This should be set from environment
if _testing or not fastapi_limiter_available:
    limiter = NoOpLimiter()
else:
    limiter = RateLimiter()  # type: ignore[operator]


async def get_user_email_for_analysis(
    request: Request,
    x_test_password: str | None = Header(None),  # noqa: B008
) -> str:
    """Extract user email from JWT token or use test backdoor.

    Args:
        request: HTTP request (to access Authorization header)
        x_test_password: Optional test password for debugging

    Returns:
        User email (from token or test backdoor)

    Raises:
        HTTPException: If authentication fails and test password not provided
    """
    # Allow bypass with test password (for curl testing, debugging)
    if is_test_password_valid(x_test_password):
        test_email = os.getenv("TEST_EMAIL", "test@example.com")
        logger.info("analysis_test_password_used", email=test_email)
        return test_email

    # Otherwise require valid JWT token from Authorization header
    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    token = auth_header.replace("Bearer ", "")
    try:
        auth = SupabaseAuth()
        email = auth.get_user_email(token)
        return email
    except HTTPException:
        raise
    except Exception as e:
        logger.error("user_email_extraction_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        ) from e


@router.post("/analyze")
@limiter.limit("3/minute")
async def analyze_video(
    request: Request,
    file: UploadFile = File(...),  # noqa: B008
    jump_type: str = Form("cmj"),  # noqa: B008
    quality: str = Form("balanced"),  # noqa: B008
    debug: str = Form("false"),  # noqa: B008
    referer: str | None = Header(None),  # noqa: B008
    x_test_password: str | None = Header(None),  # noqa: B008
    email: str = Depends(get_user_email_for_analysis),  # noqa: B008
) -> JSONResponse:
    """Analyze video and return jump metrics.

    This endpoint processes a video file using real kinemotion analysis:
    - Drop Jump: Analyzes ground contact and flight time
    - CMJ: Analyzes jump height, countermovement depth, and phases

    Requires authentication via JWT token in Authorization header, or TEST_PASSWORD
    header for testing/debugging.

    Args:
        file: Video file to analyze (multipart/form-data)
        jump_type: Type of jump ("drop_jump" or "cmj")
        quality: Analysis quality preset ("fast", "balanced", or "accurate")
        debug: Debug overlay flag ("true" or "false", default "false")
        email: Authenticated user email (extracted from JWT or test password)

    Returns:
        JSON response with metrics or error details

    Raises:
        HTTPException: If authentication or processing fails
    """
    start_time = time.time()

    # Validate referer (prevent direct API access)
    validate_referer(referer, x_test_password)

    # Initialize analysis service
    analysis_service = AnalysisService()

    try:
        # Convert debug string to boolean
        enable_debug = debug.lower() == "true"

        # Log analysis start
        logger.info(
            "analyzing_video_started",
            jump_type=jump_type,
            quality=quality,
            debug=enable_debug,
            email=email,
        )

        # Perform analysis using service layer
        result: AnalysisResponse = await analysis_service.analyze_video(
            file=file,
            jump_type=jump_type,
            quality=quality,
            debug=enable_debug,
            user_id=email,
        )

        # Log analysis completion
        analysis_duration = time.time() - start_time
        logger.info(
            "analyzing_video_completed",
            duration_ms=round(analysis_duration * 1000, 1),
            status_code=result.status_code,
        )

        # Return JSON response
        return JSONResponse(content=result.to_dict())

    except ValueError as e:
        elapsed = time.time() - start_time
        logger.warning(
            "analyze_endpoint_validation_error",
            upload_id=request.headers.get("x-upload-id", "unknown"),
            error=str(e),
            processing_time_s=round(elapsed, 2),
        )

        # Return validation error
        error_result = AnalysisResponse(
            status_code=422,
            message=str(e),
            error="validation_error",
            metrics=None,
            results_url=None,
            debug_video_url=None,
            original_video_url=None,
            processing_time_s=elapsed,
        )

        return JSONResponse(
            status_code=422,
            content=error_result.to_dict(),
        )

    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(
            "analyze_endpoint_error",
            upload_id=request.headers.get("x-upload-id", "unknown"),
            error=str(e),
            error_type=type(e).__name__,
            processing_time_s=round(elapsed, 2),
            exc_info=True,
        )

        # Return generic server error
        error_result = AnalysisResponse(
            status_code=500,
            message="Internal server error during analysis",
            error=str(e),
            metrics=None,
            results_url=None,
            debug_video_url=None,
            original_video_url=None,
            processing_time_s=elapsed,
        )

        return JSONResponse(
            status_code=500,
            content=error_result.to_dict(),
        )
