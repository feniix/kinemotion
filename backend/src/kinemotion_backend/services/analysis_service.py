import tempfile
import time
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

from fastapi import UploadFile

from ..logging_config import get_logger
from ..models.responses import AnalysisResponse, MetricsData
from .interpretation_service import interpret_metrics
from .storage_service import StorageService
from .validation import validate_jump_type, validate_video_file
from .video_processor import VideoProcessorService

logger = get_logger(__name__)


def _cleanup_temp_files(temp_path: str | None, debug_path: str | None) -> None:
    """Clean up temporary files.

    Args:
        temp_path: Path to main temporary file
        debug_path: Path to debug video file
    """
    if temp_path is not None:
        Path(temp_path).unlink(missing_ok=True)
    if debug_path is not None and Path(debug_path).exists():
        Path(debug_path).unlink(missing_ok=True)


@contextmanager
def _temp_file_context() -> Generator[dict[str, str | None], None, None]:
    """Context manager for temporary file cleanup.

    Yields:
        Dictionary to track temp_path and debug_path
    """
    paths: dict[str, str | None] = {"temp_path": None, "debug_path": None}
    try:
        yield paths
    finally:
        _cleanup_temp_files(paths["temp_path"], paths["debug_path"])


def _create_error_response(
    status_code: int,
    message: str,
    error: str,
    processing_time: float,
) -> AnalysisResponse:
    """Create an error response.

    Args:
        status_code: HTTP status code
        message: Response message
        error: Error string
        processing_time: Processing time in seconds

    Returns:
        AnalysisResponse with error details
    """
    return AnalysisResponse(
        status_code=status_code,
        message=message,
        error=error,
        metrics=None,
        results_url=None,
        debug_video_url=None,
        original_video_url=None,
        processing_time_s=processing_time,
    )


class AnalysisService:
    """Service for orchestrating video analysis workflow."""

    def __init__(self) -> None:
        """Initialize analysis service with required dependencies."""
        self.storage_service = StorageService()
        self.video_processor = VideoProcessorService()

    async def analyze_video(
        self,
        file: UploadFile,
        jump_type: str,
        quality: str = "balanced",
        debug: bool = False,
        user_id: str | None = None,
        sex: str | None = None,
        age: int | None = None,
        training_level: str | None = None,
    ) -> AnalysisResponse:
        """Analyze uploaded video file.

        Args:
            file: Uploaded video file
            jump_type: Type of jump analysis
            quality: Analysis quality preset
            debug: Whether to generate debug overlay video
            user_id: Optional user ID for storage organization
            sex: Biological sex for normative comparison (optional)
            age: Athlete age in years for normative comparison (optional)
            training_level: Training level for normative comparison (optional)

        Returns:
            AnalysisResponse with results and metadata

        Raises:
            ValueError: If validation fails
        """
        from kinemotion.core.timing import PerformanceTimer

        start_time = time.perf_counter()

        # Validate inputs (let ValueError propagate to route handler)
        logger.info("validating_video_file")
        validation_start = time.perf_counter()
        validate_video_file(file)
        logger.info(
            "validating_video_file_completed",
            duration_ms=round((time.perf_counter() - validation_start) * 1000, 1),
        )

        logger.info("validating_jump_type", jump_type=jump_type)
        jump_type_start = time.perf_counter()
        normalized_jump_type = validate_jump_type(jump_type)
        logger.info(
            "validating_jump_type_completed",
            normalized_jump_type=normalized_jump_type,
            duration_ms=round((time.perf_counter() - jump_type_start) * 1000, 1),
        )

        with _temp_file_context() as paths:
            try:
                return await self._process_video(
                    file=file,
                    normalized_jump_type=normalized_jump_type,
                    quality=quality,
                    debug=debug,
                    user_id=user_id,
                    start_time=start_time,
                    paths=paths,
                    timer_class=PerformanceTimer,
                    sex=sex,
                    age=age,
                )
            except ValueError as e:
                logger.error(
                    "video_analysis_validation_error",
                    error=str(e),
                    processing_time_s=round(time.perf_counter() - start_time, 2),
                )
                raise

            except Exception as e:
                processing_time = time.perf_counter() - start_time
                logger.error(
                    "video_analysis_failed",
                    error=str(e),
                    error_type=type(e).__name__,
                    processing_time_s=round(processing_time, 2),
                    exc_info=True,
                )
                return _create_error_response(
                    status_code=500,
                    message=f"Analysis failed: {e!s}",
                    error=str(e),
                    processing_time=processing_time,
                )

    async def _process_video(
        self,
        file: UploadFile,
        normalized_jump_type: str,
        quality: str,
        debug: bool,
        user_id: str | None,
        start_time: float,
        paths: dict[str, str | None],
        timer_class: type,
        sex: str | None = None,
        age: int | None = None,
    ) -> AnalysisResponse:
        """Process video and return analysis response.

        Args:
            file: Uploaded video file
            normalized_jump_type: Validated jump type
            quality: Analysis quality preset
            debug: Whether to generate debug overlay
            user_id: Optional user ID
            start_time: Start time for processing duration
            paths: Dictionary to track temp file paths for cleanup
            timer_class: PerformanceTimer class for timing
            sex: Biological sex for normative comparison
            age: Athlete age in years for normative comparison

        Returns:
            AnalysisResponse with results
        """
        # Generate unique storage key
        logger.info("generating_storage_key", filename=file.filename)
        key_start = time.perf_counter()
        storage_key = await self.storage_service.generate_unique_key(
            file.filename or "video.mp4", user_id
        )
        logger.info(
            "generating_storage_key_completed",
            storage_key=storage_key,
            duration_ms=round((time.perf_counter() - key_start) * 1000, 1),
        )

        # Save uploaded file to temporary location
        temp_path = self.storage_service.get_temp_file_path(Path(storage_key).name)
        paths["temp_path"] = temp_path

        logger.info("saving_uploaded_file", temp_path=temp_path)
        save_start = time.perf_counter()
        content = await file.read()

        if len(content) > 500 * 1024 * 1024:
            raise ValueError("File size exceeds maximum of 500MB")

        with open(temp_path, "wb") as temp_file:
            temp_file.write(content)

        logger.info(
            "saving_uploaded_file_completed",
            file_size_mb=round(len(content) / (1024 * 1024), 2),
            duration_ms=round((time.perf_counter() - save_start) * 1000, 1),
        )

        # Create temporary debug video path if debug is enabled
        temp_debug_video_path: str | None = None
        if debug:
            temp_debug = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
            temp_debug_video_path = temp_debug.name
            temp_debug.close()
            paths["debug_path"] = temp_debug_video_path
            logger.info("debug_video_path_created", debug_video_path=temp_debug_video_path)

        # Process video with detailed timing
        logger.info("video_processing_started")
        timer = timer_class()
        with timer.measure("video_processing"):
            metrics = await self.video_processor.process_video_async(
                video_path=temp_path,
                jump_type=normalized_jump_type,
                quality=quality,
                output_video=temp_debug_video_path,
                timer=timer,
            )

        self._log_stage_metrics(timer.get_metrics())

        # Upload files to storage
        original_video_url = await self._upload_original_video(temp_path, storage_key)
        results_url = await self._upload_results(metrics, storage_key)
        debug_video_url = await self._upload_debug_video(temp_debug_video_path, storage_key)

        # Generate coaching interpretations from metrics
        metrics_data = metrics.get("data") or {}
        interpretation = interpret_metrics(normalized_jump_type, metrics_data, sex=sex, age=age)
        if interpretation:
            metrics["interpretation"] = interpretation

        # Build response
        processing_time = time.perf_counter() - start_time
        metrics_count = len(metrics.get("data", {}))

        serialization_start = time.perf_counter()
        response = AnalysisResponse(
            status_code=200,
            message="Analysis completed successfully",
            metrics=MetricsData(**metrics),
            results_url=results_url,
            debug_video_url=debug_video_url,
            original_video_url=original_video_url,
            error=None,
            processing_time_s=processing_time,
        )
        logger.info(
            "response_serialization",
            duration_ms=round((time.perf_counter() - serialization_start) * 1000, 1),
        )

        logger.info(
            "video_analysis_completed",
            jump_type=normalized_jump_type,
            duration_ms=round(processing_time * 1000, 1),
            metrics_count=metrics_count,
        )

        return response

    def _log_stage_metrics(self, stage_metrics: dict[str, float]) -> None:
        """Log individual pipeline stage timings.

        Args:
            stage_metrics: Dictionary of stage names to durations in seconds
        """
        for stage_name, duration_s in stage_metrics.items():
            logger.info(stage_name, duration_ms=round(duration_s * 1000, 1))

        total_duration_s = stage_metrics.get("video_processing", 0)
        logger.info(
            "video_processing_completed",
            total_duration_s=round(total_duration_s, 2),
            duration_ms=round(total_duration_s * 1000, 1),
        )

    async def _upload_original_video(self, temp_path: str, storage_key: str) -> str:
        """Upload original video to storage.

        Args:
            temp_path: Path to temporary video file
            storage_key: Storage key for the file

        Returns:
            URL of uploaded video
        """
        logger.info("uploading_original_video", storage_key=storage_key)
        url = await self.storage_service.upload_video(temp_path, f"videos/{storage_key}")
        logger.info("original_video_uploaded", url=url)
        return url

    async def _upload_results(self, metrics: dict, storage_key: str) -> str:
        """Upload analysis results to storage.

        Args:
            metrics: Analysis metrics dictionary
            storage_key: Storage key for the file

        Returns:
            URL of uploaded results
        """
        logger.info("uploading_analysis_results", storage_key=storage_key)
        results_start = time.perf_counter()
        url = await self.storage_service.upload_analysis_results(
            metrics, f"results/{storage_key}.json"
        )
        logger.info(
            "r2_results_upload",
            duration_ms=round((time.perf_counter() - results_start) * 1000, 1),
            url=url,
            key=f"results/{storage_key}.json",
        )
        return url

    async def _upload_debug_video(self, debug_path: str | None, storage_key: str) -> str | None:
        """Upload debug video to storage if it exists and is non-empty.

        Args:
            debug_path: Path to debug video file
            storage_key: Storage key for the file

        Returns:
            URL of uploaded debug video or None
        """
        if not debug_path or not Path(debug_path).exists():
            return None

        if Path(debug_path).stat().st_size == 0:
            logger.info("debug_video_empty_skipping_upload")
            return None

        logger.info("uploading_debug_video", storage_key=storage_key)
        debug_start = time.perf_counter()
        url = await self.storage_service.upload_video(
            debug_path, f"debug_videos/{storage_key}_debug.mp4"
        )
        logger.info(
            "r2_debug_video_upload",
            duration_ms=round((time.perf_counter() - debug_start) * 1000, 1),
            url=url,
            key=f"debug_videos/{storage_key}_debug.mp4",
        )
        return url
