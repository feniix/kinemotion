from typing import Any, cast

import structlog
from kinemotion import process_cmj_video, process_dropjump_video
from kinemotion.core.pose import PoseTracker
from kinemotion.core.timing import Timer

logger = structlog.get_logger(__name__)


class VideoProcessorService:
    """Service for processing video files and extracting kinematic metrics."""

    @staticmethod
    async def process_video_async(
        video_path: str,
        jump_type: str,
        quality: str = "balanced",
        output_video: str | None = None,
        timer: Timer | None = None,
        pose_tracker: PoseTracker | None = None,
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
        logger.info(
            "video_processor_starting",
            jump_type=jump_type,
            quality=quality,
            video_path=video_path,
            has_debug_output=output_video is not None,
        )

        try:
            if jump_type == "drop_jump":
                logger.info("processing_drop_jump_video")
                metrics = process_dropjump_video(
                    video_path,
                    quality=quality,
                    output_video=output_video,
                    timer=timer,
                    pose_tracker=pose_tracker,
                )
            else:  # cmj
                logger.info("processing_cmj_video")
                metrics = process_cmj_video(
                    video_path,
                    quality=quality,
                    output_video=output_video,
                    timer=timer,
                    pose_tracker=pose_tracker,
                )

            logger.info(
                "video_processor_completed",
                jump_type=jump_type,
                metrics_extracted=True,
            )

            return cast(dict[str, Any], metrics.to_dict())
        except Exception as e:
            logger.error(
                "video_processor_failed",
                jump_type=jump_type,
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True,
            )
            raise
