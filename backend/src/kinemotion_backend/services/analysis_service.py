from pathlib import Path

from fastapi import UploadFile

from ..models.responses import AnalysisResponse
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
        user_id: str | None = None,
    ) -> AnalysisResponse:
        """Analyze uploaded video file.

        Args:
            file: Uploaded video file
            jump_type: Type of jump analysis
            quality: Analysis quality preset
            user_id: Optional user ID for storage organization

        Returns:
            AnalysisResponse with results and metadata
        """
        import time

        from timer import PerformanceTimer

        start_time = time.time()

        try:
            # Validate inputs
            validate_video_file(file)
            normalized_jump_type = validate_jump_type(jump_type)

            # Generate unique storage key
            storage_key = await self.storage_service.generate_unique_key(
                file.filename or "video.mp4", user_id
            )

            # Save uploaded file to temporary location
            temp_path = self.storage_service.get_temp_file_path(Path(storage_key).name)

            with open(temp_path, "wb") as temp_file:
                content = await file.read()
                temp_file.write(content)

            # Process video
            with PerformanceTimer() as timer:
                metrics = await self.video_processor.process_video_async(
                    video_path=temp_path,
                    jump_type=normalized_jump_type,
                    quality=quality,
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

            # Calculate processing time
            processing_time = time.time() - start_time

            # Clean up temporary file
            Path(temp_path).unlink(missing_ok=True)

            return AnalysisResponse(
                status_code=200,
                message="Analysis completed successfully",
                metrics=metrics,
                results_url=results_url,
                original_video_url=original_video_url,
                processing_time_s=processing_time,
            )

        except Exception as e:
            # Clean up on error
            if "temp_path" in locals():
                Path(temp_path).unlink(missing_ok=True)

            processing_time = time.time() - start_time
            return AnalysisResponse(
                status_code=500,
                message=f"Analysis failed: {str(e)}",
                error=str(e),
                processing_time_s=processing_time,
            )
