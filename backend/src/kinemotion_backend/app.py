"""FastAPI application for Kinemotion video analysis backend.

Real metrics integration with Cloudflare R2 storage for video and results management.
"""

import os
import tempfile
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path
from typing import Any, Literal, cast

import boto3
from fastapi import (
    FastAPI,
    File,
    Form,
    Header,
    HTTPException,
    Request,
    UploadFile,
    status,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from kinemotion.api import process_cmj_video, process_dropjump_video
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

from kinemotion_backend.logging_config import get_logger, setup_logging
from kinemotion_backend.middleware import RequestLoggingMiddleware

# Initialize structured logging
setup_logging(
    json_logs=os.getenv("JSON_LOGS", "false").lower() == "true",
    log_level=os.getenv("LOG_LEVEL", "INFO"),
)

logger = get_logger(__name__)

# ========== Type Definitions ==========

JumpType = Literal["drop_jump", "cmj"]


class AnalysisResponse:
    """Response structure for video analysis results."""

    def __init__(
        self,
        status_code: int,
        message: str,
        metrics: dict[str, Any] | None = None,
        results_url: str | None = None,
        error: str | None = None,
        processing_time_s: float = 0.0,
    ):
        self.status_code = status_code
        self.message = message
        self.metrics = metrics
        self.results_url = results_url
        self.error = error
        self.processing_time_s = processing_time_s

    def to_dict(self) -> dict[str, Any]:
        """Convert response to JSON-serializable dictionary."""
        result: dict[str, Any] = {
            "status": self.status_code,
            "message": self.message,
            "processing_time_s": self.processing_time_s,
        }

        if self.metrics is not None:
            result["metrics"] = self.metrics

        if self.results_url is not None:
            result["results_url"] = self.results_url

        if self.error is not None:
            result["error"] = self.error

        return result


# ========== R2 Storage Client ==========


class R2StorageClient:
    """Cloudflare R2 storage client for video and results management."""

    def __init__(self) -> None:
        """Initialize R2 client with environment configuration."""
        self.endpoint = os.getenv("R2_ENDPOINT", "")
        self.access_key = os.getenv("R2_ACCESS_KEY", "")
        self.secret_key = os.getenv("R2_SECRET_KEY", "")
        self.bucket_name = os.getenv("R2_BUCKET_NAME") or "kinemotion"

        if not all([self.endpoint, self.access_key, self.secret_key]):
            raise ValueError(
                "R2 credentials not configured. Set R2_ENDPOINT, "
                "R2_ACCESS_KEY, and R2_SECRET_KEY environment variables."
            )

        # Initialize S3-compatible client for R2
        self.client = boto3.client(
            "s3",
            endpoint_url=self.endpoint,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name="auto",
        )

    def upload_file(self, local_path: str, remote_key: str) -> str:
        """Upload file to R2 storage.

        Args:
            local_path: Local file path to upload
            remote_key: S3 object key in R2 bucket

        Returns:
            S3 URL of uploaded file

        Raises:
            IOError: If upload fails
        """
        try:
            self.client.upload_file(local_path, self.bucket_name, remote_key)
            return f"{self.endpoint}/{self.bucket_name}/{remote_key}"
        except Exception as e:
            raise OSError(f"Failed to upload to R2: {str(e)}") from e

    def download_file(self, remote_key: str, local_path: str) -> None:
        """Download file from R2 storage.

        Args:
            remote_key: S3 object key in R2 bucket
            local_path: Local path to save downloaded file

        Raises:
            IOError: If download fails
        """
        try:
            self.client.download_file(self.bucket_name, remote_key, local_path)
        except Exception as e:
            raise OSError(f"Failed to download from R2: {str(e)}") from e

    def delete_file(self, remote_key: str) -> None:
        """Delete file from R2 storage.

        Args:
            remote_key: S3 object key in R2 bucket

        Raises:
            IOError: If deletion fails
        """
        try:
            self.client.delete_object(Bucket=self.bucket_name, Key=remote_key)
        except Exception as e:
            raise OSError(f"Failed to delete from R2: {str(e)}") from e

    def put_object(self, key: str, body: bytes) -> str:
        """Put object (bytes) to R2 storage.

        Args:
            key: S3 object key in R2 bucket
            body: Binary content to store

        Returns:
            S3 URL of uploaded object

        Raises:
            IOError: If upload fails
        """
        try:
            self.client.put_object(Bucket=self.bucket_name, Key=key, Body=body)
            return f"{self.endpoint}/{self.bucket_name}/{key}"
        except Exception as e:
            raise OSError(f"Failed to put object to R2: {str(e)}") from e


# ========== FastAPI Application ==========

app = FastAPI(
    title="Kinemotion Backend API",
    description="Video-based kinematic analysis API for athletic performance",
    version="0.1.0",
)

# ========== CORS Configuration (added FIRST for correct middleware order) ==========

cors_origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:8080",
    "http://localhost:8888",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:8080",
    "http://127.0.0.1:8888",
]

# Add production origins from environment variable if configured
cors_origins_env = os.getenv("CORS_ORIGINS", "").strip()
if cors_origins_env:
    # Split by comma and strip whitespace from each origin
    prod_origins = [origin.strip() for origin in cors_origins_env.split(",")]
    cors_origins.extend(prod_origins)

# Add CORS middleware FIRST so it wraps all other middleware (LIFO order)
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=[
        "Accept",
        "Accept-Language",
        "Content-Language",
        "Content-Type",
        "Authorization",
        "X-Request-ID",
        "X-User-ID",
    ],
)

# Add request logging middleware
app.add_middleware(RequestLoggingMiddleware)

# ========== Rate Limiting Configuration ==========


class NoOpLimiter:
    """No-op limiter for testing."""

    def limit(self, limit_string: str) -> Any:  # type: ignore[no-untyped-def]
        """Decorator that does nothing."""

        def decorator(func: Any) -> Any:  # type: ignore[no-untyped-def]
            return func

        return decorator


# Use conditional limiter based on testing state
_testing = os.getenv("TESTING", "").lower() == "true"
limiter: Limiter | NoOpLimiter = (
    NoOpLimiter() if _testing else Limiter(key_func=get_remote_address)
)
app.state.limiter = limiter

if not _testing:
    app.add_exception_handler(
        Exception,
        _rate_limit_exceeded_handler,  # type: ignore[arg-type]
    )

# Initialize R2 client (optional - only if credentials provided)
r2_client: R2StorageClient | None = None
try:
    r2_client = R2StorageClient()
    logger.info("r2_storage_initialized", endpoint=r2_client.endpoint)
except ValueError:
    logger.warning("r2_storage_not_configured", message="R2 credentials not provided")


# ========== Helper Functions ==========


def _validate_video_file(file: UploadFile) -> None:
    """Validate uploaded video file.

    Args:
        file: Uploaded file to validate

    Raises:
        ValueError: If file is invalid
    """
    if not file.filename:
        raise ValueError("File must have a name")

    # Check file extension
    valid_extensions = {".mp4", ".avi", ".mov", ".mkv", ".flv", ".wmv"}
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in valid_extensions:
        raise ValueError(
            f"Invalid video format: {file_ext}. "
            f"Supported formats: {', '.join(valid_extensions)}"
        )

    # Check file size (max 500MB for practical limits)
    if file.size and file.size > 500 * 1024 * 1024:
        raise ValueError("File size exceeds maximum of 500MB")


def _validate_jump_type(jump_type: str) -> str:
    """Validate jump type parameter (case-insensitive).

    Args:
        jump_type: Jump type to validate

    Returns:
        Normalized jump type (lowercase)

    Raises:
        ValueError: If jump type is invalid
    """
    normalized = jump_type.lower()
    valid_types: set[str] = {"drop_jump", "cmj"}
    if normalized not in valid_types:
        raise ValueError(
            f"Invalid jump type: {jump_type}. Must be one of: {', '.join(valid_types)}"
        )
    return normalized


def _validate_referer(referer: str | None, x_test_password: str | None = None) -> None:
    """Validate request comes from authorized frontend.

    Args:
        referer: Referer header from request
        x_test_password: Optional test password header for debugging

    Raises:
        HTTPException: If referer is missing or not from allowed origins
    """
    # Skip validation in test mode
    if os.getenv("TESTING", "").lower() == "true":
        return

    # Allow bypass with test password (for curl testing, debugging)
    test_password = os.getenv("TEST_PASSWORD")
    if test_password and x_test_password == test_password:
        return  # Bypass referer check

    allowed_referers = [
        "https://kinemotion.vercel.app",
        "http://localhost:5173",
        "http://localhost:8888",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8888",
    ]

    # Allow additional referers from env var
    referer_env = os.getenv("ALLOWED_REFERERS", "").strip()
    if referer_env:
        additional = [r.strip() for r in referer_env.split(",")]
        allowed_referers.extend(additional)

    if not referer:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Direct API access not allowed. Use the web interface.",
        )

    # Check if referer starts with any allowed origin
    referer_valid = any(referer.startswith(origin) for origin in allowed_referers)

    if not referer_valid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Request must originate from authorized frontend",
        )


async def _process_video_async(
    video_path: str,
    jump_type: JumpType,
    quality: str = "balanced",
) -> dict[str, Any]:
    """Process video and return metrics.

    Args:
        video_path: Path to video file
        jump_type: Type of jump analysis
        quality: Analysis quality preset

    Returns:
        Dictionary with metrics

    Raises:
        ValueError: If video processing fails
    """
    if jump_type == "drop_jump":
        metrics = process_dropjump_video(video_path, quality=quality)
    else:  # cmj
        metrics = process_cmj_video(video_path, quality=quality)

    return cast(dict[str, Any], metrics.to_dict())


# ========== API Endpoints ==========


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, Any]:
    """Health check endpoint.

    Returns:
        Status dictionary with service health information
    """
    # Get kinemotion version safely
    try:
        kinemotion_version = version("kinemotion")
    except Exception:
        kinemotion_version = "unknown"

    return {
        "status": "ok",
        "service": "kinemotion-backend",
        "version": "0.1.0",
        "kinemotion_version": kinemotion_version,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "r2_configured": r2_client is not None,
    }


@app.post("/api/analyze", tags=["Analysis"])
@limiter.limit("3/minute")
async def analyze_video(
    request: Request,
    file: UploadFile = File(...),  # noqa: B008
    jump_type: str = Form("cmj"),  # noqa: B008
    quality: str = Form("balanced"),  # noqa: B008
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

    Returns:
        JSON response with metrics or error details

    Raises:
        HTTPException: If validation or processing fails
    """
    import json
    import time

    start_time = time.time()
    temp_video_path = None
    r2_video_key = None
    r2_results_key = None

    try:
        # Validate referer (prevent direct API access)
        _validate_referer(referer, x_test_password)

        # Validate inputs
        logger.debug(
            "analyze_request_received",
            jump_type=jump_type,
            filename=file.filename,
            file_size=file.size,
        )
        jump_type = _validate_jump_type(jump_type)  # Normalize to lowercase
        await file.seek(0)
        _validate_video_file(file)

        # Create temporary file for processing
        suffix = Path(file.filename or "video.mp4").suffix
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp_file:
            temp_video_path = temp_file.name
            # Write uploaded file to temp location
            content = await file.read()
            temp_file.write(content)

        # Upload to R2 if client available
        if r2_client:
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            r2_video_key = f"videos/{jump_type}/{timestamp}_{file.filename}"
            try:
                r2_client.upload_file(temp_video_path, r2_video_key)
                logger.info("video_uploaded_to_r2", key=r2_video_key)
            except OSError as e:
                logger.error("r2_upload_failed", error=str(e), key=r2_video_key)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to upload video to storage: {str(e)}",
                ) from e

        # Process video with real kinemotion analysis
        metrics = await _process_video_async(temp_video_path, jump_type, quality)  # type: ignore[arg-type]
        logger.info(
            "video_analysis_completed",
            jump_type=jump_type,
            metrics_count=len(metrics),
        )

        # Upload results to R2 if client available
        results_url = None
        if r2_client:
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            r2_results_key = f"results/{jump_type}/{timestamp}_results.json"
            try:
                results_json = json.dumps(metrics, indent=2)
                results_url = r2_client.put_object(
                    r2_results_key, results_json.encode()
                )
                logger.info(
                    "results_uploaded_to_r2", key=r2_results_key, url=results_url
                )
            except OSError as e:
                # Log error but don't fail - results still available in response
                logger.warning(
                    "r2_results_upload_failed", error=str(e), key=r2_results_key
                )

        processing_time = time.time() - start_time

        # Build successful response
        jump_type_display = "drop_jump" if jump_type == "drop_jump" else "cmj"
        response = AnalysisResponse(
            status_code=200,
            message=f"Successfully analyzed {jump_type_display} video",
            metrics=metrics,
            results_url=results_url,
            processing_time_s=processing_time,
        )

        return JSONResponse(
            status_code=200,
            content=response.to_dict(),
        )

    except ValueError as e:
        processing_time = time.time() - start_time
        error_message = str(e)
        logger.warning(
            "validation_error",
            error=error_message,
            processing_time_s=processing_time,
        )
        response = AnalysisResponse(
            status_code=422,
            message="Validation error",
            error=error_message,
            processing_time_s=processing_time,
        )
        return JSONResponse(
            status_code=422,
            content=response.to_dict(),
        )

    except Exception as e:
        processing_time = time.time() - start_time
        error_detail = f"{type(e).__name__}: {str(e)}"
        logger.error(
            "video_analysis_failed",
            error=error_detail,
            processing_time_s=processing_time,
            exc_info=True,
        )

        response = AnalysisResponse(
            status_code=500,
            message="Video analysis failed",
            error=error_detail,
            processing_time_s=processing_time,
        )
        return JSONResponse(
            status_code=500,
            content=response.to_dict(),
        )

    finally:
        # Clean up temporary video file
        if temp_video_path and Path(temp_video_path).exists():
            try:
                Path(temp_video_path).unlink()
                logger.debug("temp_file_cleaned", path=temp_video_path)
            except OSError as e:
                logger.warning(
                    "temp_file_cleanup_failed", path=temp_video_path, error=str(e)
                )

        # Clean up R2 video if results failed (optional - adjust based on policy)
        # if r2_client and r2_video_key and not results_url:
        #     try:
        #         r2_client.delete_file(r2_video_key)
        #     except IOError as e:
        #         print(f"Warning: Failed to delete R2 video: {e}")


@app.post("/api/analyze-local", tags=["Analysis"])
@limiter.limit("3/minute")
async def analyze_local_video(
    request: Request,
    video_path: str = Form(...),  # noqa: B008
    jump_type: str = Form("cmj"),  # noqa: B008
    quality: str = Form("balanced"),  # noqa: B008
) -> JSONResponse:
    """Analyze video from local filesystem.

    Development endpoint for testing with local video files.

    Args:
        video_path: Path to local video file
        jump_type: Type of jump ("drop_jump" or "cmj")
        quality: Analysis quality preset

    Returns:
        JSON response with metrics

    Raises:
        HTTPException: If video not found or processing fails
    """
    import time

    start_time = time.time()

    try:
        # Validate inputs
        jump_type = _validate_jump_type(jump_type)  # Normalize to lowercase

        if not Path(video_path).exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Video file not found: {video_path}",
            )

        # Process video
        metrics = await _process_video_async(video_path, jump_type, quality)  # type: ignore[arg-type]

        processing_time = time.time() - start_time

        response = AnalysisResponse(
            status_code=200,
            message=f"Successfully analyzed {jump_type} video",
            metrics=metrics,
            processing_time_s=processing_time,
        )

        return JSONResponse(
            status_code=200,
            content=response.to_dict(),
        )

    except ValueError as e:
        processing_time = time.time() - start_time
        response = AnalysisResponse(
            status_code=422,
            message="Validation error",
            error=str(e),
            processing_time_s=processing_time,
        )
        return JSONResponse(
            status_code=422,
            content=response.to_dict(),
        )

    except Exception as e:
        processing_time = time.time() - start_time
        error_detail = f"{type(e).__name__}: {str(e)}"
        logger.error(
            "local_video_analysis_failed",
            error=error_detail,
            video_path=video_path,
            processing_time_s=processing_time,
            exc_info=True,
        )

        response = AnalysisResponse(
            status_code=500,
            message="Video analysis failed",
            error=error_detail,
            processing_time_s=processing_time,
        )
        return JSONResponse(
            status_code=500,
            content=response.to_dict(),
        )


# ========== Error Handlers ==========


@app.get("/determinism/platform-info", tags=["Determinism"])
async def get_platform_info() -> dict[str, Any]:
    """Get platform info for cross-platform determinism testing."""
    import platform

    import cv2
    import numpy as np

    return {
        "platform": {
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
        },
        "libraries": {
            "numpy": np.__version__,
            "opencv": cv2.__version__,
        },
    }


@app.post("/determinism/extract-landmarks", tags=["Determinism"])
async def extract_landmarks_determinism(video: UploadFile = File(...)) -> JSONResponse:  # noqa: B008
    """Extract raw MediaPipe landmarks for cross-platform comparison."""
    import platform

    from kinemotion.core.pose import PoseTracker
    from kinemotion.core.video_io import VideoProcessor

    with tempfile.NamedTemporaryFile(delete=False, suffix=".MOV") as tmp:
        content = await video.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        tracker = PoseTracker()
        video_proc = VideoProcessor(tmp_path)

        all_landmarks = []
        frame_idx = 0

        while True:
            ret, frame = video_proc.cap.read()
            if not ret:
                break

            landmarks = tracker.process_frame(frame)

            if landmarks:
                frame_landmarks = {
                    "frame": frame_idx,
                    "landmarks": {
                        name: {
                            "x": float(coords[0]),
                            "y": float(coords[1]),
                            "visibility": float(coords[2]),
                        }
                        for name, coords in landmarks.items()
                    },
                }
            else:
                frame_landmarks = {"frame": frame_idx, "landmarks": None}

            all_landmarks.append(frame_landmarks)
            frame_idx += 1

        video_proc.close()

        return JSONResponse(
            content={
                "video_filename": video.filename,
                "platform": platform.machine(),
                "num_frames": frame_idx,
                "landmarks": all_landmarks,
            }
        )

    finally:
        os.unlink(tmp_path)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Any, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions with consistent response format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": exc.status_code,
            "message": "HTTP Error",
            "error": exc.detail,
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Any, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    error_detail = f"{type(exc).__name__}: {str(exc)}"
    logger.error(
        "unhandled_exception",
        error=error_detail,
        exc_info=True,
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": 500,
            "message": "Internal server error",
            "error": error_detail,
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
