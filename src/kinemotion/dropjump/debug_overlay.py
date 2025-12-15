"""Debug overlay rendering for drop jump analysis."""

import cv2
import numpy as np

from ..core.debug_overlay_utils import BaseDebugOverlayRenderer
from ..core.pose import compute_center_of_mass
from .analysis import ContactState, compute_average_foot_position
from .kinematics import DropJumpMetrics


class DebugOverlayRenderer(BaseDebugOverlayRenderer):
    """Renders debug information on video frames."""

    def _draw_com_visualization(
        self,
        frame: np.ndarray,
        landmarks: dict[str, tuple[float, float, float]],
        contact_state: ContactState,
    ) -> None:
        """Draw center of mass visualization on frame."""
        com_x, com_y, _ = compute_center_of_mass(landmarks)
        px = int(com_x * self.width)
        py = int(com_y * self.height)

        color = (0, 255, 0) if contact_state == ContactState.ON_GROUND else (0, 0, 255)
        cv2.circle(frame, (px, py), 15, color, -1)
        cv2.circle(frame, (px, py), 17, (255, 255, 255), 2)

        # Draw hip midpoint reference
        if "left_hip" in landmarks and "right_hip" in landmarks:
            lh_x, lh_y, _ = landmarks["left_hip"]
            rh_x, rh_y, _ = landmarks["right_hip"]
            hip_x = int((lh_x + rh_x) / 2 * self.width)
            hip_y = int((lh_y + rh_y) / 2 * self.height)
            cv2.circle(frame, (hip_x, hip_y), 8, (255, 165, 0), -1)
            cv2.line(frame, (hip_x, hip_y), (px, py), (255, 165, 0), 2)

    def _draw_foot_visualization(
        self,
        frame: np.ndarray,
        landmarks: dict[str, tuple[float, float, float]],
        contact_state: ContactState,
    ) -> None:
        """Draw foot position visualization on frame."""
        foot_x, foot_y = compute_average_foot_position(landmarks)
        px = int(foot_x * self.width)
        py = int(foot_y * self.height)

        color = (0, 255, 0) if contact_state == ContactState.ON_GROUND else (0, 0, 255)
        cv2.circle(frame, (px, py), 10, color, -1)

        # Draw individual foot landmarks
        foot_keys = ["left_ankle", "right_ankle", "left_heel", "right_heel"]
        for key in foot_keys:
            if key in landmarks:
                x, y, vis = landmarks[key]
                if vis > 0.5:
                    lx = int(x * self.width)
                    ly = int(y * self.height)
                    cv2.circle(frame, (lx, ly), 5, (255, 255, 0), -1)

    def _draw_phase_labels(
        self,
        frame: np.ndarray,
        frame_idx: int,
        metrics: DropJumpMetrics,
    ) -> None:
        """Draw phase labels (ground contact, flight, peak) on frame."""
        y_offset = 110

        # Ground contact phase
        if (
            metrics.contact_start_frame
            and metrics.contact_end_frame
            and metrics.contact_start_frame <= frame_idx <= metrics.contact_end_frame
        ):
            cv2.putText(
                frame,
                "GROUND CONTACT",
                (10, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2,
            )
            y_offset += 40

        # Flight phase
        if (
            metrics.flight_start_frame
            and metrics.flight_end_frame
            and metrics.flight_start_frame <= frame_idx <= metrics.flight_end_frame
        ):
            cv2.putText(
                frame,
                "FLIGHT PHASE",
                (10, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 255),
                2,
            )
            y_offset += 40

        # Peak height
        if metrics.peak_height_frame == frame_idx:
            cv2.putText(
                frame,
                "PEAK HEIGHT",
                (10, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 0, 255),
                2,
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
        with self.timer.measure("debug_video_copy"):
            annotated = frame.copy()

        def _draw_overlays() -> None:
            # Draw landmarks
            if landmarks:
                if use_com:
                    self._draw_com_visualization(annotated, landmarks, contact_state)
                else:
                    self._draw_foot_visualization(annotated, landmarks, contact_state)

            # Draw contact state
            state_color = (0, 255, 0) if contact_state == ContactState.ON_GROUND else (0, 0, 255)
            cv2.putText(
                annotated,
                f"State: {contact_state.value}",
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

            # Draw phase labels
            if metrics:
                self._draw_phase_labels(annotated, frame_idx, metrics)

        with self.timer.measure("debug_video_draw"):
            _draw_overlays()

        return annotated
