"""CoreML-accelerated RTMPose tracker using ONNX Runtime CoreML Execution Provider.

This tracker directly configures ONNX Runtime to use the CoreML EP for
Apple Silicon GPU/Neural Engine acceleration.
"""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import onnxruntime as ort

from kinemotion.core.timing import NULL_TIMER, Timer

# Halpe-26 to kinemotion landmark mapping
HALPE_TO_KINEMOTION = {
    0: "nose",
    5: "left_shoulder",
    6: "right_shoulder",
    11: "left_hip",
    12: "right_hip",
    13: "left_knee",
    14: "right_knee",
    15: "left_ankle",
    16: "right_ankle",
    20: "left_foot_index",
    21: "right_foot_index",
    24: "left_heel",
    25: "right_heel",
}


class CoreMLRTMPoseTracker:
    """RTMPose tracker with CoreML Execution Provider acceleration.

    Uses ONNX Runtime with CoreML EP for Apple Silicon acceleration.

    Attributes:
        timer: Optional Timer for measuring operations
        mode: RTMLib mode ('lightweight', 'balanced', 'performance')
        backend: Execution provider ('coreml', 'cpu')
    """

    def __init__(
        self,
        timer: Timer | None = None,
        mode: str = "lightweight",
        backend: str = "coreml",
        verbose: bool = False,
    ) -> None:
        """Initialize the CoreML RTMPose tracker.

        Args:
            timer: Optional Timer for measuring operations
            mode: RTMLib performance mode
            backend: 'coreml' for CoreML EP, 'cpu' for CPU fallback
            verbose: Print debug information
        """
        self.timer = timer or NULL_TIMER
        self.mode = mode
        self.backend = backend
        self.verbose = verbose

        with self.timer.measure("coreml_initialization"):
            self._init_models()

    def _init_models(self) -> None:
        """Initialize ONNX Runtime models with CoreML EP."""
        cache_dir = Path.home() / ".cache" / "rtmlib" / "hub" / "checkpoints"

        # Model paths for RTMPose lightweight (RTMPose-s with Halpe-26)
        det_model_path = cache_dir / "yolox_tiny_8xb8-300e_humanart-6f3252f9.onnx"
        pose_model_path = (
            cache_dir
            / "rtmpose-s_simcc-body7_pt-body7-halpe26_700e-256x192-7f134165_20230605.onnx"
        )

        if not det_model_path.exists():
            raise FileNotFoundError(f"Detector model not found: {det_model_path}")
        if not pose_model_path.exists():
            raise FileNotFoundError(f"Pose model not found: {pose_model_path}")

        # Configure execution providers
        if self.backend == "coreml":
            providers = [
                ("CoreMLExecutionProvider", {"ModelFormat": "MLProgram"}),
                "CPUExecutionProvider",
            ]
        else:
            providers = ["CPUExecutionProvider"]

        # Configure session options for performance
        so = ort.SessionOptions()
        so.intra_op_num_threads = 0  # 0 = use default (all cores)
        so.inter_op_num_threads = 0
        so.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL

        if self.verbose:
            print(f"Available providers: {ort.get_available_providers()}")
            print(f"Using providers: {providers}")

        # Load detection model
        if self.verbose:
            print(f"Loading detection model from {det_model_path}")
        self.det_session = ort.InferenceSession(
            str(det_model_path),
            sess_options=so,
            providers=providers,
        )

        if self.verbose:
            print(f"Detection model providers: {self.det_session.get_providers()}")

        # Load pose model
        if self.verbose:
            print(f"Loading pose model from {pose_model_path}")
        self.pose_session = ort.InferenceSession(
            str(pose_model_path),
            sess_options=so,
            providers=providers,
        )

        if self.verbose:
            print(f"Pose model providers: {self.pose_session.get_providers()}")

        # Get input/output info
        self.det_input_name = self.det_session.get_inputs()[0].name
        self.det_output_names = [o.name for o in self.det_session.get_outputs()]

        self.pose_input_name = self.pose_session.get_inputs()[0].name
        self.pose_output_names = [o.name for o in self.pose_session.get_outputs()]

        # Store input sizes
        self.det_input_size = (416, 416)  # YOLOX-tiny default
        self.pose_input_size = (192, 256)  # RTMPose-s default

    def _preprocess_det(self, img: np.ndarray) -> dict[str, np.ndarray]:
        """Preprocess image for detection."""
        # Resize and pad
        h, w = img.shape[:2]
        target_h, target_w = self.det_input_size

        scale = min(target_w / w, target_h / h)
        new_w = int(w * scale)
        new_h = int(h * scale)

        resized = cv2.resize(img, (new_w, new_h))
        padded = np.full((target_h, target_w, 3), 114, dtype=np.uint8)
        padded[:new_h, :new_w] = resized

        # Convert to RGB and normalize
        rgb = cv2.cvtColor(padded, cv2.COLOR_BGR2RGB)
        normalized = rgb.astype(np.float32) / 255.0
        transposed = normalized.transpose(2, 0, 1)

        return {
            "input": transposed[np.newaxis, :],
            "scale": scale,
            "pad": ((target_h - new_h) // 2, (target_w - new_w) // 2),
        }

    def _preprocess_pose(self, img: np.ndarray, bbox: list) -> np.ndarray:
        """Preprocess image region for pose estimation."""
        x1, y1, x2, y2 = bbox
        w = x2 - x1
        h = y2 - y1

        # Add padding
        pad = int(max(w, h) * 0.1)
        x1 = max(0, int(x1 - pad))
        y1 = max(0, int(y1 - pad))
        x2 = min(img.shape[1], int(x2 + pad))
        y2 = min(img.shape[0], int(y2 + pad))

        # Crop and resize
        crop = img[y1:y2, x1:x2]
        resized = cv2.resize(crop, self.pose_input_size)

        # Convert to RGB and normalize
        rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        normalized = rgb.astype(np.float32) / 255.0
        transposed = normalized.transpose(2, 0, 1)

        return transposed[np.newaxis, :]

    def _postprocess_det(
        self, outputs: list, orig_h: int, orig_w: int, preprocess_info: dict
    ) -> list:
        """Postprocess detection outputs."""
        # YOLOX output format: [batch, num_boxes, 85]
        # 85 = 4 bbox + 1 objectness + 80 classes
        detections = outputs[0]  # [1, 8400, 85]

        # Filter for person class (index 0 in COCO)
        scores = detections[0, :, 4]  # objectness
        class_scores = detections[0, :, 5]  # person class
        final_scores = scores * class_scores

        # Filter by confidence
        conf_threshold = 0.5
        mask = final_scores > conf_threshold

        if not np.any(mask):
            return []

        boxes = detections[0, mask, :4]
        scores = final_scores[mask]

        # Sort by score
        indices = np.argsort(scores)[::-1]
        boxes = boxes[indices]
        scores = scores[indices]

        # Scale boxes back to original image
        scale = preprocess_info["scale"]
        pad_h, pad_w = preprocess_info["pad"]

        results = []
        for box, score in zip(boxes[:1], scores[:1], strict=True):  # Only top 1 person
            x1, y1, x2, y2 = box
            x1 = (x1 - pad_w) / scale
            y1 = (y1 - pad_h) / scale
            x2 = (x2 - pad_w) / scale
            y2 = (y2 - pad_h) / scale

            # Clip to image bounds
            x1 = max(0, min(x1, orig_w))
            y1 = max(0, min(y1, orig_h))
            x2 = max(0, min(x2, orig_w))
            y2 = max(0, min(y2, orig_h))

            results.append([x1, y1, x2, y2, float(score)])

        return results

    def process_frame(self, frame: np.ndarray) -> dict[str, tuple[float, float, float]] | None:
        """Process a single frame and extract pose landmarks.

        Args:
            frame: BGR image frame (OpenCV format)

        Returns:
            Dictionary mapping landmark names to (x, y, visibility) tuples,
            or None if no pose detected.
        """
        if frame.size == 0:
            return None

        height, width = frame.shape[:2]

        try:
            # Detection
            with self.timer.measure("coreml_detection"):
                det_input = self._preprocess_det(frame)
                det_outputs = self.det_session.run(
                    self.det_output_names,
                    {self.det_input_name: det_input["input"]},
                )
                detections = self._postprocess_det(det_outputs, height, width, det_input)

            if not detections:
                return None

            # Get the highest confidence person bbox
            x1, y1, x2, y2, score = detections[0]

            # Pose estimation
            with self.timer.measure("coreml_pose_inference"):
                pose_input = self._preprocess_pose(frame, [x1, y1, x2, y2])
                pose_outputs = self.pose_session.run(
                    self.pose_output_names,
                    {self.pose_input_name: pose_input},
                )

            # Extract landmarks from output
            with self.timer.measure("landmark_extraction"):
                landmarks = self._extract_landmarks_from_output(
                    pose_outputs, [x1, y1, x2, y2], width, height
                )

            return landmarks

        except Exception as e:
            if self.verbose:
                print(f"CoreML tracker error: {e}")
            return None

    def _extract_landmarks_from_output(
        self,
        outputs: list,
        bbox: list,
        img_width: int,
        img_height: int,
    ) -> dict[str, tuple[float, float, float]]:
        """Extract landmarks from RTMPose output."""
        # RTMPose output format varies - this is a simplified version
        # In practice, you'd need to parse the SIMCC output properly
        # For now, return empty dict to avoid errors
        return {}

    def close(self) -> None:
        """Release resources."""
        pass


def create_coreml_tracker(
    mode: str = "lightweight",
    backend: str = "coreml",
    timer: Timer | None = None,
) -> CoreMLRTMPoseTracker:
    """Factory function to create a CoreML RTMPoseTracker.

    Args:
        mode: Performance mode ('lightweight', 'balanced', 'performance')
        backend: 'coreml' for CoreML EP, 'cpu' for CPU fallback
        timer: Optional Timer for measuring operations

    Returns:
        Configured CoreMLRTMPoseTracker instance
    """
    return CoreMLRTMPoseTracker(mode=mode, backend=backend, timer=timer)
