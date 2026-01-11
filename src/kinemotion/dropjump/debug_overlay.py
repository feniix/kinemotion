"""Debug overlay rendering for drop jump analysis."""

import cv2
import numpy as np

from ..core.debug_overlay_utils import BaseDebugOverlayRenderer
from ..core.overlay_constants import (
    COM_CIRCLE_RADIUS,
    COM_OUTLINE_RADIUS,
    CYAN,
    FOOT_CIRCLE_RADIUS,
    FOOT_LANDMARK_RADIUS,
    FOOT_VISIBILITY_THRESHOLD,
    GREEN,
    HIP_MARKER_RADIUS,
    ORANGE,
    PHASE_LABEL_LINE_HEIGHT,
    PHASE_LABEL_START_Y,
    RED,
    WHITE,
    Color,
    LandmarkDict,
)
from ..core.pose import compute_center_of_mass
from .analysis import ContactState, compute_average_foot_position
from .kinematics import DropJumpMetrics


class DebugOverlayRenderer(BaseDebugOverlayRenderer):
    """Renders debug information on video frames."""

    def _get_contact_state_color(self, contact_state: ContactState) -> Color:
        """Get color based on ground contact state."""
        return GREEN if contact_state == ContactState.ON_GROUND else RED

    def _normalize_to_pixels(self, x: float, y: float) -> tuple[int, int]:
        """Convert normalized coordinates to pixel coordinates."""
        return int(x * self.width), int(y * self.height)

    def _draw_com_visualization(
        self,
        frame: np.ndarray,
        landmarks: LandmarkDict,
        contact_state: ContactState,
    ) -> None:
        """Draw center of mass visualization on frame."""
        com_x, com_y, _ = compute_center_of_mass(landmarks)
        px, py = self._normalize_to_pixels(com_x, com_y)

        color = self._get_contact_state_color(contact_state)
        cv2.circle(frame, (px, py), COM_CIRCLE_RADIUS, color, -1)
        cv2.circle(frame, (px, py), COM_OUTLINE_RADIUS, WHITE, 2)

        # Draw hip midpoint reference
        if "left_hip" in landmarks and "right_hip" in landmarks:
            lh_x, lh_y, _ = landmarks["left_hip"]
            rh_x, rh_y, _ = landmarks["right_hip"]
            hip_x, hip_y = self._normalize_to_pixels((lh_x + rh_x) / 2, (lh_y + rh_y) / 2)
            cv2.circle(frame, (hip_x, hip_y), HIP_MARKER_RADIUS, ORANGE, -1)
            cv2.line(frame, (hip_x, hip_y), (px, py), ORANGE, 2)

    def _draw_foot_visualization(
        self,
        frame: np.ndarray,
        landmarks: LandmarkDict,
        contact_state: ContactState,
    ) -> None:
        """Draw foot position visualization on frame."""
        foot_x, foot_y = compute_average_foot_position(landmarks)
        px, py = self._normalize_to_pixels(foot_x, foot_y)

        color = self._get_contact_state_color(contact_state)
        cv2.circle(frame, (px, py), FOOT_CIRCLE_RADIUS, color, -1)

        # Draw individual foot landmarks
        foot_keys = ["left_ankle", "right_ankle", "left_heel", "right_heel"]
        for key in foot_keys:
            if key in landmarks:
                x, y, vis = landmarks[key]
                if vis > FOOT_VISIBILITY_THRESHOLD:
                    lx, ly = self._normalize_to_pixels(x, y)
                    cv2.circle(frame, (lx, ly), FOOT_LANDMARK_RADIUS, CYAN, -1)

    def _draw_phase_labels(
        self,
        frame: np.ndarray,
        frame_idx: int,
        metrics: DropJumpMetrics,
    ) -> None:
        """Draw phase labels (ground contact, flight, peak) on frame."""
        y_offset = PHASE_LABEL_START_Y

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
                GREEN,
                2,
            )
            y_offset += PHASE_LABEL_LINE_HEIGHT

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
                RED,
                2,
            )
            y_offset += PHASE_LABEL_LINE_HEIGHT

        # Peak height
        if metrics.peak_height_frame == frame_idx:
            cv2.putText(
                frame,
                "PEAK HEIGHT",
                (10, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 0, 255),  # Magenta
                2,
            )

    def render_frame(
        self,
        frame: np.ndarray,
        landmarks: LandmarkDict | None,
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

        with self.timer.measure("debug_video_draw"):
            # Draw landmarks
            if landmarks:
                if use_com:
                    self._draw_com_visualization(annotated, landmarks, contact_state)
                else:
                    self._draw_foot_visualization(annotated, landmarks, contact_state)

            # Draw contact state
            state_color = self._get_contact_state_color(contact_state)
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
                WHITE,
                2,
            )

            # Draw phase labels
            if metrics:
                self._draw_phase_labels(annotated, frame_idx, metrics)

        return annotated
