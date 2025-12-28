"""Optimized CPU RTMPose tracker with ONNX Runtime performance tuning.

This tracker applies specific optimizations for AMD Ryzen CPUs:
- Tuned threading for Ryzen 7 7800X3D (8 cores/16 threads)
- Sequential execution mode for better cache locality
- Optional input size reduction for faster inference

Landmark accuracy: 9-12px mean difference from MediaPipe
- CMJ: 9.7px → 1-3% metric accuracy
- Drop Jump: 11.5px → 2-5% metric accuracy

Performance: 40-68 FPS (vs MediaPipe's 48 FPS)
"""

from __future__ import annotations

from collections.abc import Sequence
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


class OptimizedCPUTracker:
    """RTMPose tracker with CPU-optimized ONNX Runtime configuration.

    Optimized for AMD Ryzen 7 7800X3D with:
    - intra_op_num_threads=8 (physical cores)
    - inter_op_num_threads=1 (avoid oversubscription)
    - ORT_SEQUENTIAL execution mode
    - Optional reduced input size for faster inference

    Attributes:
        timer: Optional Timer for measuring operations
        mode: RTMLib mode ('lightweight', 'balanced', 'performance')
        input_size: Pose input size as (height, width) tuple
        intra_threads: Number of intra-op threads
        inter_threads: Number of inter-op threads
    """

    def __init__(
        self,
        timer: Timer | None = None,
        mode: str = "lightweight",
        input_size: tuple[int, int] = (192, 256),
        intra_threads: int = 8,
        inter_threads: int = 1,
        verbose: bool = False,
    ) -> None:
        """Initialize the optimized CPU tracker.

        Args:
            timer: Optional Timer for measuring operations
            mode: RTMLib performance mode
            input_size: Pose model input size as (height, width)
            intra_threads: Number of intra-op threads (default: 8 for Ryzen 7 7800X3D)
            inter_threads: Number of inter-op threads (default: 1 to avoid oversubscription)
            verbose: Print debug information
        """
        self.timer = timer or NULL_TIMER
        self.mode = mode
        self.input_size = input_size
        self.intra_threads = intra_threads
        self.inter_threads = inter_threads
        self.verbose = verbose

        with self.timer.measure("optimized_cpu_initialization"):
            self._init_models()

    def _init_models(self) -> None:
        """Initialize ONNX Runtime models with optimized CPU configuration."""
        from importlib.resources import files

        # Use bundled models from package
        models_dir = Path(files("kinemotion") / "models")  # type: ignore[arg-type]

        # Model paths for RTMPose lightweight (RTMPose-s with Halpe-26)
        det_model_path = models_dir / "yolox_tiny_8xb8-300e_humanart-6f3252f9.onnx"
        pose_model_path = (
            models_dir
            / "rtmpose-s_simcc-body7_pt-body7-halpe26_700e-256x192-7f134165_20230605.onnx"
        )

        if not det_model_path.exists():
            raise FileNotFoundError(
                f"Detector model not found: {det_model_path}\n"
                f"Please ensure RTMPose models are installed in {models_dir}"
            )
        if not pose_model_path.exists():
            raise FileNotFoundError(
                f"Pose model not found: {pose_model_path}\n"
                f"Please ensure RTMPose models are installed in {models_dir}"
            )

        # Configure execution providers - CPU only with optimizations
        providers = ["CPUExecutionProvider"]

        # Configure session options for optimal CPU performance
        so = ort.SessionOptions()
        so.intra_op_num_threads = self.intra_threads
        so.inter_op_num_threads = self.inter_threads
        so.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
        so.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        # Enable thread spinning for lower latency
        so.add_session_config_entry("session.intra_op.allow_spinning", "1")
        so.add_session_config_entry("session.inter_op.allow_spinning", "0")

        if self.verbose:
            print("Optimized CPU Configuration:")
            print(f"  intra_op_num_threads: {self.intra_threads}")
            print(f"  inter_op_num_threads: {self.inter_threads}")
            print("  execution_mode: ORT_SEQUENTIAL")
            print(f"  input_size: {self.input_size}")
            print(f"Available providers: {ort.get_available_providers()}")

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
        # Note: input_size is (height, width), but pose model expects (width, height)
        self.pose_input_size = (self.input_size[1], self.input_size[0])  # Swap to (width, height)

    def _preprocess_det(self, img: np.ndarray) -> dict:
        """Preprocess image for detection following rtmlib's YOLOX preprocessing.

        IMPORTANT: YOLOX expects float32 in [0, 255] range, NOT normalized to [0, 1]!

        Returns dict with 'input' (tensor) and 'ratio' (scale factor).
        """
        # Create padded image with 114 (YOLOX default padding color)
        h, w = img.shape[:2]
        target_h, target_w = self.det_input_size

        # Calculate ratio
        ratio = min(target_h / h, target_w / w)

        # Resize image
        resized = cv2.resize(
            img,
            (int(w * ratio), int(h * ratio)),
            interpolation=cv2.INTER_LINEAR,
        ).astype(np.uint8)

        # Create padded image
        padded = np.ones((target_h, target_w, 3), dtype=np.uint8) * 114
        padded[: resized.shape[0], : resized.shape[1]] = resized

        # Convert BGR to RGB (YOLOX expects RGB)
        rgb = cv2.cvtColor(padded, cv2.COLOR_BGR2RGB)

        # Convert to float32 in [0, 255] range - DO NOT NORMALIZE!
        # rtmlib: img = np.ascontiguousarray(img, dtype=np.float32)
        rgb_float = np.ascontiguousarray(rgb, dtype=np.float32)

        # Transpose to (3, H, W) and add batch dimension
        transposed = rgb_float.transpose(2, 0, 1)

        return {
            "input": transposed[np.newaxis, :],
            "ratio": ratio,
        }

    def _preprocess_pose(self, img: np.ndarray, bbox: list) -> np.ndarray:
        """Preprocess image region for pose estimation using RTMPose preprocessing.

        This follows RTMLib's preprocessing which uses affine transform and
        specific normalization (mean=[123.675, 116.28, 103.53], std=[58.395, 57.12, 57.375]).

        Args:
            img: Original BGR image
            bbox: Bounding box [x1, y1, x2, y2]

        Returns:
            Preprocessed image tensor ready for ONNX inference
        """
        # Convert bbox to numpy array
        bbox_array = np.array(bbox, dtype=np.float32)

        # Get center and scale using rtmlib's bbox_xyxy2cs logic
        # padding=1.25 is the default used by RTMPose
        x1, y1, x2, y2 = bbox_array
        center = np.array([x1 + x2, y1 + y2]) * 0.5
        scale = np.array([x2 - x1, y2 - y1]) * 1.25

        # Reshape bbox to fixed aspect ratio using rtmlib's logic
        model_h, model_w = self.pose_input_size
        aspect_ratio = model_w / model_h

        b_w = scale[0]
        b_h = scale[1]

        # Reshape to maintain aspect ratio
        if b_w > b_h * aspect_ratio:
            scale = np.array([b_w, b_w / aspect_ratio], dtype=np.float32)
        else:
            scale = np.array([b_h * aspect_ratio, b_h], dtype=np.float32)

        # Get affine transformation matrix
        warp_mat = self._get_warp_matrix(center, scale, 0, (model_w, model_h))

        # Do affine transform
        warped = cv2.warpAffine(img, warp_mat, (model_w, model_h), flags=cv2.INTER_LINEAR)

        # Normalize using RTMPose's mean and std
        mean = np.array([123.675, 116.28, 103.53], dtype=np.float32)
        std = np.array([58.395, 57.12, 57.375], dtype=np.float32)

        normalized = (warped - mean) / std

        # Convert to RGB and transpose to NCHW format
        rgb = cv2.cvtColor(normalized.astype(np.float32), cv2.COLOR_BGR2RGB)
        transposed = rgb.transpose(2, 0, 1)

        return transposed[np.newaxis, :]

    def _get_warp_matrix(
        self,
        center: np.ndarray,
        scale: np.ndarray,
        rot: float,
        output_size: tuple[int, int],
    ) -> np.ndarray:
        """Calculate the affine transformation matrix for pose preprocessing.

        This follows rtmlib's get_warp_matrix logic.

        Args:
            center: Center of the bounding box (x, y)
            scale: Scale of the bounding box [w, h]
            rot: Rotation angle (degrees) - usually 0
            output_size: Destination size (width, height)

        Returns:
            2x3 affine transformation matrix
        """
        import math

        dst_w, dst_h = output_size

        # Compute transformation matrix
        rot_rad = math.radians(rot)

        # Source direction vector (rotated)
        src_dir = self._rotate_point(np.array([0.0, scale[0] * -0.5]), rot_rad)
        dst_dir = np.array([0.0, dst_w * -0.5])

        # Get three corners of the src rectangle
        src: np.ndarray = np.zeros((3, 2), dtype=np.float32)
        src[0, :] = center
        src[1, :] = center + src_dir
        src[2, :] = self._get_3rd_point(src[0, :], src[1, :])

        # Get three corners of the dst rectangle
        dst: np.ndarray = np.zeros((3, 2), dtype=np.float32)
        dst[0, :] = [dst_w * 0.5, dst_h * 0.5]
        dst[1, :] = np.array([dst_w * 0.5, dst_h * 0.5]) + dst_dir
        dst[2, :] = self._get_3rd_point(dst[0, :], dst[1, :])

        # Get affine transform matrix
        warp_mat = cv2.getAffineTransform(src, dst)

        return warp_mat

    def _rotate_point(self, pt: np.ndarray, angle_rad: float) -> np.ndarray:
        """Rotate a point by an angle.

        Args:
            pt: 2D point coordinates (x, y)
            angle_rad: Rotation angle in radians

        Returns:
            Rotated point
        """
        import math

        sn, cs = math.sin(angle_rad), math.cos(angle_rad)
        rot_mat = np.array([[cs, -sn], [sn, cs]])
        return rot_mat @ pt

    def _get_3rd_point(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """Calculate the 3rd point for affine transform matrix.

        The 3rd point is defined by rotating vector a - b by 90 degrees
        anticlockwise, using b as the rotation center.

        Args:
            a: The 1st point (x, y)
            b: The 2nd point (x, y)

        Returns:
            The 3rd point
        """
        direction = a - b
        c = b + np.array([-direction[1], direction[0]])
        return c

    def _postprocess_det(
        self,
        outputs: tuple[np.ndarray, ...] | Sequence[np.ndarray],
        orig_h: int,
        orig_w: int,
        preprocess_info: dict,
    ) -> list:
        """Postprocess detection outputs.

        YOLOX ONNX model has NMS built-in, output shape is (1, N, 5) where:
        - 5 values: [x1, y1, x2, y2, score]
        - N is the number of detections after NMS
        """
        detections = outputs[0]  # (1, N, 5)

        if self.verbose:
            print(f"DEBUG: detections shape: {detections.shape}")
            print(f"DEBUG: detections[0]: {detections[0]}")

        # Extract boxes and scores
        # detections[0] because we have batch dimension
        boxes = detections[0, :, :4]  # (N, 4)
        scores = detections[0, :, 4]  # (N,)

        # Filter by confidence
        conf_threshold = 0.3

        if self.verbose:
            print(f"DEBUG: scores before filter: {scores}")
            print(f"DEBUG: conf_threshold: {conf_threshold}")

        mask = scores > conf_threshold

        if not np.any(mask):
            if self.verbose:
                print("DEBUG: No detections passed threshold")
            return []

        boxes = boxes[mask]
        scores = scores[mask]

        # Sort by score
        indices = np.argsort(scores)[::-1]
        boxes = boxes[indices]
        scores = scores[indices]

        # Scale boxes back to original image using ratio
        ratio = preprocess_info["ratio"]
        boxes = boxes / ratio  # Scale back to original image size

        results = []
        for box, score in zip(boxes[:1], scores[:1], strict=True):  # Only top 1 person
            x1, y1, x2, y2 = box

            # Clip to image bounds
            x1 = max(0, min(x1, orig_w))
            y1 = max(0, min(y1, orig_h))
            x2 = max(0, min(x2, orig_w))
            y2 = max(0, min(y2, orig_h))

            results.append([float(x1), float(y1), float(x2), float(y2), float(score)])

        return results

    def process_frame(
        self, frame: np.ndarray, timestamp_ms: int = 0
    ) -> dict[str, tuple[float, float, float]] | None:
        """Process a single frame and extract pose landmarks.

        Args:
            frame: BGR image frame (OpenCV format)
            timestamp_ms: Frame timestamp in milliseconds (unused, for API compatibility)

        Returns:
            Dictionary mapping landmark names to (x, y, visibility) tuples,
            or None if no pose detected.
        """
        if frame.size == 0:
            return None

        height, width = frame.shape[:2]

        try:
            # Detection
            with self.timer.measure("optimized_cpu_detection"):
                if self.verbose:
                    print("DEBUG: Starting detection...")

                det_input = self._preprocess_det(frame)

                if self.verbose:
                    print(f"DEBUG: det_input input shape: {det_input['input'].shape}")

                det_outputs = self.det_session.run(
                    self.det_output_names,
                    {self.det_input_name: det_input["input"]},
                )

                if self.verbose:
                    det_output_0: np.ndarray = det_outputs[0]  # type: ignore[index]
                    print(f"DEBUG: det_outputs[0] shape: {det_output_0.shape}")

                detections = self._postprocess_det(list(det_outputs), height, width, det_input)  # type: ignore[arg-type]

                if self.verbose:
                    print(f"DEBUG: detections count: {len(detections)}")

            if not detections:
                return None

            # Get the highest confidence person bbox
            x1, y1, x2, y2, _score = detections[0]

            # Pose estimation
            with self.timer.measure("optimized_cpu_pose_inference"):
                try:
                    pose_input = self._preprocess_pose(frame, [x1, y1, x2, y2])
                except Exception as e:
                    if self.verbose:
                        print(f"Preprocessing error: {e}")
                        import traceback

                        traceback.print_exc()
                    return None

                try:
                    pose_outputs_any = self.pose_session.run(
                        self.pose_output_names,
                        {self.pose_input_name: pose_input},
                    )
                    # ONNX Runtime returns tuple[Any, ...], but we know these are ndarrays
                    pose_outputs: tuple[np.ndarray, ...] = tuple(
                        o if isinstance(o, np.ndarray) else np.array(o) for o in pose_outputs_any
                    )
                except Exception as e:
                    if self.verbose:
                        print(f"ONNX inference error: {e}")
                        import traceback

                        traceback.print_exc()
                    return None

            # Extract landmarks from output
            with self.timer.measure("landmark_extraction"):
                landmarks = self._extract_landmarks_from_output(
                    pose_outputs, [x1, y1, x2, y2], width, height
                )

            return landmarks

        except Exception as e:
            if self.verbose:
                print(f"Optimized CPU tracker error: {e}")
            return None

    def _extract_landmarks_from_output(
        self,
        outputs: tuple[np.ndarray, ...] | Sequence[np.ndarray],
        bbox: list,
        img_width: int,
        img_height: int,
    ) -> dict[str, tuple[float, float, float]]:
        """Extract landmarks from RTMPose SIMCC output.

        RTMPose uses SIMCC (SimCC-based coordinate representation) which outputs
        dual 1-D heatmaps for horizontal and vertical coordinates.

        Args:
            outputs: ONNX model outputs [simcc_x, simcc_y]
                - simcc_x: (1, 26, Wx) horizontal heatmap
                - simcc_y: (1, 26, Wy) vertical heatmap
            bbox: Bounding box [x1, y1, x2, y2]
            img_width: Original image width
            img_height: Original image height

        Returns:
            Dictionary mapping landmark names to normalized (x, y, visibility) tuples
        """

        # Extract SIMCC outputs
        simcc_x = outputs[0]  # Expected: (1, 26, Wx)
        simcc_y = outputs[1]  # Expected: (1, 26, Wy)

        if self.verbose:
            print(f"DEBUG: simcc_x shape = {simcc_x.shape}")
            print(f"DEBUG: simcc_y shape = {simcc_y.shape}")

        # Decode SIMCC to get keypoint locations - MATCHING RTMLIB EXACTLY
        # simcc_x shape: (1, 26, wx) where wx = input_width * 2
        # simcc_y shape: (1, 26, wy) where wy = input_height * 2
        n, k, _wx = simcc_x.shape

        # CRITICAL: Reshape to (n*k, -1) before argmax like rtmlib does
        simcc_x_flat = simcc_x.reshape(n * k, -1)
        simcc_y_flat = simcc_y.reshape(n * k, -1)

        # Get maximum value locations (argmax along last axis of flat arrays)
        x_locs_flat = np.argmax(simcc_x_flat, axis=1)
        y_locs_flat = np.argmax(simcc_y_flat, axis=1)

        # Get maximum values
        max_val_x = np.amax(simcc_x_flat, axis=1)
        max_val_y = np.amax(simcc_y_flat, axis=1)

        # Combine x and y confidence (average of both axes)
        vals_flat = 0.5 * (max_val_x + max_val_y)

        # Stack locations
        locs_flat = np.stack((x_locs_flat, y_locs_flat), axis=-1).astype(np.float32)

        # CRITICAL: Mask invalid locations (where confidence <= 0)
        locs_flat[vals_flat <= 0.0] = -1

        # Reshape back to (n, k, 2) and (n, k)
        locs = locs_flat.reshape(n, k, 2)
        scores = vals_flat.reshape(n, k)

        # Extract first person's keypoints
        keypoints = locs[0]  # (26, 2)
        confidences = scores[0]  # (26,)

        # SIMCC split ratio (default is 2.0 - resolution is 2x input size)
        simcc_split_ratio = 2.0
        keypoints = keypoints / simcc_split_ratio  # Now in model input size coordinates

        # Convert from model input size back to original image coordinates
        # We need the bbox center and scale for rescaling
        x1, y1, x2, y2 = bbox

        # Calculate center and scale (from bbox_xyxy2cs with padding=1.25)
        center = np.array([x1 + x2, y1 + y2]) * 0.5
        scale = np.array([x2 - x1, y2 - y1]) * 1.25

        # CRITICAL: Apply the same aspect ratio adjustment used in _preprocess_pose!
        # This matches rtmlib's top_down_affine logic
        model_h, model_w = self.pose_input_size
        aspect_ratio = model_w / model_h

        b_w = scale[0]
        b_h = scale[1]

        # Reshape to maintain aspect ratio (must match _preprocess_pose)
        if b_w > b_h * aspect_ratio:
            scale = np.array([b_w, b_w / aspect_ratio], dtype=np.float32)
        else:
            scale = np.array([b_h * aspect_ratio, b_h], dtype=np.float32)

        # Rescale keypoints to original image
        # Following RTMPose.postprocess() logic:
        # keypoints = keypoints / model_input_size * scale
        # keypoints = keypoints + center - scale / 2
        model_h, model_w = self.pose_input_size
        keypoints = keypoints / np.array([model_w, model_h]) * scale
        keypoints = keypoints + center - scale / 2

        # Build landmark dictionary with Halpe-26 to kinemotion mapping
        landmarks = {}

        for halpe_idx, name in HALPE_TO_KINEMOTION.items():
            if halpe_idx >= keypoints.shape[0]:
                continue

            x_pixel, y_pixel = keypoints[halpe_idx]
            confidence = float(confidences[halpe_idx])

            # Normalize to [0, 1] like MediaPipe
            x_norm = float(x_pixel / img_width)
            y_norm = float(y_pixel / img_height)

            # Clamp to valid range
            x_norm = max(0.0, min(1.0, x_norm))
            y_norm = max(0.0, min(1.0, y_norm))

            # Use confidence as visibility (MediaPipe compatibility)
            landmarks[name] = (x_norm, y_norm, confidence)

        return landmarks

    def close(self) -> None:
        """Release resources."""
        pass
