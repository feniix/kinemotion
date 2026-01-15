"""Debug overlay visualization for Squat Jump analysis."""

from typing import Any

import cv2
import numpy as np


class SquatJumpDebugOverlayRenderer:
    """Debug overlay renderer for Squat Jump analysis results."""

    def __init__(
        self,
        output_path: str,
        input_width: int,
        input_height: int,
        output_width: int,
        output_height: int,
        fps: float,
        timer: Any = None,
    ):
        """Initialize debug overlay renderer.

        Args:
            output_path: Path to output video file
            input_width: Width of input frames
            input_height: Height of input frames
            output_width: Width of output video
            output_height: Height of output video
            fps: Frames per second for output video
            timer: Optional timer for performance profiling
        """
        self.output_path = output_path
        self.input_width = input_width
        self.input_height = input_height
        self.output_width = output_width
        self.output_height = output_height
        self.fps = fps
        self.timer = timer

        self.writer = None
        self.frame_count = 0

    def __enter__(self):
        """Enter context manager and initialize video writer."""
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # type: ignore[attr-defined]
        self.writer = cv2.VideoWriter(
            self.output_path,
            fourcc,
            self.fps,
            (self.output_width, self.output_height),
        )
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        """Exit context manager and release video writer."""
        if self.writer:
            self.writer.release()

    def write_frame(self, frame: np.ndarray) -> None:
        """Write a frame to the output video.

        Args:
            frame: Annotated frame to write
        """
        if self.writer:
            self.writer.write(frame)
        self.frame_count += 1

    def render_frame(
        self,
        frame: np.ndarray,
        landmarks: list | None,
        frame_index: int,
        metrics: Any = None,
    ) -> np.ndarray:
        """Render debug overlay on a single frame.

        Args:
            frame: Input frame (BGR format)
            landmarks: Pose landmarks for the frame
            frame_index: Frame index for timeline display
            metrics: Analysis metrics for data display

        Returns:
            Annotated frame with debug overlay
        """
        # Create a copy to avoid modifying the original
        annotated_frame = frame.copy()

        # Resize if needed
        if self.input_width != self.output_width or self.input_height != self.output_height:
            annotated_frame = cv2.resize(
                annotated_frame,
                (self.output_width, self.output_height),
                interpolation=cv2.INTER_LINEAR,
            )

        # TODO: Implement by Computer Vision Engineer
        # This is a placeholder function that needs to be implemented

        # Placeholder: Just draw basic info
        self._draw_frame_info(annotated_frame, frame_index)

        # Placeholder: Draw landmarks if available
        if landmarks:
            self._draw_landmarks(annotated_frame, landmarks)

        # Placeholder: Draw metrics if available
        if metrics:
            self._draw_metrics(annotated_frame, metrics)

        return annotated_frame

    def _draw_frame_info(self, frame: np.ndarray, frame_index: int) -> None:
        """Draw frame information overlay.

        Args:
            frame: Frame to draw on
            frame_index: Current frame index
        """
        # Draw frame counter
        cv2.putText(
            frame,
            f"Frame: {frame_index}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2,
            cv2.LINE_AA,
        )

    def _draw_landmarks(self, frame: np.ndarray, landmarks: list) -> None:
        """Draw pose landmarks on frame.

        Args:
            frame: Frame to draw on
            landmarks: Pose landmarks data
        """
        # TODO: Implement by Computer Vision Engineer
        # This should draw key joints and connections based on landmarks
        pass

    def _draw_metrics(self, frame: np.ndarray, metrics: Any) -> None:
        """Draw metrics information on frame.

        Args:
            frame: Frame to draw on
            metrics: Metrics object with analysis results
        """
        # TODO: Implement by Computer Vision Engineer
        # This should display current phase, key metrics, and highlights
        y_offset = 60

        # Placeholder: Display some basic info
        if hasattr(metrics, "jump_height"):
            text = f"Jump Height: {metrics.jump_height:.3f} m"
            cv2.putText(
                frame,
                text,
                (10, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )
            y_offset += 30

        if hasattr(metrics, "flight_time"):
            text = f"Flight Time: {metrics.flight_time * 1000:.1f} ms"
            cv2.putText(
                frame,
                text,
                (10, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )
            y_offset += 30

        if hasattr(metrics, "squat_hold_duration"):
            text = f"Squat Hold: {metrics.squat_hold_duration * 1000:.1f} ms"
            cv2.putText(
                frame,
                text,
                (10, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )
            y_offset += 30

        if hasattr(metrics, "concentric_duration"):
            text = f"Concentric: {metrics.concentric_duration * 1000:.1f} ms"
            cv2.putText(
                frame,
                text,
                (10, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )
