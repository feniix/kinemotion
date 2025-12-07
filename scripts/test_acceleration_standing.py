#!/usr/bin/env python3
"""
Test using acceleration to detect standing_end (start of countermovement).
"""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from kinemotion.cmj.analysis import compute_signed_velocity
from kinemotion.core.pose import PoseTracker
from kinemotion.core.smoothing import compute_acceleration_from_derivative
from kinemotion.core.video_io import VideoProcessor
from kinemotion.dropjump.analysis import extract_foot_positions_and_visibilities

# Test all 3 CMJ videos
videos = [
    ("samples/validation/cmj-45-IMG_6733.MOV", 65, 89),
    ("samples/validation/cmj-45-IMG_6734.MOV", 70, 90),
    ("samples/validation/cmj-45-IMG_6735.MOV", 56, 77),
]

for video_path, standing_gt, lowest_gt in videos:
    print("=" * 80)
    print(f"{Path(video_path).name}: standing_end GT={standing_gt}")
    print("=" * 80)

    # Process video
    video_processor = VideoProcessor(video_path)
    fps = video_processor.fps
    frame_count = video_processor.frame_count

    # Get pose landmarks
    pose_tracker = PoseTracker()
    landmarks_sequence = []

    for frame_idx in range(frame_count):
        frame = video_processor.read_frame()
        if frame is None:
            break
        results = pose_tracker.process_frame(frame)
        landmarks_sequence.append(results)

    # Extract positions
    positions, visibilities = extract_foot_positions_and_visibilities(landmarks_sequence)

    # Calculate acceleration
    accelerations = compute_acceleration_from_derivative(positions, window_length=5, polyorder=2)

    # Find where acceleration first becomes positive (downward movement starts)
    # Use frames 10-40 as baseline (should have near-zero acceleration)
    baseline_accel = accelerations[10:40]
    baseline_mean = np.mean(baseline_accel)
    baseline_std = np.std(baseline_accel)

    print(f"Baseline acceleration (frames 10-40): {baseline_mean:.6f} ± {baseline_std:.6f}")

    # Search from frame 40 onwards for positive acceleration spike
    accel_threshold = baseline_mean + 3 * baseline_std

    print(f"Acceleration threshold: {accel_threshold:.6f}")

    for i in range(40, lowest_gt):
        if accelerations[i] > accel_threshold:
            detected = i
            error = abs(detected - standing_gt)
            print(f"✓ Detected standing_end: {detected} (Error: {error} frames)")
            print(f"  Acceleration at detected frame: {accelerations[detected]:.6f}")
            print(f"  Acceleration at GT frame: {accelerations[standing_gt]:.6f}")
            break
    else:
        print(f"✗ No acceleration spike detected before lowest_point")

    print()
