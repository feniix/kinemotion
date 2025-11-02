"""Debug overlay rendering for drop jump analysis."""

import cv2
import numpy as np

from ..core.pose import compute_center_of_mass
from .analysis import ContactState, compute_average_foot_position
from .kinematics import DropJumpMetrics


class DebugOverlayRenderer:
    """Renders debug information on video frames."""

    def __init__(
        self,
        output_path: str,
        width: int,
        height: int,
        display_width: int,
        display_height: int,
        fps: float,
    ):
        """
        Initialize overlay renderer.

        Args:
            output_path: Path for output video
            width: Encoded frame width (from source video)
            height: Encoded frame height (from source video)
            display_width: Display width (considering SAR)
            display_height: Display height (considering SAR)
            fps: Frames per second
        """
        self.width = width
        self.height = height
        self.display_width = display_width
        self.display_height = display_height
        self.needs_resize = (display_width != width) or (display_height != height)

        # Try H.264 codec first (better quality/compatibility), fallback to mp4v
        fourcc = cv2.VideoWriter_fourcc(*"avc1")
        # IMPORTANT: cv2.VideoWriter expects (width, height) tuple - NOT (height, width)
        # Write at display dimensions so video displays correctly without SAR metadata
        self.writer = cv2.VideoWriter(
            output_path, fourcc, fps, (display_width, display_height)
        )

        # Check if writer opened successfully, fallback to mp4v if not
        if not self.writer.isOpened():
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            self.writer = cv2.VideoWriter(
                output_path, fourcc, fps, (display_width, display_height)
            )

        if not self.writer.isOpened():
            raise ValueError(
                f"Failed to create video writer for {output_path} with dimensions "
                f"{display_width}x{display_height}"
            )

    def render_frame(
        self,
        frame: np.ndarray,
        landmarks: dict[str, tuple[float, float, float]] | None,
        contact_state: ContactState,
        frame_idx: int,
        metrics: DropJumpMetrics | None = None,
        use_com: bool = False,
    ) -> np.ndarray:
        """
        Render debug overlay on frame.

        Args:
            frame: Original video frame
            landmarks: Pose landmarks for this frame
            contact_state: Ground contact state
            frame_idx: Current frame index
            metrics: Drop-jump metrics (optional)
            use_com: Whether to visualize CoM instead of feet (optional)

        Returns:
            Frame with debug overlay
        """
        annotated = frame.copy()

        # Draw landmarks if available
        if landmarks:
            if use_com:
                # Draw center of mass position
                com_x, com_y, _ = compute_center_of_mass(landmarks)  # com_vis not used
                px = int(com_x * self.width)
                py = int(com_y * self.height)

                # Draw CoM with larger circle
                color = (
                    (0, 255, 0)
                    if contact_state == ContactState.ON_GROUND
                    else (0, 0, 255)
                )
                cv2.circle(annotated, (px, py), 15, color, -1)
                cv2.circle(annotated, (px, py), 17, (255, 255, 255), 2)  # White border

                # Draw body segments for reference
                # Draw hip midpoint
                if "left_hip" in landmarks and "right_hip" in landmarks:
                    lh_x, lh_y, _ = landmarks["left_hip"]
                    rh_x, rh_y, _ = landmarks["right_hip"]
                    hip_x = int((lh_x + rh_x) / 2 * self.width)
                    hip_y = int((lh_y + rh_y) / 2 * self.height)
                    cv2.circle(
                        annotated, (hip_x, hip_y), 8, (255, 165, 0), -1
                    )  # Orange
                    # Draw line from hip to CoM
                    cv2.line(annotated, (hip_x, hip_y), (px, py), (255, 165, 0), 2)
            else:
                # Draw foot position (original method)
                foot_x, foot_y = compute_average_foot_position(landmarks)
                px = int(foot_x * self.width)
                py = int(foot_y * self.height)

                # Draw foot position circle
                color = (
                    (0, 255, 0)
                    if contact_state == ContactState.ON_GROUND
                    else (0, 0, 255)
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
            ValueError: If frame dimensions don't match expected encoded dimensions
        """
        # Validate frame dimensions match expected encoded dimensions
        frame_height, frame_width = frame.shape[:2]
        if frame_height != self.height or frame_width != self.width:
            raise ValueError(
                f"Frame dimensions ({frame_width}x{frame_height}) don't match "
                f"source dimensions ({self.width}x{self.height}). "
                f"Aspect ratio must be preserved from source video."
            )

        # Resize to display dimensions if needed (to handle SAR)
        if self.needs_resize:
            frame = cv2.resize(
                frame,
                (self.display_width, self.display_height),
                interpolation=cv2.INTER_LANCZOS4,
            )

        self.writer.write(frame)

    def close(self) -> None:
        """Release video writer."""
        self.writer.release()

    def __enter__(self) -> "DebugOverlayRenderer":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore[no-untyped-def]
        self.close()
