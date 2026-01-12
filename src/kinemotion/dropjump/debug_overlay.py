"""Debug overlay rendering for drop jump analysis."""

import cv2
import numpy as np

from ..core.debug_overlay_utils import BaseDebugOverlayRenderer
from ..core.overlay_constants import (
    BLACK,
    COM_CIRCLE_RADIUS,
    COM_OUTLINE_RADIUS,
    CYAN,
    FOOT_CIRCLE_RADIUS,
    FOOT_LANDMARK_RADIUS,
    FOOT_VISIBILITY_THRESHOLD,
    GREEN,
    HIP_MARKER_RADIUS,
    METRICS_BOX_WIDTH,
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


class DropJumpDebugOverlayRenderer(BaseDebugOverlayRenderer):
    """Renders debug information on video frames."""

    def _get_contact_state_color(self, contact_state: ContactState) -> Color:
        """Get color based on ground contact state."""
        return GREEN if contact_state == ContactState.ON_GROUND else RED

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
        # Phase configurations: (start_frame, end_frame, label, color)
        # For range-based phases (ground contact, flight)
        range_phase_configs = [
            (metrics.contact_start_frame, metrics.contact_end_frame, "GROUND CONTACT", GREEN),
            (metrics.flight_start_frame, metrics.flight_end_frame, "FLIGHT PHASE", RED),
        ]

        y_offset = PHASE_LABEL_START_Y
        for start_frame, end_frame, label, color in range_phase_configs:
            if start_frame and end_frame and start_frame <= frame_idx <= end_frame:
                cv2.putText(
                    frame,
                    label,
                    (10, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    color,
                    2,
                )
                y_offset += PHASE_LABEL_LINE_HEIGHT

        # Single-frame indicator (peak height)
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

    def _draw_info_box(
        self,
        frame: np.ndarray,
        top_left: tuple[int, int],
        bottom_right: tuple[int, int],
        border_color: Color,
    ) -> None:
        """Draw a filled box with border for displaying information."""
        cv2.rectangle(frame, top_left, bottom_right, BLACK, -1)
        cv2.rectangle(frame, top_left, bottom_right, border_color, 2)

    def _draw_metrics_summary(
        self, frame: np.ndarray, frame_idx: int, metrics: DropJumpMetrics
    ) -> None:
        """Draw metrics summary in bottom right after flight phase ends."""
        if metrics.flight_end_frame is None or frame_idx < metrics.flight_end_frame:
            return

        # Build metrics text list
        metrics_text: list[str] = []

        if metrics.ground_contact_time is not None:
            metrics_text.append(f"Contact Time: {metrics.ground_contact_time * 1000:.0f}ms")

        if metrics.flight_time is not None:
            metrics_text.append(f"Flight Time: {metrics.flight_time * 1000:.0f}ms")

        if metrics.jump_height is not None:
            metrics_text.append(f"Jump Height: {metrics.jump_height:.3f}m")

        # Calculate RSI (Reactive Strength Index)
        if (
            metrics.jump_height is not None
            and metrics.ground_contact_time is not None
            and metrics.ground_contact_time > 0
        ):
            rsi = metrics.jump_height / metrics.ground_contact_time
            metrics_text.append(f"RSI: {rsi:.2f}")

        if not metrics_text:
            return

        # Calculate box dimensions
        box_height = len(metrics_text) * 30 + 20
        top_left = (self.width - METRICS_BOX_WIDTH, self.height - box_height - 10)
        bottom_right = (self.width - 10, self.height - 10)

        self._draw_info_box(frame, top_left, bottom_right, GREEN)

        # Draw metrics text
        text_x = self.width - METRICS_BOX_WIDTH + 10
        text_y = self.height - box_height + 10
        for text in metrics_text:
            cv2.putText(frame, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, WHITE, 1)
            text_y += 30

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
            # Draw skeleton and landmarks
            if landmarks:
                self._draw_skeleton(annotated, landmarks)
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

            # Draw phase labels and metrics summary
            if metrics:
                self._draw_phase_labels(annotated, frame_idx, metrics)
                self._draw_metrics_summary(annotated, frame_idx, metrics)

        return annotated
