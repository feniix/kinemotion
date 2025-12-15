import time
from pathlib import Path

from fastapi import UploadFile

from ..logging_config import get_logger
from ..models.responses import AnalysisResponse, MetricsData
from .storage_service import StorageService
from .validation import validate_jump_type, validate_video_file
from .video_processor import VideoProcessorService

logger = get_logger(__name__)


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
    ) -> AnalysisResponse:
        """Analyze uploaded video file.

        Args:
            file: Uploaded video file
            jump_type: Type of jump analysis
            quality: Analysis quality preset
            debug: Whether to generate debug overlay video
            user_id: Optional user ID for storage organization

        Returns:
            AnalysisResponse with results and metadata

        Raises:
            ValueError: If validation fails
        """
        from kinemotion.core.timing import PerformanceTimer

        start_time = time.time()
        temp_path: str | None = None
        temp_debug_video_path: str | None = None

        # Validate inputs (let ValueError propagate to route handler)
        logger.info("validating_video_file")
        validation_start = time.time()
        validate_video_file(file)
        validation_duration_ms = (time.time() - validation_start) * 1000
        logger.info(
            "validating_video_file_completed",
            duration_ms=round(validation_duration_ms, 1),
        )

        logger.info("validating_jump_type", jump_type=jump_type)
        jump_type_start = time.time()
        normalized_jump_type = validate_jump_type(jump_type)
        jump_type_duration_ms = (time.time() - jump_type_start) * 1000
        logger.info(
            "validating_jump_type_completed",
            normalized_jump_type=normalized_jump_type,
            duration_ms=round(jump_type_duration_ms, 1),
        )

        try:
            # Generate unique storage key
            logger.info("generating_storage_key", filename=file.filename)
            key_start = time.time()
            storage_key = await self.storage_service.generate_unique_key(
                file.filename or "video.mp4", user_id
            )
            key_duration_ms = (time.time() - key_start) * 1000
            logger.info(
                "generating_storage_key_completed",
                storage_key=storage_key,
                duration_ms=round(key_duration_ms, 1),
            )

            # Save uploaded file to temporary location
            logger.info("saving_uploaded_file", temp_path=temp_path)
            save_start = time.time()
            temp_path = self.storage_service.get_temp_file_path(Path(storage_key).name)
            assert temp_path is not None

            with open(temp_path, "wb") as temp_file:
                content = await file.read()
                # Check file size from actual content
                if len(content) > 500 * 1024 * 1024:
                    raise ValueError("File size exceeds maximum of 500MB")
                temp_file.write(content)
            save_duration_ms = (time.time() - save_start) * 1000
            file_size_mb = len(content) / (1024 * 1024)
            logger.info(
                "saving_uploaded_file_completed",
                file_size_mb=round(file_size_mb, 2),
                duration_ms=round(save_duration_ms, 1),
            )

            # Create temporary debug video path if debug is enabled
            import tempfile

            if debug:
                temp_debug = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
                temp_debug_video_path = temp_debug.name
                temp_debug.close()
                logger.info("debug_video_path_created", debug_video_path=temp_debug_video_path)

            # Process video with detailed timing
            logger.info("video_processing_started")
            timer = PerformanceTimer()
            with timer.measure("video_processing"):
                metrics = await self.video_processor.process_video_async(
                    video_path=temp_path,
                    jump_type=normalized_jump_type,
                    quality=quality,
                    output_video=temp_debug_video_path,
                    timer=timer,
                )

            # Log individual pipeline stage timings
            stage_metrics = timer.get_metrics()

            # Log each timing stage individually (for detailed performance tracking)
            for stage_name, duration_s in stage_metrics.items():
                duration_ms = duration_s * 1000
                logger.info(stage_name, duration_ms=round(duration_ms, 1))

            # Log overall processing completion summary
            total_duration_s = stage_metrics.get("video_processing", 0)
            logger.info(
                "video_processing_completed",
                total_duration_s=round(total_duration_s, 2),
                duration_ms=round(total_duration_s * 1000, 1),
            )

            # Upload original video to storage
            logger.info("uploading_original_video", storage_key=storage_key)
            original_video_url = await self.storage_service.upload_video(
                temp_path, f"videos/{storage_key}"
            )
            logger.info("original_video_uploaded", url=original_video_url)

            # Upload analysis results with timing
            logger.info("uploading_analysis_results", storage_key=storage_key)
            results_start = time.time()
            results_url = await self.storage_service.upload_analysis_results(
                metrics, f"results/{storage_key}.json"
            )
            results_duration_ms = (time.time() - results_start) * 1000
            logger.info(
                "r2_results_upload",
                duration_ms=round(results_duration_ms, 1),
                url=results_url,
                key=f"results/{storage_key}.json",
            )

            # Upload debug video if it was created
            debug_video_url = None
            if temp_debug_video_path and Path(temp_debug_video_path).exists():
                if Path(temp_debug_video_path).stat().st_size > 0:
                    logger.info("uploading_debug_video", storage_key=storage_key)
                    debug_start = time.time()
                    debug_video_url = await self.storage_service.upload_video(
                        temp_debug_video_path, f"debug_videos/{storage_key}_debug.mp4"
                    )
                    debug_duration_ms = (time.time() - debug_start) * 1000
                    logger.info(
                        "r2_debug_video_upload",
                        duration_ms=round(debug_duration_ms, 1),
                        url=debug_video_url,
                        key=f"debug_videos/{storage_key}_debug.mp4",
                    )
                else:
                    logger.info("debug_video_empty_skipping_upload")

            # Calculate processing time
            processing_time = time.time() - start_time

            # Count metrics from the data field
            metrics_count = len(metrics.get("data", {}))

            # Log response serialization timing
            serialization_start = time.time()
            response_data = AnalysisResponse(
                status_code=200,
                message="Analysis completed successfully",
                metrics=MetricsData(**metrics),
                results_url=results_url,
                debug_video_url=debug_video_url,
                original_video_url=original_video_url,
                error=None,
                processing_time_s=processing_time,
            )
            serialization_duration_ms = (time.time() - serialization_start) * 1000
            logger.info(
                "response_serialization",
                duration_ms=round(serialization_duration_ms, 1),
            )

            # Clean up temporary files with timing
            logger.info("cleaning_up_temporary_files")
            cleanup_start = time.time()
            Path(temp_path).unlink(missing_ok=True)
            if temp_debug_video_path and Path(temp_debug_video_path).exists():
                Path(temp_debug_video_path).unlink(missing_ok=True)
            cleanup_duration_ms = (time.time() - cleanup_start) * 1000
            logger.info(
                "temp_file_cleanup",
                duration_ms=round(cleanup_duration_ms, 1),
            )

            logger.info(
                "video_analysis_completed",
                jump_type=normalized_jump_type,
                duration_ms=round(processing_time * 1000, 1),
                metrics_count=metrics_count,
            )

            return response_data

        except ValueError as e:
            # Clean up on validation error and re-raise
            logger.error(
                "video_analysis_validation_error",
                error=str(e),
                processing_time_s=round(time.time() - start_time, 2),
            )
            if temp_path is not None:
                Path(temp_path).unlink(missing_ok=True)
            if temp_debug_video_path and Path(temp_debug_video_path).exists():
                Path(temp_debug_video_path).unlink(missing_ok=True)
            raise

        except Exception as e:
            # Clean up on other errors
            processing_time = time.time() - start_time
            logger.error(
                "video_analysis_failed",
                error=str(e),
                error_type=type(e).__name__,
                processing_time_s=round(processing_time, 2),
                exc_info=True,
            )
            if temp_path is not None:
                Path(temp_path).unlink(missing_ok=True)
            if temp_debug_video_path and Path(temp_debug_video_path).exists():
                Path(temp_debug_video_path).unlink(missing_ok=True)

            return AnalysisResponse(
                status_code=500,
                message=f"Analysis failed: {str(e)}",
                error=str(e),
                metrics=None,
                results_url=None,
                debug_video_url=None,
                original_video_url=None,
                processing_time_s=processing_time,
            )
