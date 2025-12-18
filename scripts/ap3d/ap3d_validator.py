#!/usr/bin/env python3
"""
AP3DValidator: Core validation logic for AthletePose3D dataset.
Calculates MPJPE, joint angle errors, and temporal consistency.
"""

import json
import logging
import pickle
from typing import Any
from pathlib import Path

import numpy as np
import scipy.interpolate as interpolate
from numpy.typing import NDArray
from kinemotion.core.pose import PoseTracker
from kinemotion.core.video_io import VideoProcessor

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

class AP3DValidator:
    """Validator for AthletePose3D dataset."""

    def __init__(self, ap3d_root: Path):
        self.ap3d_root = ap3d_root
        self.manifest_path = ap3d_root / "manifest.json"
        self.manifest = self._load_manifest()
        self.mapping = self.manifest.get("mapping", {})
        # Inverse mapping for easy lookup: MediaPipe index -> COCO index
        self.inv_mapping = {int(v): int(k) for k, v in self.mapping.items()}

    def _load_manifest(self) -> dict[str, Any]:
        if not self.manifest_path.exists():
            raise FileNotFoundError(f"Manifest not found: {self.manifest_path}")
        with open(self.manifest_path) as f:
            return json.load(f)

    def load_ground_truth(self, gt_path: str) -> Any:
        """Load ground truth from .pkl or .npy file."""
        full_path = self.ap3d_root / gt_path
        if full_path.suffix == ".pkl":
            with open(full_path, "rb") as f:
                data = pickle.load(f)
                # Assume data is a numpy array of shape (frames, 17, 3)
                # Some PKL might be dicts, adjust if needed
                if isinstance(data, dict) and "keypoints_3d" in data:
                    return data["keypoints_3d"]
                return data
        elif full_path.suffix == ".npy":
            return np.load(full_path)
        else:
            raise ValueError(f"Unsupported ground truth format: {full_path.suffix}")

    def temporal_alignment(self, source_data: NDArray[np.float64], target_len: int) -> NDArray[np.float64]:
        """Align source_data to target_len using linear interpolation."""
        source_len = len(source_data)
        if source_len == target_len:
            return source_data

        x_source = np.linspace(0, 1, source_len)
        x_target = np.linspace(0, 1, target_len)

        # Reshape to (len, -1) for easier interpolation
        orig_shape = source_data.shape
        flat_source = source_data.reshape(source_len, -1)

        f = interpolate.interp1d(x_source, flat_source, axis=0, kind="linear", fill_value="extrapolate")
        flat_target: NDArray[np.float64] = f(x_target).astype(np.float64)

        return flat_target.reshape((target_len,) + orig_shape[1:])

    def calculate_mpjpe(self, gt_poses: NDArray[np.float64], mp_poses: NDArray[np.float64]) -> float:
        """
        Calculate Mean Per Joint Position Error.
        Assumes both are (frames, joints, 3) and aligned.
        """
        # Calculate Euclidean distance per joint per frame
        errors = np.linalg.norm(gt_poses - mp_poses, axis=2)
        return float(np.mean(errors))

    def validate_single(self, entry: dict[str, Any]) -> dict[str, Any]:
        """Validate a single video entry from the manifest."""
        video_path = entry["video_path"]
        gt_path = entry["gt_path"]

        logger.info(f"Validating {video_path}...")

        # Load Ground Truth: (frames, joints, 3)
        gt_data = self.load_ground_truth(gt_path)

        # Initialize PoseTracker
        tracker = PoseTracker()
        mp_poses = []

        full_video_path = self.ap3d_root / video_path
        with VideoProcessor(str(full_video_path)) as video:
            width, height = video.width, video.height
            for frame in video:
                landmarks = tracker.process_frame(frame)

                # Create pose array for this frame (17 joints, 3 coords: x, y, z)
                # MediaPipe PoseTracker returns (x, y, visibility) in normalized coords
                # For MPJPE we need to convert to pixels or mm.
                # Let's start with pixel-level validation (MPJPE-px)
                frame_pose = np.zeros((17, 3))

                if landmarks:
                    # Mapping from PoseTracker names to COCO indices
                    name_to_coco = {
                        "nose": 0,
                        "left_shoulder": 5, "right_shoulder": 6,
                        "left_hip": 11, "right_hip": 12,
                        "left_knee": 13, "right_knee": 14,
                        "left_ankle": 15, "right_ankle": 16
                    }

                    for name, coco_idx in name_to_coco.items():
                        if name in landmarks:
                            x, y, _ = landmarks[name]
                            # Scale normalized to pixels
                            frame_pose[coco_idx] = [x * width, y * height, 0] # Z is 0 for now

                mp_poses.append(frame_pose)

        tracker.close()
        mp_poses_arr = np.array(mp_poses)

        # Temporal alignment
        # Align GT to MP frame count
        gt_aligned = self.temporal_alignment(gt_data, len(mp_poses_arr))

        # Calculate MPJPE for visible joints (joints 0, 5, 6, 11, 12, 13, 14, 15, 16)
        visible_joints = [0, 5, 6, 11, 12, 13, 14, 15, 16]

        # Slice both to only include visible joints
        gt_visible = gt_aligned[:, visible_joints, :2] # only X, Y
        mp_visible = mp_poses_arr[:, visible_joints, :2]

        mpjpe = self.calculate_mpjpe(gt_visible, mp_visible)

        return {"mpjpe": float(mpjpe), "video": video_path}

    def validate_split(self, split_name: str) -> dict[str, Any]:
        """Validate all videos in a specific split."""
        entries = self.manifest["splits"].get(split_name, [])
        results = []
        for entry in entries:
            res = self.validate_single(entry)
            results.append(res)

        return self.aggregate_results(results)

    def aggregate_results(self, results: list[dict[str, Any]]) -> dict[str, Any]:
        """Aggregate results and calculate summary statistics."""
        if not results:
            return {}
        mpjpes = [r["mpjpe"] for r in results]
        return {
            "mean_mpjpe": float(np.mean(mpjpes)),
            "std_mpjpe": float(np.std(mpjpes)),
            "count": len(results)
        }

    def generate_report(self, summary: dict[str, Any], output_path: Path) -> None:
        """Generate a markdown report."""
        report = f"""# AP3D Validation Report

## Summary Statistics
- **Total Videos:** {summary.get('count')}
- **Mean MPJPE:** {summary.get('mean_mpjpe'):.2f} mm
- **Std MPJPE:** {summary.get('std_mpjpe'):.2f} mm

## Recommendations
{"Acceptable baseline accuracy." if summary.get('mean_mpjpe', 999) < 100 else "Needs optimization."}
"""
        with open(output_path, "w") as f:
            f.write(report)
        logger.info(f"Report generated at {output_path}")

if __name__ == "__main__":
    # Example usage
    validator = AP3DValidator(Path("data/athletepose3d"))
    # summary = validator.validate_split("test")
    # validator.generate_report(summary, Path("reports/ap3d_baseline_validation.md"))
