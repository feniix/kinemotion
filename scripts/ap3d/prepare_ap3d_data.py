#!/usr/bin/env python3
"""
Prepare AthletePose3D dataset for validation.
Scans directories, extracts metadata, and creates a manifest.json.
"""

import json
import logging
import random
from pathlib import Path
from typing import Any

import click
import cv2

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# COCO 17 keypoints to MediaPipe 33 landmarks mapping
# COCO: [nose, l_eye, r_eye, l_ear, r_ear, l_shoulder, r_shoulder, l_elbow, r_elbow, l_wrist, r_wrist, l_hip, r_hip, l_knee, r_knee, l_ankle, r_ankle]
COCO_TO_MEDIAPIPE = {
    0: 0,   # nose
    1: 2,   # l_eye
    2: 5,   # r_eye
    3: 7,   # l_ear
    4: 8,   # r_ear
    5: 11,  # l_shoulder
    6: 12,  # r_shoulder
    7: 13,  # l_elbow
    8: 14,  # r_elbow
    9: 15,  # l_wrist
    10: 16, # r_wrist
    11: 23, # l_hip
    12: 24, # r_hip
    13: 25, # l_knee
    14: 26, # r_knee
    15: 27, # l_ankle
    16: 28, # r_ankle
}

def get_video_metadata(video_path: Path) -> dict[str, Any]:
    """Extract metadata from video file."""
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        return {}

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()

    return {
        "fps": fps,
        "frame_count": frame_count,
        "width": width,
        "height": height,
        "duration": frame_count / fps if fps > 0 else 0
    }

@click.command()
@click.option("--ap3d-root", type=click.Path(exists=True, path_type=Path), default="data/athletepose3d", help="Root directory of AP3D dataset")
@click.option("--train-split", type=float, default=0.7, help="Ratio of training data")
@click.option("--val-split", type=float, default=0.15, help="Ratio of validation data")
@click.option("--seed", type=int, default=42, help="Random seed for splitting")
def main(ap3d_root: Path, train_split: float, val_split: float, seed: int) -> None:
    """Scan AP3D dataset and generate manifest.json."""
    video_dir = ap3d_root / "videos"
    gt_dir = ap3d_root / "ground_truth"

    if not video_dir.exists():
        logger.error(f"Video directory not found: {video_dir}")
        return

    logger.info(f"Scanning videos in {video_dir}...")
    video_files = list(video_dir.glob("*.mp4")) + list(video_dir.glob("*.mov"))
    logger.info(f"Found {len(video_files)} videos.")

    manifest_entries = []

    for video_path in video_files:
        # Match with ground truth
        # AP3D often has matching names, e.g., video1.mp4 -> video1.pkl or video1.npy
        gt_path_pkl = gt_dir / f"{video_path.stem}.pkl"
        gt_path_npy = gt_dir / f"{video_path.stem}.npy"

        gt_path = None
        if gt_path_pkl.exists():
            gt_path = gt_path_pkl
        elif gt_path_npy.exists():
            gt_path = gt_path_npy

        if not gt_path:
            logger.warning(f"No ground truth found for {video_path.name}, skipping.")
            continue

        metadata = get_video_metadata(video_path)
        if not metadata:
            logger.warning(f"Could not read metadata for {video_path.name}, skipping.")
            continue

        entry = {
            "video_path": str(video_path.relative_to(ap3d_root)),
            "gt_path": str(gt_path.relative_to(ap3d_root)),
            "metadata": metadata,
            "movement_type": video_path.stem.split("-")[0] if "-" in video_path.stem else "unknown"
        }
        manifest_entries.append(entry)

    if not manifest_entries:
        logger.error("No valid video/ground-truth pairs found.")
        return

    # Shuffle and split
    random.seed(seed)
    random.shuffle(manifest_entries)

    num_total = len(manifest_entries)
    num_train = int(num_total * train_split)
    num_val = int(num_total * val_split)

    train_entries = manifest_entries[:num_train]
    val_entries = manifest_entries[num_train:num_train+num_val]
    test_entries = manifest_entries[num_train+num_val:]

    manifest = {
        "dataset": "AthletePose3D",
        "mapping": COCO_TO_MEDIAPIPE,
        "splits": {
            "train": train_entries,
            "validation": val_entries,
            "test": test_entries
        },
        "summary": {
            "total": num_total,
            "train": len(train_entries),
            "validation": len(val_entries),
            "test": len(test_entries)
        }
    }

    manifest_path = ap3d_root / "manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    logger.info(f"Manifest generated at {manifest_path}")
    logger.info(f"Total: {num_total} (Train: {len(train_entries)}, Val: {len(val_entries)}, Test: {len(test_entries)})")

if __name__ == "__main__":
    main()
