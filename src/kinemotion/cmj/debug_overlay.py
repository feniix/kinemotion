"""Debug overlay rendering for CMJ analysis."""

import cv2
import numpy as np

from ..core.debug_overlay_utils import BaseDebugOverlayRenderer
from .joint_angles import calculate_triple_extension
from .kinematics import CMJMetrics


class CMJPhaseState:
    """States for CMJ phases."""

    STANDING = "standing"
    ECCENTRIC = "eccentric"
    TRANSITION = "transition"
    CONCENTRIC = "concentric"
    FLIGHT = "flight"
    LANDING = "landing"


class CMJDebugOverlayRenderer(BaseDebugOverlayRenderer):
    """Renders debug information on CMJ video frames."""

    def _determine_phase(self, frame_idx: int, metrics: CMJMetrics) -> str:
        """Determine which phase the current frame is in."""
        if metrics.standing_start_frame and frame_idx < metrics.standing_start_frame:
            return CMJPhaseState.STANDING

        if frame_idx < metrics.lowest_point_frame:
            return CMJPhaseState.ECCENTRIC

        # Brief transition at lowest point (±2 frames)
        if abs(frame_idx - metrics.lowest_point_frame) < 2:
            return CMJPhaseState.TRANSITION

        if frame_idx < metrics.takeoff_frame:
            return CMJPhaseState.CONCENTRIC

        if frame_idx < metrics.landing_frame:
            return CMJPhaseState.FLIGHT

        return CMJPhaseState.LANDING

    def _get_phase_color(self, phase: str) -> tuple[int, int, int]:
        """Get color for each phase."""
        colors = {
            CMJPhaseState.STANDING: (255, 200, 100),  # Light blue
            CMJPhaseState.ECCENTRIC: (0, 165, 255),  # Orange
            CMJPhaseState.TRANSITION: (255, 0, 255),  # Magenta/Purple
            CMJPhaseState.CONCENTRIC: (0, 255, 0),  # Green
            CMJPhaseState.FLIGHT: (0, 0, 255),  # Red
            CMJPhaseState.LANDING: (255, 255, 255),  # White
        }
        return colors.get(phase, (128, 128, 128))

    def _get_skeleton_segments(
        self, side_prefix: str
    ) -> list[tuple[str, str, tuple[int, int, int], int]]:
        """Get skeleton segments for one side of the body."""
        return [
            (f"{side_prefix}heel", f"{side_prefix}ankle", (0, 255, 255), 3),  # Foot
            (
                f"{side_prefix}heel",
                f"{side_prefix}foot_index",
                (0, 255, 255),
                2,
            ),  # Alt foot
            (f"{side_prefix}ankle", f"{side_prefix}knee", (255, 100, 100), 4),  # Shin
            (f"{side_prefix}knee", f"{side_prefix}hip", (100, 255, 100), 4),  # Femur
            (
                f"{side_prefix}hip",
                f"{side_prefix}shoulder",
                (100, 100, 255),
                4,
            ),  # Trunk
            (f"{side_prefix}shoulder", "nose", (150, 150, 255), 2),  # Neck
        ]

    def _draw_segment(
        self,
        frame: np.ndarray,
        landmarks: dict[str, tuple[float, float, float]],
        start_key: str,
        end_key: str,
        color: tuple[int, int, int],
        thickness: int,
    ) -> None:
        """Draw a single skeleton segment if both endpoints are visible."""
        if start_key not in landmarks or end_key not in landmarks:
            return

        start_vis = landmarks[start_key][2]
        end_vis = landmarks[end_key][2]

        # Very low threshold to show as much as possible
        if start_vis > 0.2 and end_vis > 0.2:
            start_x = int(landmarks[start_key][0] * self.width)
            start_y = int(landmarks[start_key][1] * self.height)
            end_x = int(landmarks[end_key][0] * self.width)
            end_y = int(landmarks[end_key][1] * self.height)

            cv2.line(frame, (start_x, start_y), (end_x, end_y), color, thickness)

    def _draw_joints(
        self,
        frame: np.ndarray,
        landmarks: dict[str, tuple[float, float, float]],
        side_prefix: str,
    ) -> None:
        """Draw joint circles for one side of the body."""
        joint_keys = [
            f"{side_prefix}heel",
            f"{side_prefix}foot_index",
            f"{side_prefix}ankle",
            f"{side_prefix}knee",
            f"{side_prefix}hip",
            f"{side_prefix}shoulder",
        ]
        for key in joint_keys:
            if key in landmarks and landmarks[key][2] > 0.2:
                jx = int(landmarks[key][0] * self.width)
                jy = int(landmarks[key][1] * self.height)
                cv2.circle(frame, (jx, jy), 6, (255, 255, 255), -1)
                cv2.circle(frame, (jx, jy), 8, (0, 0, 0), 2)

    def _draw_skeleton(
        self, frame: np.ndarray, landmarks: dict[str, tuple[float, float, float]]
    ) -> None:
        """Draw skeleton segments showing body landmarks.

        Draws whatever landmarks are visible. In side-view videos, ankle/knee
        may have low visibility, so we draw available segments.

        Args:
            frame: Frame to draw on (modified in place)
            landmarks: Pose landmarks
        """
        # Try both sides and draw all visible segments
        for side_prefix in ["right_", "left_"]:
            segments = self._get_skeleton_segments(side_prefix)

            # Draw ALL visible segments (not just one side)
            for start_key, end_key, color, thickness in segments:
                self._draw_segment(frame, landmarks, start_key, end_key, color, thickness)

            # Draw joints as circles for this side
            self._draw_joints(frame, landmarks, side_prefix)

        # Always draw nose (head position) if visible
        if "nose" in landmarks and landmarks["nose"][2] > 0.2:
            nx = int(landmarks["nose"][0] * self.width)
            ny = int(landmarks["nose"][1] * self.height)
            cv2.circle(frame, (nx, ny), 8, (255, 255, 0), -1)
            cv2.circle(frame, (nx, ny), 10, (0, 0, 0), 2)

    def _draw_joint_angles(
        self,
        frame: np.ndarray,
        landmarks: dict[str, tuple[float, float, float]],
        phase_color: tuple[int, int, int],
    ) -> None:
        """Draw joint angles for triple extension analysis.

        Args:
            frame: Frame to draw on (modified in place)
            landmarks: Pose landmarks
            phase_color: Current phase color
        """
        # Try right side first, fallback to left
        angles = calculate_triple_extension(landmarks, side="right")
        side_used = "right"

        if angles is None:
            angles = calculate_triple_extension(landmarks, side="left")
            side_used = "left"

        if angles is None:
            return

        # Position for angle text display (right side of frame)
        text_x = self.width - 180
        text_y = 100

        # Draw background box for angles
        box_height = 150
        cv2.rectangle(
            frame,
            (text_x - 10, text_y - 30),
            (self.width - 10, text_y + box_height),
            (0, 0, 0),
            -1,
        )
        cv2.rectangle(
            frame,
            (text_x - 10, text_y - 30),
            (self.width - 10, text_y + box_height),
            phase_color,
            2,
        )

        # Title
        cv2.putText(
            frame,
            "TRIPLE EXTENSION",
            (text_x, text_y - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            1,
        )

        # Draw available angles (show "N/A" for unavailable)
        angle_data = [
            ("Ankle", angles.get("ankle_angle"), (0, 255, 255)),
            ("Knee", angles.get("knee_angle"), (255, 100, 100)),
            ("Hip", angles.get("hip_angle"), (100, 255, 100)),
            ("Trunk", angles.get("trunk_tilt"), (100, 100, 255)),
        ]

        y_offset = text_y + 25
        for label, angle, color in angle_data:
            # Angle text
            if angle is not None:
                angle_text = f"{label}: {angle:.0f}"
                text_color = color
            else:
                angle_text = f"{label}: N/A"
                text_color = (128, 128, 128)  # Gray for unavailable

            cv2.putText(
                frame,
                angle_text,
                (text_x, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                text_color,
                2,
            )
            y_offset += 30

        # Draw angle arcs at joints for visual feedback (only if angle is available)
        ankle_angle = angles.get("ankle_angle")
        if ankle_angle is not None:
            self._draw_angle_arc(frame, landmarks, f"{side_used}_ankle", ankle_angle)
        knee_angle = angles.get("knee_angle")
        if knee_angle is not None:
            self._draw_angle_arc(frame, landmarks, f"{side_used}_knee", knee_angle)
        hip_angle = angles.get("hip_angle")
        if hip_angle is not None:
            self._draw_angle_arc(frame, landmarks, f"{side_used}_hip", hip_angle)

    def _draw_angle_arc(
        self,
        frame: np.ndarray,
        landmarks: dict[str, tuple[float, float, float]],
        joint_key: str,
        angle: float,
    ) -> None:
        """Draw a small arc at a joint to visualize the angle.

        Args:
            frame: Frame to draw on (modified in place)
            landmarks: Pose landmarks
            joint_key: Key of the joint landmark
            angle: Angle value in degrees
        """
        if joint_key not in landmarks or landmarks[joint_key][2] < 0.3:
            return

        jx = int(landmarks[joint_key][0] * self.width)
        jy = int(landmarks[joint_key][1] * self.height)

        # Draw arc radius based on angle (smaller arc for more extended joints)
        radius = 25

        # Color based on extension: green for extended (>160°), red for flexed (<90°)
        if angle > 160:
            arc_color = (0, 255, 0)  # Green - good extension
        elif angle < 90:
            arc_color = (0, 0, 255)  # Red - deep flexion
        else:
            arc_color = (0, 165, 255)  # Orange - moderate

        # Draw arc (simplified as a circle for now)
        cv2.circle(frame, (jx, jy), radius, arc_color, 2)

    def _draw_foot_landmarks(
        self,
        frame: np.ndarray,
        landmarks: dict[str, tuple[float, float, float]],
        phase_color: tuple[int, int, int],
    ) -> None:
        """Draw foot landmarks and average position."""
        foot_keys = ["left_ankle", "right_ankle", "left_heel", "right_heel"]
        foot_positions = []

        for key in foot_keys:
            if key in landmarks:
                x, y, vis = landmarks[key]
                if vis > 0.5:
                    lx = int(x * self.width)
                    ly = int(y * self.height)
                    foot_positions.append((lx, ly))
                    cv2.circle(frame, (lx, ly), 5, (255, 255, 0), -1)

        # Draw average foot position with phase color
        if foot_positions:
            avg_x = int(np.mean([p[0] for p in foot_positions]))
            avg_y = int(np.mean([p[1] for p in foot_positions]))
            cv2.circle(frame, (avg_x, avg_y), 12, phase_color, -1)
            cv2.circle(frame, (avg_x, avg_y), 14, (255, 255, 255), 2)

    def _draw_phase_banner(
        self, frame: np.ndarray, phase: str | None, phase_color: tuple[int, int, int]
    ) -> None:
        """Draw phase indicator banner."""
        if not phase:
            return

        phase_text = f"Phase: {phase.upper()}"
        text_size = cv2.getTextSize(phase_text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
        cv2.rectangle(frame, (5, 5), (text_size[0] + 15, 45), phase_color, -1)
        cv2.putText(frame, phase_text, (10, 35), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

    def _draw_key_frame_markers(
        self, frame: np.ndarray, frame_idx: int, metrics: CMJMetrics
    ) -> None:
        """Draw markers for key frames (standing start, lowest, takeoff, landing)."""
        y_offset = 120
        markers = []

        if metrics.standing_start_frame and frame_idx == int(metrics.standing_start_frame):
            markers.append("COUNTERMOVEMENT START")

        if frame_idx == int(metrics.lowest_point_frame):
            markers.append("LOWEST POINT")

        if frame_idx == int(metrics.takeoff_frame):
            markers.append("TAKEOFF")

        if frame_idx == int(metrics.landing_frame):
            markers.append("LANDING")

        for marker in markers:
            cv2.putText(
                frame,
                marker,
                (10, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 0),
                2,
            )
            y_offset += 35

    def _draw_metrics_summary(
        self, frame: np.ndarray, frame_idx: int, metrics: CMJMetrics
    ) -> None:
        """Draw metrics summary in bottom right (last 30 frames)."""
        total_frames = int(metrics.landing_frame) + 30
        if frame_idx < total_frames - 30:
            return

        metrics_text = [
            f"Jump Height: {metrics.jump_height:.3f}m",
            f"Flight Time: {metrics.flight_time * 1000:.0f}ms",
            f"CM Depth: {metrics.countermovement_depth:.3f}m",
            f"Ecc Duration: {metrics.eccentric_duration * 1000:.0f}ms",
            f"Con Duration: {metrics.concentric_duration * 1000:.0f}ms",
        ]

        # Draw background
        box_height = len(metrics_text) * 30 + 20
        cv2.rectangle(
            frame,
            (self.width - 320, self.height - box_height - 10),
            (self.width - 10, self.height - 10),
            (0, 0, 0),
            -1,
        )
        cv2.rectangle(
            frame,
            (self.width - 320, self.height - box_height - 10),
            (self.width - 10, self.height - 10),
            (0, 255, 0),
            2,
        )

        # Draw metrics text
        text_y = self.height - box_height + 10
        for text in metrics_text:
            cv2.putText(
                frame,
                text,
                (self.width - 310, text_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                1,
            )
            text_y += 30

    def render_frame(
        self,
        frame: np.ndarray,
        landmarks: dict[str, tuple[float, float, float]] | None,
        frame_idx: int,
        metrics: CMJMetrics | None = None,
    ) -> np.ndarray:
        """
        Render debug overlay on frame.

        Args:
            frame: Original video frame
            landmarks: Pose landmarks for this frame
            frame_idx: Current frame index
            metrics: CMJ metrics (optional)

        Returns:
            Frame with debug overlay
        """
        annotated = frame.copy()

        # Determine current phase if metrics available
        phase = None
        phase_color = (255, 255, 255)
        if metrics:
            phase = self._determine_phase(frame_idx, metrics)
            phase_color = self._get_phase_color(phase)

        # Draw skeleton and triple extension if landmarks available
        if landmarks:
            self._draw_skeleton(annotated, landmarks)
            self._draw_joint_angles(annotated, landmarks, phase_color)
            self._draw_foot_landmarks(annotated, landmarks, phase_color)

        # Draw phase indicator banner
        self._draw_phase_banner(annotated, phase, phase_color)

        # Draw frame number
        cv2.putText(
            annotated,
            f"Frame: {frame_idx}",
            (10, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )

        # Draw key frame markers and metrics summary
        if metrics:
            self._draw_key_frame_markers(annotated, frame_idx, metrics)
            self._draw_metrics_summary(annotated, frame_idx, metrics)

        return annotated
