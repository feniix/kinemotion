from pathlib import Path

from fastapi import UploadFile

from ..models.responses import AnalysisResponse, MetricsData
from .storage_service import StorageService
from .validation import validate_jump_type, validate_video_file
from .video_processor import VideoProcessorService


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
        import time

        from kinemotion.core.timing import PerformanceTimer

        start_time = time.time()
        temp_path: str | None = None
        temp_debug_video_path: str | None = None

        # Validate inputs (let ValueError propagate to route handler)
        validate_video_file(file)
        normalized_jump_type = validate_jump_type(jump_type)

        try:
            # Generate unique storage key
            storage_key = await self.storage_service.generate_unique_key(
                file.filename or "video.mp4", user_id
            )

            # Save uploaded file to temporary location
            temp_path = self.storage_service.get_temp_file_path(Path(storage_key).name)
            assert temp_path is not None

            with open(temp_path, "wb") as temp_file:
                content = await file.read()
                # Check file size from actual content
                if len(content) > 500 * 1024 * 1024:
                    raise ValueError("File size exceeds maximum of 500MB")
                temp_file.write(content)

            # Create temporary debug video path if debug is enabled
            import tempfile

            if debug:
                temp_debug = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
                temp_debug_video_path = temp_debug.name
                temp_debug.close()

            # Process video
            timer = PerformanceTimer()
            with timer.measure("video_processing"):
                metrics = await self.video_processor.process_video_async(
                    video_path=temp_path,
                    jump_type=normalized_jump_type,
                    quality=quality,
                    output_video=temp_debug_video_path,
                    timer=timer,
                )

            # Upload original video to storage
            original_video_url = await self.storage_service.upload_video(
                temp_path, f"videos/{storage_key}"
            )

            # Upload analysis results
            results_url = await self.storage_service.upload_analysis_results(
                metrics, f"results/{storage_key}.json"
            )

            # Upload debug video if it was created
            debug_video_url = None
            if temp_debug_video_path and Path(temp_debug_video_path).exists():
                if Path(temp_debug_video_path).stat().st_size > 0:
                    debug_video_url = await self.storage_service.upload_video(
                        temp_debug_video_path, f"debug_videos/{storage_key}_debug.mp4"
                    )

            # Calculate processing time
            processing_time = time.time() - start_time

            # Clean up temporary files
            Path(temp_path).unlink(missing_ok=True)
            if temp_debug_video_path and Path(temp_debug_video_path).exists():
                Path(temp_debug_video_path).unlink(missing_ok=True)

            return AnalysisResponse(
                status=200,
                message="Analysis completed successfully",
                metrics=MetricsData(**metrics),
                results_url=results_url,
                debug_video_url=debug_video_url,
                original_video_url=original_video_url,
                error=None,
                processing_time_s=processing_time,
            )

        except ValueError:
            # Clean up on validation error and re-raise
            if temp_path is not None:
                Path(temp_path).unlink(missing_ok=True)
            if temp_debug_video_path and Path(temp_debug_video_path).exists():
                Path(temp_debug_video_path).unlink(missing_ok=True)
            raise

        except Exception as e:
            # Clean up on other errors
            if temp_path is not None:
                Path(temp_path).unlink(missing_ok=True)
            if temp_debug_video_path and Path(temp_debug_video_path).exists():
                Path(temp_debug_video_path).unlink(missing_ok=True)

            processing_time = time.time() - start_time
            return AnalysisResponse(
                status=500,
                message=f"Analysis failed: {str(e)}",
                error=str(e),
                metrics=None,
                results_url=None,
                debug_video_url=None,
                original_video_url=None,
                processing_time_s=processing_time,
            )
