"""Video analysis routes for kinemotion backend."""

import structlog
from fastapi import APIRouter, File, Form, Header, Request, UploadFile
from fastapi.responses import JSONResponse
from fastapi_limiter.depends import RateLimiter

from ..models.responses import AnalysisResponse
from ..services import AnalysisService, validate_referer
from ..utils import NoOpLimiter

logger = structlog.get_logger()
router = APIRouter(prefix="/api", tags=["Analysis"])

# Rate limiting (use NoOpLimiter for testing)
_testing = False  # This should be set from environment
limiter = NoOpLimiter() if _testing else RateLimiter()


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
) -> JSONResponse:
    """Analyze video and return jump metrics.

    This endpoint processes a video file using real kinemotion analysis:
    - Drop Jump: Analyzes ground contact and flight time
    - CMJ: Analyzes jump height, countermovement depth, and phases

    Args:
        file: Video file to analyze (multipart/form-data)
        jump_type: Type of jump ("drop_jump" or "cmj")
        quality: Analysis quality preset ("fast", "balanced", or "accurate")
        debug: Debug overlay flag ("true" or "false", default "false")

    Returns:
        JSON response with metrics or error details

    Raises:
        HTTPException: If validation or processing fails
    """
    # Validate referer (prevent direct API access)
    validate_referer(referer, x_test_password)

    # Initialize analysis service
    analysis_service = AnalysisService()

    try:
        # Perform analysis using service layer
        result: AnalysisResponse = await analysis_service.analyze_video(
            file=file,
            jump_type=jump_type,
            quality=quality,
            user_id=None,  # TODO: Extract from auth when available
        )

        # Return JSON response
        return JSONResponse(content=result.to_dict())

    except Exception as e:
        logger.error(
            "Video analysis failed",
            upload_id=request.headers.get("x-upload-id", "unknown"),
            error=str(e),
            exc_info=True,
        )

        # Return error response using service layer error handling
        error_result = await analysis_service.analyze_video(
            file=file,
            jump_type=jump_type,
            quality=quality,
            user_id=None,
        )

        return JSONResponse(
            status_code=error_result.status_code,
            content=error_result.to_dict(),
        )
