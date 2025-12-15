"""FastAPI application for Kinemotion video analysis backend.

Real metrics integration with Cloudflare R2 storage for video and results management.
"""

import os
import re
import tempfile
from contextlib import asynccontextmanager
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
from kinemotion.core.pose import PoseTracker
from kinemotion.core.timing import (
    PerformanceTimer,
    Timer,
)
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

from kinemotion_backend.analysis_api import router as analysis_router
from kinemotion_backend.database import get_database_client
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
        debug_video_url: str | None = None,
        original_video_url: str | None = None,
        error: str | None = None,
        processing_time_s: float = 0.0,
    ):
        self.status_code = status_code
        self.message = message
        self.metrics = metrics
        self.results_url = results_url
        self.debug_video_url = debug_video_url
        self.original_video_url = original_video_url
        self.error = error
        self.processing_time_s = processing_time_s

    def to_dict(self) -> dict[str, Any]:
        """Convert response to JSON-serializable dictionary."""
        result: dict[str, Any] = {
            "status_code": self.status_code,
            "message": self.message,
            "processing_time_s": self.processing_time_s,
        }

        if self.metrics is not None:
            result["metrics"] = self.metrics

        if self.results_url is not None:
            result["results_url"] = self.results_url

        if self.debug_video_url is not None:
            result["debug_video_url"] = self.debug_video_url

        if self.original_video_url is not None:
            result["original_video_url"] = self.original_video_url

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
        # Optional: if set, we will return stable public URLs instead of presigned URLs.
        # Example: https://<your-public-domain> (custom domain) or https://<bucket>.<account>.r2.dev
        self.public_base_url = (os.getenv("R2_PUBLIC_BASE_URL") or "").rstrip("/")
        # Fallback: presigned URL expiration seconds (default 7 days, S3 max)
        try:
            self.presign_expiration_s = int(os.getenv("R2_PRESIGN_EXPIRATION_S") or "604800")
        except ValueError:
            self.presign_expiration_s = 604800

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

    def generate_presigned_url(self, key: str, expiration: int = 3600) -> str:
        """Generate presigned URL for object.

        Args:
            key: Object key
            expiration: Expiration in seconds (default 1 hour)

        Returns:
            Presigned URL string

        Raises:
            OSError: If generation fails
        """
        try:
            return self.client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": key},
                ExpiresIn=expiration,
            )
        except Exception as e:
            raise OSError(f"Failed to generate presigned URL: {str(e)}") from e

    def get_object_url(self, key: str) -> str:
        """Return a long-lived shareable URL for an object key.

        Prefers a stable public URL if `R2_PUBLIC_BASE_URL` is configured.
        Otherwise, falls back to a presigned URL with `R2_PRESIGN_EXPIRATION_S`.
        """
        normalized_key = key.lstrip("/")
        if self.public_base_url:
            return f"{self.public_base_url}/{normalized_key}"
        return self.generate_presigned_url(normalized_key, expiration=self.presign_expiration_s)

    def upload_file(self, local_path: str, remote_key: str) -> str:
        """Upload file to R2 storage.

        Args:
            local_path: Local file path to upload
            remote_key: S3 object key in R2 bucket

        Returns:
            Presigned URL of uploaded file

        Raises:
            OSError: If upload fails
        """
        try:
            self.client.upload_file(local_path, self.bucket_name, remote_key)
            return self.get_object_url(remote_key)
        except Exception as e:
            raise OSError(f"Failed to upload to R2: {str(e)}") from e

    def download_file(self, remote_key: str, local_path: str) -> None:
        """Download file from R2 storage.

        Args:
            remote_key: S3 object key in R2 bucket
            local_path: Local path to save downloaded file

        Raises:
            OSError: If download fails
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
            OSError: If deletion fails
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
            Presigned URL of uploaded object

        Raises:
            OSError: If upload fails
        """
        try:
            self.client.put_object(Bucket=self.bucket_name, Key=key, Body=body)
            return self.get_object_url(key)
        except Exception as e:
            raise OSError(f"Failed to put object to R2: {str(e)}") from e


# ========== Global State & Lifespan ==========

global_pose_trackers: dict[str, PoseTracker] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle and global resources."""
    logger.info("initializing_pose_trackers")
    try:
        # Initialize trackers for each quality preset
        # Fast: lower confidence for speed
        global_pose_trackers["fast"] = PoseTracker(
            min_detection_confidence=0.3, min_tracking_confidence=0.3
        )
        # Balanced: standard confidence
        global_pose_trackers["balanced"] = PoseTracker(
            min_detection_confidence=0.5, min_tracking_confidence=0.5
        )
        # Accurate: high confidence
        global_pose_trackers["accurate"] = PoseTracker(
            min_detection_confidence=0.6, min_tracking_confidence=0.6
        )
        logger.info("pose_trackers_initialized")

        yield

    finally:
        # Clean up resources
        logger.info("closing_pose_trackers")
        for tracker in global_pose_trackers.values():
            tracker.close()
        global_pose_trackers.clear()


# ========== FastAPI Application ==========

app = FastAPI(
    title="Kinemotion Backend API",
    description="Video-based kinematic analysis API for athletic performance",
    version="0.1.0",
    lifespan=lifespan,
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

# Include analysis API router
app.include_router(analysis_router)

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
            f"Invalid video format: {file_ext}. Supported formats: {', '.join(valid_extensions)}"
        )

    # Check file size (max 500MB for practical limits)
    # Note: file.size may be None, so we need to check from the file object itself
    max_size = 500 * 1024 * 1024
    if file.size is not None and file.size > max_size:
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
    output_video: str | None = None,
    timer: Timer | None = None,
    pose_tracker: "PoseTracker | None" = None,
) -> dict[str, Any]:
    """Process video and return metrics.

    Args:
        video_path: Path to video file
        jump_type: Type of jump analysis
        quality: Analysis quality preset
        output_video: Optional path for debug video output
        timer: Optional Timer for measuring operations
        pose_tracker: Optional shared PoseTracker instance

    Returns:
        Dictionary with metrics

    Raises:
        ValueError: If video processing fails
    """
    if jump_type == "drop_jump":
        metrics = process_dropjump_video(
            video_path,
            quality=quality,
            output_video=output_video,
            timer=timer,
            pose_tracker=pose_tracker,
        )
    else:  # cmj
        metrics = process_cmj_video(
            video_path,
            quality=quality,
            output_video=output_video,
            timer=timer,
            pose_tracker=pose_tracker,
        )

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

    # Check database connection
    database_connected = False
    try:
        from kinemotion_backend.database import get_database_client

        db_client = get_database_client()
        # Test database with a simple query
        db_client.client.table("analysis_sessions").select("id").limit(1).execute()
        database_connected = True
    except Exception as db_error:
        logger.warning("database_health_check_failed", error=str(db_error))

    return {
        "status": "ok",
        "service": "kinemotion-backend",
        "version": "0.1.0",
        "kinemotion_version": kinemotion_version,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "r2_configured": r2_client is not None,
        "trackers_initialized": len(global_pose_trackers) > 0,
        "database_connected": database_connected,
    }


@app.post("/api/analyze", tags=["Analysis"])
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
    import json
    import time
    import uuid

    start_time = time.time()
    temp_video_path = None
    temp_debug_video_path = None
    r2_video_key = None
    r2_results_key = None
    r2_debug_video_key = None

    upload_id = uuid.uuid4().hex
    upload_suffix = Path(file.filename or "video.mp4").suffix or ".mp4"

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
        # Normalize to lowercase
        jump_type = cast(JumpType, _validate_jump_type(jump_type))
        await file.seek(0)

        # Validate video file
        validation_start = time.time()
        _validate_video_file(file)
        validation_duration = time.time() - validation_start
        logger.info(
            "timing_video_validation",
            duration_ms=round(validation_duration * 1000),
        )

        # Create temporary file for processing
        suffix = Path(file.filename or "video.mp4").suffix
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp_file:
            temp_video_path = temp_file.name
            # Write uploaded file to temp location
            save_start = time.time()
            content = await file.read()

            # Validate file size after reading
            max_size = 500 * 1024 * 1024
            if len(content) > max_size:
                raise ValueError("File size exceeds maximum of 500MB")

            temp_file.write(content)
            save_duration = time.time() - save_start
        logger.info("timing_video_file_save", duration_ms=round(save_duration * 1000))

        # Convert debug string to boolean
        enable_debug = debug.lower() == "true"

        # Create temporary path for debug video output (only if debug enabled)
        temp_debug_video_path = None
        if enable_debug:
            with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_debug:
                temp_debug_video_path = temp_debug.name

        # Upload to R2 if client available
        original_video_url = None
        if r2_client:
            upload_start = time.time()
            r2_video_key = f"videos/{jump_type}/{upload_id}{upload_suffix}"
            try:
                original_video_url = r2_client.upload_file(temp_video_path, r2_video_key)
                upload_duration = time.time() - upload_start
                logger.info(
                    "timing_r2_input_video_upload",
                    key=r2_video_key,
                    url=original_video_url,
                    duration_ms=round(upload_duration * 1000),
                )
            except OSError as e:
                logger.error("r2_upload_failed", error=str(e), key=r2_video_key)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to upload video to storage: {str(e)}",
                ) from e

        # Process video with real kinemotion analysis
        analysis_start = time.time()

        # Initialize timer
        timer = PerformanceTimer()

        # Select appropriate pre-initialized tracker from pool
        # Default to balanced if quality not found or trackers not initialized
        tracker_key = quality.lower()
        if tracker_key not in global_pose_trackers:
            tracker_key = "balanced"

        pose_tracker = global_pose_trackers.get(tracker_key)

        metrics = await _process_video_async(
            temp_video_path,
            jump_type,
            quality,
            output_video=temp_debug_video_path if enable_debug else None,
            timer=timer,
            pose_tracker=pose_tracker,
        )  # type: ignore[arg-type]
        analysis_duration = time.time() - analysis_start

        # Log detailed timing breakdown if available in metadata
        if (
            "metadata" in metrics
            and "processing" in metrics["metadata"]
            and "timing_breakdown_ms" in metrics["metadata"]["processing"]
        ):
            timing_breakdown = metrics["metadata"]["processing"]["timing_breakdown_ms"]
            # Normalize keys: remove special chars, spaces → underscores, lowercase
            normalized_timings = {
                re.sub(r"[^\w\s]", "", stage).lower().replace(" ", "_") + "_ms": duration
                for stage, duration in timing_breakdown.items()
            }
            # Log each timing stage as a separate event for granular monitoring
            for stage_key, duration_ms in normalized_timings.items():
                # Remove "_ms" suffix and create timing event name
                stage_name = stage_key.replace("_ms", "")
                event_name = f"timing_{stage_name}"
                logger.info(event_name, duration_ms=round(duration_ms, 1))

        logger.info(
            "video_analysis_completed",
            jump_type=jump_type,
            metrics_count=len(metrics.get("data", {})),
            duration_ms=round(analysis_duration * 1000),
        )

        # Upload results and debug video to R2 if client available
        results_url = None
        debug_video_url = None

        if r2_client:
            # Upload Metrics JSON
            r2_results_key = f"results/{jump_type}/{upload_id}_results.json"
            try:
                results_upload_start = time.time()
                results_json = json.dumps(metrics, indent=2)
                results_url = r2_client.put_object(r2_results_key, results_json.encode())
                results_upload_duration = time.time() - results_upload_start
                logger.info(
                    "timing_r2_results_upload",
                    key=r2_results_key,
                    url=results_url,
                    duration_ms=round(results_upload_duration * 1000),
                )
            except OSError as e:
                # Log error but don't fail - results still available in response
                logger.warning("r2_results_upload_failed", error=str(e), key=r2_results_key)

            # Upload Debug Video if it was created
            if (
                temp_debug_video_path
                and os.path.exists(temp_debug_video_path)
                and os.path.getsize(temp_debug_video_path) > 0
            ):
                r2_debug_video_key = f"debug_videos/{jump_type}/{upload_id}_debug.mp4"
                try:
                    debug_upload_start = time.time()
                    debug_video_url = r2_client.upload_file(
                        temp_debug_video_path, r2_debug_video_key
                    )
                    debug_upload_duration = time.time() - debug_upload_start
                    logger.info(
                        "timing_r2_debug_video_upload",
                        key=r2_debug_video_key,
                        url=debug_video_url,
                        duration_ms=round(debug_upload_duration * 1000),
                    )
                except OSError as e:
                    logger.warning(
                        "r2_debug_video_upload_failed",
                        error=str(e),
                        key=r2_debug_video_key,
                    )
        processing_time = time.time() - start_time

        # Optionally store analysis session in database if user is authenticated
        user_id = None
        try:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                from kinemotion_backend.auth import SupabaseAuth

                auth = SupabaseAuth()
                token = auth_header.split(" ")[1]
                user_id = auth.get_user_id(token)
                logger.info("user_authenticated_for_analysis", user_id=user_id)
        except Exception as e:
            logger.info("analysis_save_no_auth", reason=str(e))
            user_id = None

        # Store in database if authenticated
        session_id = None
        if user_id:
            try:
                db_client = get_database_client()
                session_record = await db_client.create_analysis_session(
                    user_id=user_id,
                    jump_type=jump_type,
                    quality_preset=quality,
                    analysis_data=metrics,
                    original_video_url=original_video_url,
                    debug_video_url=debug_video_url,
                    results_json_url=results_url,
                    processing_time_s=processing_time,
                    upload_id=upload_id,
                )
                session_id = session_record["id"]
                logger.info(
                    "analysis_session_saved",
                    session_id=session_id,
                    user_id=user_id,
                )
            except Exception as e:
                # Log error but don't fail the analysis - this is optional storage
                logger.warning(
                    "analysis_session_save_failed",
                    error=str(e),
                    user_id=user_id,
                )

        # Build successful response
        jump_type_display = "drop_jump" if jump_type == "drop_jump" else "cmj"
        response = AnalysisResponse(
            status_code=200,
            message=f"Successfully analyzed {jump_type_display} video",
            metrics=metrics,
            results_url=results_url,
            debug_video_url=debug_video_url,
            original_video_url=original_video_url,
            processing_time_s=processing_time,
        )

        # Serialize response to JSON
        serialization_start = time.time()
        response_dict = response.to_dict()
        serialization_duration = time.time() - serialization_start
        logger.info(
            "timing_response_serialization",
            duration_ms=round(serialization_duration * 1000),
        )

        return JSONResponse(
            status_code=200,
            content=response_dict,
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
        # Clean up temporary files
        cleanup_start = time.time()

        # Clean up temporary video file
        if temp_video_path and Path(temp_video_path).exists():
            try:
                Path(temp_video_path).unlink()
                logger.debug("temp_file_cleaned", path=temp_video_path)
            except OSError as e:
                logger.warning("temp_file_cleanup_failed", path=temp_video_path, error=str(e))

        # Clean up temporary debug video file
        if temp_debug_video_path and Path(temp_debug_video_path).exists():
            try:
                Path(temp_debug_video_path).unlink()
                logger.debug("temp_debug_file_cleaned", path=temp_debug_video_path)
            except OSError as e:
                logger.warning(
                    "temp_debug_file_cleanup_failed",
                    path=temp_debug_video_path,
                    error=str(e),
                )

        cleanup_duration = time.time() - cleanup_start
        if cleanup_duration > 0:
            logger.info(
                "timing_temp_file_cleanup",
                duration_ms=round(cleanup_duration * 1000),
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
        jump_type = cast(JumpType, _validate_jump_type(jump_type))

        if not Path(video_path).exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Video file not found: {video_path}",
            )

        # Process video
        # Initialize timer
        timer = PerformanceTimer()

        # Select appropriate pre-initialized tracker from pool
        tracker_key = quality.lower()
        if tracker_key not in global_pose_trackers:
            tracker_key = "balanced"

        pose_tracker = global_pose_trackers.get(tracker_key)

        metrics = await _process_video_async(
            video_path, jump_type, quality, timer=timer, pose_tracker=pose_tracker
        )  # type: ignore[arg-type]

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


@app.post("/determinism/analyze-dropjump", tags=["Determinism"])
async def analyze_dropjump_determinism(video: UploadFile = File(...)) -> dict[str, Any]:  # noqa: B008
    """Run full drop jump analysis without authentication for determinism testing."""
    import platform

    with tempfile.NamedTemporaryFile(delete=False, suffix=".MOV") as tmp:
        content = await video.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        # Run full analysis
        result = process_dropjump_video(tmp_path)

        # Convert to plain dict using to_dict() method
        result_dict = cast(dict[str, Any], result.to_dict())

        # Add platform info
        result_dict["platform_info"] = {
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
        }

        return result_dict

    finally:
        os.unlink(tmp_path)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Any, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions with consistent response format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status_code": exc.status_code,
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
            "status_code": 500,
            "message": "Internal server error",
            "error": error_detail,
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
