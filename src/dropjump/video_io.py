"""Video I/O and debug overlay rendering."""


import cv2
import numpy as np

from .contact_detection import ContactState, compute_average_foot_position
from .kinematics import DropJumpMetrics


class VideoProcessor:
    """
    Handles video reading and processing.

    IMPORTANT: This class preserves the exact aspect ratio of the source video.
    No dimensions are hardcoded - all dimensions are extracted from actual frame data.
    """

    def __init__(self, video_path: str):
        """
        Initialize video processor.

        Args:
            video_path: Path to input video file
        """
        self.video_path = video_path
        self.cap = cv2.VideoCapture(video_path)

        if not self.cap.isOpened():
            raise ValueError(f"Could not open video: {video_path}")

        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # Read first frame to get actual dimensions
        # This is critical for preserving aspect ratio, especially with mobile videos
        # that have rotation metadata. OpenCV properties (CAP_PROP_FRAME_WIDTH/HEIGHT)
        # may return incorrect dimensions, so we read the actual frame data.
        ret, first_frame = self.cap.read()
        if ret:
            # frame.shape is (height, width, channels) - extract actual dimensions
            self.height, self.width = first_frame.shape[:2]
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Reset to beginning
        else:
            # Fallback to video properties if can't read frame
            self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    def read_frame(self) -> np.ndarray | None:
        """Read next frame from video."""
        ret, frame = self.cap.read()
        return frame if ret else None

    def reset(self) -> None:
        """Reset video to beginning."""
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    def close(self) -> None:
        """Release video capture."""
        self.cap.release()

    def __enter__(self) -> "VideoProcessor":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore[no-untyped-def]
        self.close()


class DebugOverlayRenderer:
    """Renders debug information on video frames."""

    def __init__(
        self,
        output_path: str,
        width: int,
        height: int,
        fps: float,
    ):
        """
        Initialize overlay renderer.

        Args:
            output_path: Path for output video
            width: Frame width (from source video)
            height: Frame height (from source video)
            fps: Frames per second
        """
        self.width = width
        self.height = height

        # Try H.264 codec first (better quality/compatibility), fallback to mp4v
        fourcc = cv2.VideoWriter_fourcc(*"avc1")  # type: ignore[attr-defined]
        # IMPORTANT: cv2.VideoWriter expects (width, height) tuple - NOT (height, width)
        self.writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        # Check if writer opened successfully, fallback to mp4v if not
        if not self.writer.isOpened():
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # type: ignore[attr-defined]
            self.writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        if not self.writer.isOpened():
            raise ValueError(
                f"Failed to create video writer for {output_path} with dimensions {width}x{height}"
            )

    def render_frame(
        self,
        frame: np.ndarray,
        landmarks: dict[str, tuple[float, float, float]] | None,
        contact_state: ContactState,
        frame_idx: int,
        metrics: DropJumpMetrics | None = None,
    ) -> np.ndarray:
        """
        Render debug overlay on frame.

        Args:
            frame: Original video frame
            landmarks: Pose landmarks for this frame
            contact_state: Ground contact state
            frame_idx: Current frame index
            metrics: Drop-jump metrics (optional)

        Returns:
            Frame with debug overlay
        """
        annotated = frame.copy()

        # Draw landmarks if available
        if landmarks:
            foot_x, foot_y = compute_average_foot_position(landmarks)
            px = int(foot_x * self.width)
            py = int(foot_y * self.height)

            # Draw foot position circle
            color = (
                (0, 255, 0) if contact_state == ContactState.ON_GROUND else (0, 0, 255)
            )
            cv2.circle(annotated, (px, py), 10, color, -1)

            # Draw individual foot landmarks
            foot_keys = ["left_ankle", "right_ankle", "left_heel", "right_heel"]
            for key in foot_keys:
                if key in landmarks:
                    x, y, vis = landmarks[key]
                    if vis > 0.5:
                        lx = int(x * self.width)
                        ly = int(y * self.height)
                        cv2.circle(annotated, (lx, ly), 5, (255, 255, 0), -1)

        # Draw contact state
        state_text = f"State: {contact_state.value}"
        state_color = (
            (0, 255, 0) if contact_state == ContactState.ON_GROUND else (0, 0, 255)
        )
        cv2.putText(
            annotated,
            state_text,
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            state_color,
            2,
        )

        # Draw frame number
        cv2.putText(
            annotated,
            f"Frame: {frame_idx}",
            (10, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )

        # Draw metrics if in relevant phase
        if metrics:
            y_offset = 110
            if (
                metrics.contact_start_frame
                and metrics.contact_end_frame
                and metrics.contact_start_frame
                <= frame_idx
                <= metrics.contact_end_frame
            ):
                cv2.putText(
                    annotated,
                    "GROUND CONTACT",
                    (10, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2,
                )
                y_offset += 40

            if (
                metrics.flight_start_frame
                and metrics.flight_end_frame
                and metrics.flight_start_frame <= frame_idx <= metrics.flight_end_frame
            ):
                cv2.putText(
                    annotated,
                    "FLIGHT PHASE",
                    (10, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 0, 255),
                    2,
                )
                y_offset += 40

            if metrics.peak_height_frame == frame_idx:
                cv2.putText(
                    annotated,
                    "PEAK HEIGHT",
                    (10, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 0, 255),
                    2,
                )

        return annotated

    def write_frame(self, frame: np.ndarray) -> None:
        """
        Write frame to output video.

        Args:
            frame: Video frame with shape (height, width, 3)

        Raises:
            ValueError: If frame dimensions don't match video dimensions
        """
        # Validate frame dimensions match expected output dimensions
        frame_height, frame_width = frame.shape[:2]
        if frame_height != self.height or frame_width != self.width:
            raise ValueError(
                f"Frame dimensions ({frame_width}x{frame_height}) don't match "
                f"video dimensions ({self.width}x{self.height}). "
                f"Aspect ratio must be preserved from source video."
            )
        self.writer.write(frame)

    def close(self) -> None:
        """Release video writer."""
        self.writer.release()

    def __enter__(self) -> "DebugOverlayRenderer":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore[no-untyped-def]
        self.close()
