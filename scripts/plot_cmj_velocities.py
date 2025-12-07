#!/usr/bin/env python3
"""
Plot CMJ velocity profiles to understand standing_end detection issue.
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from kinemotion.cmj.analysis import compute_signed_velocity
from kinemotion.core.pose import PoseTracker
from kinemotion.core.video_io import VideoProcessor
from kinemotion.dropjump.analysis import extract_foot_positions_and_visibilities

# Test video with standing_end issue
video_path = "samples/validation/cmj-45-IMG_6735.MOV"
standing_gt = 56
lowest_gt = 77
takeoff_gt = 93
landing_gt = 130

print(f"Analyzing: {Path(video_path).name}")
print(f"GT: standing_end={standing_gt}, lowest={lowest_gt}, takeoff={takeoff_gt}, landing={landing_gt}")

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

# Extract foot positions
positions, visibilities = extract_foot_positions_and_visibilities(landmarks_sequence)

# Calculate signed velocities (same as CMJ uses)
velocities = compute_signed_velocity(positions, window_length=5, polyorder=2)

print(f"\nVelocity statistics:")
print(f"  Mean abs: {np.mean(np.abs(velocities)):.4f}")
print(f"  Std: {np.std(velocities):.4f}")
print(f"  Max abs: {np.max(np.abs(velocities)):.4f}")

# Check velocities around standing phase
standing_phase = velocities[:standing_gt]
print(f"\nStanding phase (frames 0-{standing_gt}):")
print(f"  Mean abs: {np.mean(np.abs(standing_phase)):.4f}")
print(f"  Max abs: {np.max(np.abs(standing_phase)):.4f}")
print(f"  95th percentile: {np.percentile(np.abs(standing_phase), 95):.4f}")
print(f"  Mean SIGNED: {np.mean(standing_phase):.4f}")

# Check early countermovement (between standing_gt and lowest_gt)
early_cm = velocities[standing_gt:lowest_gt]
print(f"\nEarly countermovement (frames {standing_gt}-{lowest_gt}):")
print(f"  Mean abs: {np.mean(np.abs(early_cm)):.4f}")
print(f"  Max abs: {np.max(np.abs(early_cm)):.4f}")
print(f"  Mean SIGNED: {np.mean(early_cm):.4f} (positive = downward)")
print(f"  Max SIGNED: {np.max(early_cm):.4f}")

# Check position changes
standing_positions = positions[:standing_gt]
early_cm_positions = positions[standing_gt:lowest_gt]
print(f"\nPosition analysis:")
print(f"  Standing baseline (frames 0-{standing_gt}): {np.mean(standing_positions):.4f} ± {np.std(standing_positions):.4f}")
print(f"  Early CM positions (frames {standing_gt}-{lowest_gt}): {np.mean(early_cm_positions):.4f} ± {np.std(early_cm_positions):.4f}")
print(f"  Position change: {np.mean(early_cm_positions) - np.mean(standing_positions):.4f}")

# Look for position threshold crossing
baseline_pos = np.mean(standing_positions[:30])  # First 30 frames as baseline
position_change = positions - baseline_pos
print(f"\nBaseline position (first 30 frames): {baseline_pos:.4f}")
print(f"Position at standing_end GT ({standing_gt}): {positions[standing_gt]:.4f}, change: {position_change[standing_gt]:.4f}")
print(f"Position at lowest ({lowest_gt}): {positions[lowest_gt]:.4f}, change: {position_change[lowest_gt]:.4f}")

# Test current threshold
print(f"\nCurrent threshold: 0.005")
low_vel_frames = np.nonzero(np.abs(velocities[:lowest_gt]) < 0.005)[0]
if len(low_vel_frames) > 0:
    current_detection = low_vel_frames[-1]
    print(f"  Detected standing_end: {current_detection}")
    print(f"  Error: {abs(current_detection - standing_gt)} frames")

# Test improved threshold
print(f"\nImproved threshold: 0.002")
low_vel_frames_new = np.nonzero(np.abs(velocities[:lowest_gt]) < 0.002)[0]
if len(low_vel_frames_new) > 0:
    new_detection = low_vel_frames_new[-1]
    print(f"  Detected standing_end: {new_detection}")
    print(f"  Error: {abs(new_detection - standing_gt)} frames")

# Plot
fig, axes = plt.subplots(3, 1, figsize=(14, 10))

# Plot 1: Positions
axes[0].plot(positions, 'b-', linewidth=0.8)
axes[0].axvline(standing_gt, color='purple', linestyle='--', linewidth=2, label='Standing End (GT)')
axes[0].axvline(lowest_gt, color='orange', linestyle='--', linewidth=2, label='Lowest Point (GT)')
axes[0].axvline(takeoff_gt, color='green', linestyle='--', linewidth=2, label='Takeoff (GT)')
axes[0].axvline(landing_gt, color='red', linestyle='--', linewidth=2, label='Landing (GT)')
axes[0].set_ylabel('Position (normalized)')
axes[0].set_title(f'{Path(video_path).name} - CMJ Foot Position')
axes[0].legend(loc='upper right')
axes[0].grid(True, alpha=0.3)
axes[0].invert_yaxis()  # Invert so jump looks upward

# Plot 2: Signed velocities
axes[1].plot(velocities, 'g-', linewidth=0.8)
axes[1].axhline(0.005, color='red', linestyle=':', linewidth=2, label='Current threshold (0.005)')
axes[1].axhline(-0.005, color='red', linestyle=':', linewidth=2)
axes[1].axhline(0.002, color='orange', linestyle='--', linewidth=2, label='Proposed threshold (0.002)')
axes[1].axhline(-0.002, color='orange', linestyle='--', linewidth=2)
axes[1].axvline(standing_gt, color='purple', linestyle='--', linewidth=2, label='Standing End (GT)')
axes[1].axvline(lowest_gt, color='orange', linestyle='--', linewidth=2)
axes[1].set_ylabel('Velocity (signed)')
axes[1].set_title('CMJ Velocity Profile')
axes[1].legend(loc='upper right')
axes[1].grid(True, alpha=0.3)

# Plot 3: Absolute velocities with thresholds
abs_vel = np.abs(velocities)
axes[2].plot(abs_vel, 'purple', linewidth=0.8)
axes[2].axhline(0.005, color='red', linestyle='-', linewidth=2, label='Current threshold (0.005)')
axes[2].axhline(0.002, color='orange', linestyle='--', linewidth=2, label='Proposed threshold (0.002)')
axes[2].axvline(standing_gt, color='purple', linestyle='--', linewidth=2, label='Standing End (GT)')
axes[2].axvline(lowest_gt, color='orange', linestyle='--', linewidth=2)
axes[2].axvline(takeoff_gt, color='green', linestyle='--', linewidth=2)
axes[2].fill_between(range(len(abs_vel)), 0, 0.005, alpha=0.2, color='red', label='Current: detected as stationary')
axes[2].fill_between(range(len(abs_vel)), 0, 0.002, alpha=0.3, color='orange', label='Proposed: detected as stationary')
axes[2].set_ylabel('|Velocity|')
axes[2].set_xlabel('Frame')
axes[2].set_title('Absolute Velocity - Standing Detection')
axes[2].legend(loc='upper right')
axes[2].grid(True, alpha=0.3)
axes[2].set_ylim([0, 0.02])

plt.tight_layout()
plt.savefig('/tmp/cmj_velocity_debug.png', dpi=150)
print(f"\n✓ Plot saved to: /tmp/cmj_velocity_debug.png")
