"""FastAPI application for Kinemotion video analysis backend.

Real metrics integration with Cloudflare R2 storage for video and results management.
"""

import json
import os
import tempfile
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal, cast

import boto3
from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from kinemotion.api import process_cmj_video, process_dropjump_video
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

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
        self.bucket_name = os.getenv("R2_BUCKET_NAME", "kinemotion")

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

# Configure rate limiting (3 video uploads per minute per IP address)
class NoOpLimiter:
    """No-op limiter for testing."""

    def limit(self, limit_string: str) -> Any:  # type: ignore[no-untyped-def]
        """Decorator that does nothing."""
        def decorator(func: Any) -> Any:  # type: ignore[no-untyped-def]
            return func

        return decorator


# Use conditional limiter based on testing state
_testing = os.getenv("TESTING", "").lower() == "true"
limiter: Limiter | NoOpLimiter = NoOpLimiter() if _testing else Limiter(key_func=get_remote_address)
app.state.limiter = limiter

if not _testing:
    app.add_exception_handler(
        Exception,
        _rate_limit_exceeded_handler,  # type: ignore[arg-type]
    )

# Configure CORS for localhost development and production
cors_origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:8080",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:8080",
]

# Add production origins from environment variable if configured
if os.getenv("CORS_ORIGINS"):
    cors_origins.extend(os.getenv("CORS_ORIGINS", "").split(","))

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize R2 client (optional - only if credentials provided)
r2_client: R2StorageClient | None = None
try:
    r2_client = R2StorageClient()
except ValueError:
    pass  # R2 credentials not provided - will error on upload endpoints


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


def _validate_jump_type(jump_type: str) -> None:
    """Validate jump type parameter.

    Args:
        jump_type: Jump type to validate

    Raises:
        ValueError: If jump type is invalid
    """
    valid_types: set[str] = {"drop_jump", "cmj"}
    if jump_type not in valid_types:
        raise ValueError(
            f"Invalid jump type: {jump_type}. Must be one of: {', '.join(valid_types)}"
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
    return {
        "status": "ok",
        "service": "kinemotion-backend",
        "version": "0.1.0",
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
    import time

    start_time = time.time()
    temp_video_path = None
    r2_video_key = None
    r2_results_key = None

    try:
        # Validate inputs
        _validate_jump_type(jump_type)
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
            except OSError as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to upload video to storage: {str(e)}",
                ) from e

        # Process video with real kinemotion analysis
        metrics = await _process_video_async(temp_video_path, jump_type, quality)  # type: ignore[arg-type]

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
            except OSError as e:
                # Log error but don't fail - results still available in response
                print(f"Warning: Failed to upload results to R2: {e}")

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
        print(f"Error during video analysis: {error_detail}")
        print(traceback.format_exc())

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
            except OSError as e:
                print(f"Warning: Failed to delete temp file {temp_video_path}: {e}")

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
        _validate_jump_type(jump_type)

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
        print(f"Error during local video analysis: {error_detail}")
        print(traceback.format_exc())

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
    print(f"Unhandled exception: {error_detail}")
    print(traceback.format_exc())

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
