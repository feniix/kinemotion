"""Debug overlay rendering for CMJ analysis."""

import cv2
import numpy as np

from ..core.debug_overlay_utils import BaseDebugOverlayRenderer
from ..core.overlay_constants import (
    ANGLE_ARC_RADIUS,
    ANKLE_COLOR,
    BLACK,
    CYAN,
    DEEP_FLEXION_ANGLE,
    FOOT_LANDMARK_RADIUS,
    FOOT_VISIBILITY_THRESHOLD,
    FULL_EXTENSION_ANGLE,
    GRAY,
    GREEN,
    HIP_COLOR,
    JOINT_ANGLES_BOX_HEIGHT,
    JOINT_ANGLES_BOX_X_OFFSET,
    JOINT_CIRCLE_RADIUS,
    JOINT_OUTLINE_RADIUS,
    KNEE_COLOR,
    METRICS_BOX_WIDTH,
    NOSE_CIRCLE_RADIUS,
    NOSE_OUTLINE_RADIUS,
    ORANGE,
    RED,
    TRUNK_COLOR,
    VISIBILITY_THRESHOLD,
    VISIBILITY_THRESHOLD_HIGH,
    WHITE,
    Color,
    Landmark,
    LandmarkDict,
)
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

    # Phase colors (BGR format)
    PHASE_COLORS: dict[str, Color] = {
        CMJPhaseState.STANDING: (255, 200, 100),  # Light blue
        CMJPhaseState.ECCENTRIC: (0, 165, 255),  # Orange
        CMJPhaseState.TRANSITION: (255, 0, 255),  # Magenta/Purple
        CMJPhaseState.CONCENTRIC: (0, 255, 0),  # Green
        CMJPhaseState.FLIGHT: (0, 0, 255),  # Red
        CMJPhaseState.LANDING: (255, 255, 255),  # White
    }
    DEFAULT_PHASE_COLOR: Color = GRAY

    def _determine_phase(self, frame_idx: int, metrics: CMJMetrics) -> str:
        """Determine which phase the current frame is in."""
        if metrics.standing_start_frame and frame_idx < metrics.standing_start_frame:
            return CMJPhaseState.STANDING

        if frame_idx < metrics.lowest_point_frame:
            return CMJPhaseState.ECCENTRIC

        # Brief transition at lowest point (within 2 frames)
        if abs(frame_idx - metrics.lowest_point_frame) < 2:
            return CMJPhaseState.TRANSITION

        if frame_idx < metrics.takeoff_frame:
            return CMJPhaseState.CONCENTRIC

        if frame_idx < metrics.landing_frame:
            return CMJPhaseState.FLIGHT

        return CMJPhaseState.LANDING

    def _get_phase_color(self, phase: str) -> Color:
        """Get color for each phase."""
        return self.PHASE_COLORS.get(phase, self.DEFAULT_PHASE_COLOR)

    def _get_skeleton_segments(self, side_prefix: str) -> list[tuple[str, str, Color, int]]:
        """Get skeleton segments for one side of the body.

        Returns list of (start_key, end_key, color, thickness) tuples.
        """
        p = side_prefix  # Shorter alias for readability
        return [
            (f"{p}heel", f"{p}ankle", ANKLE_COLOR, 3),  # Foot
            (f"{p}heel", f"{p}foot_index", ANKLE_COLOR, 2),  # Alt foot
            (f"{p}ankle", f"{p}knee", KNEE_COLOR, 4),  # Shin
            (f"{p}knee", f"{p}hip", HIP_COLOR, 4),  # Femur
            (f"{p}hip", f"{p}shoulder", TRUNK_COLOR, 4),  # Trunk
            (f"{p}shoulder", "nose", (150, 150, 255), 2),  # Neck
        ]

    def _landmark_to_pixel(self, landmark: Landmark) -> tuple[int, int]:
        """Convert normalized landmark coordinates to pixel coordinates."""
        return int(landmark[0] * self.width), int(landmark[1] * self.height)

    def _is_visible(self, landmark: Landmark, threshold: float = VISIBILITY_THRESHOLD) -> bool:
        """Check if a landmark has sufficient visibility."""
        return landmark[2] > threshold

    def _draw_segment(
        self,
        frame: np.ndarray,
        landmarks: LandmarkDict,
        start_key: str,
        end_key: str,
        color: Color,
        thickness: int,
    ) -> None:
        """Draw a single skeleton segment if both endpoints are visible."""
        if start_key not in landmarks or end_key not in landmarks:
            return

        start_landmark = landmarks[start_key]
        end_landmark = landmarks[end_key]

        if not (self._is_visible(start_landmark) and self._is_visible(end_landmark)):
            return

        start_pt = self._landmark_to_pixel(start_landmark)
        end_pt = self._landmark_to_pixel(end_landmark)
        cv2.line(frame, start_pt, end_pt, color, thickness)

    def _draw_joints(
        self,
        frame: np.ndarray,
        landmarks: LandmarkDict,
        side_prefix: str,
    ) -> None:
        """Draw joint circles for one side of the body."""
        p = side_prefix
        joint_keys = [
            f"{p}heel",
            f"{p}foot_index",
            f"{p}ankle",
            f"{p}knee",
            f"{p}hip",
            f"{p}shoulder",
        ]

        for key in joint_keys:
            if key not in landmarks:
                continue
            landmark = landmarks[key]
            if not self._is_visible(landmark):
                continue

            point = self._landmark_to_pixel(landmark)
            cv2.circle(frame, point, JOINT_CIRCLE_RADIUS, WHITE, -1)
            cv2.circle(frame, point, JOINT_OUTLINE_RADIUS, BLACK, 2)

    def _draw_skeleton(self, frame: np.ndarray, landmarks: LandmarkDict) -> None:
        """Draw skeleton segments showing body landmarks.

        Draws whatever landmarks are visible. In side-view videos, ankle/knee
        may have low visibility, so we draw available segments.

        Args:
            frame: Frame to draw on (modified in place)
            landmarks: Pose landmarks
        """
        # Draw segments and joints for both sides
        for side_prefix in ["right_", "left_"]:
            for start_key, end_key, color, thickness in self._get_skeleton_segments(side_prefix):
                self._draw_segment(frame, landmarks, start_key, end_key, color, thickness)
            self._draw_joints(frame, landmarks, side_prefix)

        # Draw nose (head position) if visible
        if "nose" in landmarks and self._is_visible(landmarks["nose"]):
            point = self._landmark_to_pixel(landmarks["nose"])
            cv2.circle(frame, point, NOSE_CIRCLE_RADIUS, CYAN, -1)
            cv2.circle(frame, point, NOSE_OUTLINE_RADIUS, BLACK, 2)

    def _get_triple_extension_angles(
        self, landmarks: LandmarkDict
    ) -> tuple[dict[str, float | None], str] | None:
        """Get triple extension angles, trying right side first then left.

        Returns tuple of (angles_dict, side_used) or None if unavailable.
        """
        for side in ["right", "left"]:
            angles = calculate_triple_extension(landmarks, side=side)
            if angles is not None:
                return angles, side
        return None

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

    def _draw_joint_angles(
        self, frame: np.ndarray, landmarks: LandmarkDict, phase_color: Color
    ) -> None:
        """Draw joint angles for triple extension analysis.

        Args:
            frame: Frame to draw on (modified in place)
            landmarks: Pose landmarks
            phase_color: Current phase color
        """
        result = self._get_triple_extension_angles(landmarks)
        if result is None:
            return

        angles, side_used = result

        # Position for angle text display (right side of frame)
        text_x = self.width - JOINT_ANGLES_BOX_X_OFFSET
        text_y = 100
        box_height = JOINT_ANGLES_BOX_HEIGHT

        # Draw background box
        self._draw_info_box(
            frame,
            (text_x - 10, text_y - 30),
            (self.width - 10, text_y + box_height),
            phase_color,
        )

        # Title
        cv2.putText(
            frame,
            "TRIPLE EXTENSION",
            (text_x, text_y - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            WHITE,
            1,
        )

        # Angle display configuration: (label, angle_key, color, joint_suffix)
        angle_config = [
            ("Ankle", "ankle_angle", ANKLE_COLOR, "ankle"),
            ("Knee", "knee_angle", KNEE_COLOR, "knee"),
            ("Hip", "hip_angle", HIP_COLOR, "hip"),
            ("Trunk", "trunk_tilt", TRUNK_COLOR, None),
        ]

        y_offset = text_y + 25
        for label, angle_key, color, joint_suffix in angle_config:
            angle = angles.get(angle_key)

            # Draw text
            if angle is not None:
                text = f"{label}: {angle:.0f}"
                text_color = color
            else:
                text = f"{label}: N/A"
                text_color = GRAY

            cv2.putText(
                frame, text, (text_x, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 2
            )
            y_offset += 30

            # Draw arc at joint if angle available and has associated joint
            if angle is not None and joint_suffix is not None:
                self._draw_angle_arc(frame, landmarks, f"{side_used}_{joint_suffix}", angle)

    def _get_extension_color(self, angle: float) -> Color:
        """Get color based on joint extension angle.

        Green for extended (>160 deg), red for flexed (<90 deg), orange for moderate.
        """
        if angle > FULL_EXTENSION_ANGLE:
            return GREEN
        if angle < DEEP_FLEXION_ANGLE:
            return RED
        return ORANGE

    def _draw_angle_arc(
        self, frame: np.ndarray, landmarks: LandmarkDict, joint_key: str, angle: float
    ) -> None:
        """Draw a circle at a joint to visualize the angle.

        Args:
            frame: Frame to draw on (modified in place)
            landmarks: Pose landmarks
            joint_key: Key of the joint landmark
            angle: Angle value in degrees
        """
        if joint_key not in landmarks:
            return
        landmark = landmarks[joint_key]
        if not self._is_visible(landmark, VISIBILITY_THRESHOLD_HIGH):
            return

        point = self._landmark_to_pixel(landmark)
        arc_color = self._get_extension_color(angle)
        cv2.circle(frame, point, ANGLE_ARC_RADIUS, arc_color, 2)

    def _draw_foot_landmarks(
        self, frame: np.ndarray, landmarks: LandmarkDict, phase_color: Color
    ) -> None:
        """Draw foot landmarks and average position."""
        foot_keys = ["left_ankle", "right_ankle", "left_heel", "right_heel"]
        foot_positions: list[tuple[int, int]] = []

        for key in foot_keys:
            if key not in landmarks:
                continue
            landmark = landmarks[key]
            if landmark[2] > FOOT_VISIBILITY_THRESHOLD:
                point = self._landmark_to_pixel(landmark)
                foot_positions.append(point)
                cv2.circle(frame, point, FOOT_LANDMARK_RADIUS, CYAN, -1)

        # Draw average foot position with phase color
        if foot_positions:
            avg_x = int(np.mean([p[0] for p in foot_positions]))
            avg_y = int(np.mean([p[1] for p in foot_positions]))
            cv2.circle(frame, (avg_x, avg_y), 12, phase_color, -1)
            cv2.circle(frame, (avg_x, avg_y), 14, WHITE, 2)

    def _draw_phase_banner(self, frame: np.ndarray, phase: str | None, phase_color: Color) -> None:
        """Draw phase indicator banner."""
        if not phase:
            return

        phase_text = f"Phase: {phase.upper()}"
        text_size = cv2.getTextSize(phase_text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
        cv2.rectangle(frame, (5, 5), (text_size[0] + 15, 45), phase_color, -1)
        cv2.putText(frame, phase_text, (10, 35), cv2.FONT_HERSHEY_SIMPLEX, 1, BLACK, 2)

    def _draw_key_frame_markers(
        self, frame: np.ndarray, frame_idx: int, metrics: CMJMetrics
    ) -> None:
        """Draw markers for key frames (standing start, lowest, takeoff, landing)."""
        # Key frame definitions: (frame_value, label)
        key_frames: list[tuple[float | None, str]] = [
            (metrics.standing_start_frame, "COUNTERMOVEMENT START"),
            (metrics.lowest_point_frame, "LOWEST POINT"),
            (metrics.takeoff_frame, "TAKEOFF"),
            (metrics.landing_frame, "LANDING"),
        ]

        y_offset = 120
        for key_frame, label in key_frames:
            if key_frame is not None and frame_idx == int(key_frame):
                cv2.putText(frame, label, (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.7, CYAN, 2)
                y_offset += 35

    def _draw_metrics_summary(
        self, frame: np.ndarray, frame_idx: int, metrics: CMJMetrics
    ) -> None:
        """Draw metrics summary in bottom right (last 30 frames after landing)."""
        if frame_idx < int(metrics.landing_frame):
            return

        metrics_text = [
            f"Jump Height: {metrics.jump_height:.3f}m",
            f"Flight Time: {metrics.flight_time * 1000:.0f}ms",
            f"CM Depth: {metrics.countermovement_depth:.3f}m",
            f"Ecc Duration: {metrics.eccentric_duration * 1000:.0f}ms",
            f"Con Duration: {metrics.concentric_duration * 1000:.0f}ms",
        ]

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
        frame_idx: int,
        metrics: CMJMetrics | None = None,
    ) -> np.ndarray:
        """Render debug overlay on frame.

        Args:
            frame: Original video frame
            landmarks: Pose landmarks for this frame
            frame_idx: Current frame index
            metrics: CMJ metrics (optional)

        Returns:
            Frame with debug overlay
        """
        annotated = frame.copy()

        # Determine current phase and color
        phase: str | None = None
        phase_color: Color = WHITE
        if metrics:
            phase = self._determine_phase(frame_idx, metrics)
            phase_color = self._get_phase_color(phase)

        # Draw skeleton and joint visualization if landmarks available
        if landmarks:
            self._draw_skeleton(annotated, landmarks)
            self._draw_joint_angles(annotated, landmarks, phase_color)
            self._draw_foot_landmarks(annotated, landmarks, phase_color)

        # Draw phase indicator and frame number
        self._draw_phase_banner(annotated, phase, phase_color)
        cv2.putText(
            annotated, f"Frame: {frame_idx}", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, WHITE, 2
        )

        # Draw key frame markers and metrics summary
        if metrics:
            self._draw_key_frame_markers(annotated, frame_idx, metrics)
            self._draw_metrics_summary(annotated, frame_idx, metrics)

        return annotated
