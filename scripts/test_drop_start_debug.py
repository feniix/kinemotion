#!/usr/bin/env python3
"""
Test detect_drop_start with debug enabled to see why it fails on some videos.
"""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from kinemotion.core.pose import PoseTracker
from kinemotion.core.video_io import VideoProcessor
from kinemotion.dropjump.analysis import (
    detect_drop_start,
    extract_foot_positions_and_visibilities,
)

# Test all 3 drop jump videos
videos = [
    "samples/validation/dj-45-IMG_6739.MOV",  # Works (drop_start=130)
    "samples/validation/dj-45-IMG_6740.MOV",  # Fails (drop_start=0)
    "samples/validation/dj-45-IMG_6741.MOV",  # Fails (drop_start=0)
]

for video_path in videos:
    print("=" * 80)
    print(f"Testing: {Path(video_path).name}")
    print("=" * 80)

    # Process video
    video_processor = VideoProcessor(video_path)
    fps = video_processor.fps
    frame_count = video_processor.frame_count
    print(f"FPS: {fps:.1f}")
    print(f"Frame count: {frame_count}")

    # Get pose landmarks
    pose_tracker = PoseTracker()
    landmarks_sequence = []

    for frame_idx in range(frame_count):
        frame = video_processor.read_frame()
        if frame is None:
            break

        results = pose_tracker.process_frame(frame)
        landmarks_sequence.append(results)

    # Extract foot positions
    positions, visibilities = extract_foot_positions_and_visibilities(landmarks_sequence)
    print(f"Total frames: {len(positions)}")
    print(f"Position range: {np.min(positions):.4f} - {np.max(positions):.4f}")
    print(f"Position std: {np.std(positions):.4f}")

    # Test with DEFAULT parameters
    print("\n--- Test 1: DEFAULT parameters (min_stationary=1.0, threshold=0.02) ---")
    drop_start_default = detect_drop_start(
        positions, fps, min_stationary_duration=1.0, position_change_threshold=0.02, debug=True
    )
    print(f"✓ Detected drop_start: {drop_start_default}\n")

    # Test with API parameters (the ones actually used!)
    print("--- Test 2: API parameters (min_stationary=0.5, threshold=0.005) ---")
    drop_start_api = detect_drop_start(
        positions, fps, min_stationary_duration=0.5, position_change_threshold=0.005, debug=True
    )
    print(f"✓ Detected drop_start: {drop_start_api}\n")

    print("=" * 40)
    print(f"DEFAULT: {drop_start_default}")
    print(f"API:     {drop_start_api}")
    print(f"DIFF:    {abs(drop_start_default - drop_start_api)}")
    print()
