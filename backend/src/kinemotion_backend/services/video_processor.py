from typing import Any, cast

from kinemotion import process_cmj_video, process_dropjump_video
from kinemotion.core.timing import Timer


class VideoProcessorService:
    """Service for processing video files and extracting kinematic metrics."""

    @staticmethod
    async def process_video_async(
        video_path: str,
        jump_type: str,
        quality: str = "balanced",
        output_video: str | None = None,
        timer: Timer | None = None,
        pose_tracker: object | None = None,
    ) -> dict[str, Any]:
        """Process video and return metrics.

        Args:
            video_path: Path to video file
            jump_type: Type of jump analysis
            quality: Analysis quality preset
            output_video: Optional path for debug video output
            timer: Optional Timer for measuring operations
            pose_tracker: Optional shared tracker instance (type varies by backend)

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
                pose_tracker=pose_tracker,  # type: ignore[arg-type]
            )
        else:  # cmj
            metrics = process_cmj_video(
                video_path,
                quality=quality,
                output_video=output_video,
                timer=timer,
                pose_tracker=pose_tracker,  # type: ignore[arg-type]
            )

        return cast(dict[str, Any], metrics.to_dict())
