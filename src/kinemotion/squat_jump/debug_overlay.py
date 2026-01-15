"""Debug overlay visualization for Squat Jump analysis."""

import cv2
import numpy as np

from ..core.debug_overlay_utils import BaseDebugOverlayRenderer
from ..core.overlay_constants import (
    CYAN,
    GREEN,
    PHASE_LABEL_LINE_HEIGHT,
    PHASE_LABEL_START_Y,
    RED,
    WHITE,
    Color,
    LandmarkDict,
)
from .analysis import SJPhase
from .kinematics import SJMetrics


class SquatJumpDebugOverlayRenderer(BaseDebugOverlayRenderer):
    """Debug overlay renderer for Squat Jump analysis results."""

    def _get_phase_color(self, phase: SJPhase) -> Color:
        """Get color based on jump phase."""
        phase_colors = {
            SJPhase.SQUAT_HOLD: (255, 255, 0),  # Yellow
            SJPhase.CONCENTRIC: (0, 165, 255),  # Orange
            SJPhase.FLIGHT: RED,
            SJPhase.LANDING: GREEN,
            SJPhase.UNKNOWN: WHITE,
        }
        return phase_colors.get(phase, WHITE)

    def render_frame(
        self,
        frame: np.ndarray,
        landmarks: LandmarkDict | None,
        frame_index: int,
        metrics: SJMetrics | None = None,
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

        # Determine current phase
        current_phase = SJPhase.UNKNOWN
        if metrics:
            if (
                metrics.squat_hold_start_frame is not None
                and metrics.concentric_start_frame is not None
                and metrics.squat_hold_start_frame <= frame_index < metrics.concentric_start_frame
            ):
                current_phase = SJPhase.SQUAT_HOLD
            elif (
                metrics.concentric_start_frame is not None
                and metrics.takeoff_frame is not None
                and metrics.concentric_start_frame <= frame_index < metrics.takeoff_frame
            ):
                current_phase = SJPhase.CONCENTRIC
            elif (
                metrics.takeoff_frame is not None
                and metrics.landing_frame is not None
                and metrics.takeoff_frame <= frame_index < metrics.landing_frame
            ):
                current_phase = SJPhase.FLIGHT
            elif (
                metrics.landing_frame is not None
                and metrics.landing_frame <= frame_index < metrics.landing_frame + 15
            ):
                current_phase = SJPhase.LANDING

        # Draw skeleton and landmarks
        if landmarks:
            self._draw_skeleton(annotated_frame, landmarks)

        # Draw frame information
        self._draw_frame_info(annotated_frame, frame_index, current_phase)

        # Draw metrics if available
        if metrics:
            self._draw_metrics(annotated_frame, metrics, frame_index)

        return annotated_frame

    def _draw_frame_info(self, frame: np.ndarray, frame_index: int, phase: SJPhase) -> None:
        """Draw frame information overlay.

        Args:
            frame: Frame to draw on
            frame_index: Current frame index
            phase: Current jump phase
        """
        # Draw frame counter
        cv2.putText(
            frame,
            f"Frame: {frame_index}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            WHITE,
            2,
            cv2.LINE_AA,
        )

        # Draw phase label
        phase_color = self._get_phase_color(phase)
        cv2.putText(
            frame,
            f"Phase: {phase.value.replace('_', ' ').upper()}",
            (10, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            phase_color,
            2,
            cv2.LINE_AA,
        )

    def _draw_metrics(self, frame: np.ndarray, metrics: SJMetrics, frame_index: int) -> None:
        """Draw metrics information on frame.

        Args:
            frame: Frame to draw on
            metrics: Metrics object with analysis results
            frame_index: Current frame index
        """
        # Only show summary metrics after takeoff or at the end
        if metrics.takeoff_frame is None or frame_index < metrics.takeoff_frame:
            return

        y_offset = PHASE_LABEL_START_Y + 100

        # Display key metrics
        metric_items: list[tuple[str, Color]] = [
            (f"Jump Height: {metrics.jump_height:.3f} m", WHITE),
            (f"Flight Time: {metrics.flight_time * 1000:.1f} ms", RED),
            (f"Concentric: {metrics.concentric_duration * 1000:.1f} ms", CYAN),
        ]
        if metrics.peak_power is not None:
            metric_items.append((f"Peak Power: {metrics.peak_power:.0f} W", GREEN))

        for text, color in metric_items:
            cv2.putText(
                frame,
                text,
                (10, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                color,
                2,
                cv2.LINE_AA,
            )
            y_offset += PHASE_LABEL_LINE_HEIGHT
