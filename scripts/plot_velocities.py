#!/usr/bin/env python3
"""
Plot velocity profiles to understand why contact detection fails.
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from kinemotion.core.pose import PoseTracker
from kinemotion.core.smoothing import compute_velocity_from_derivative
from kinemotion.core.video_io import VideoProcessor
from kinemotion.dropjump.analysis import (
    extract_foot_positions_and_visibilities,
)

# Test video 2 (complete failure)
video_path = "samples/validation/dj-45-IMG_6740.MOV"
drop_gt = 141
landing_gt = 154
takeoff_gt = 166

print(f"Analyzing: {Path(video_path).name}")
print(f"GT: drop={drop_gt}, landing={landing_gt}, takeoff={takeoff_gt}")

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

# Calculate velocities
velocities = compute_velocity_from_derivative(positions, window_length=5, polyorder=2)

print(f"\nVelocity statistics:")
print(f"  Mean: {np.mean(np.abs(velocities)):.4f}")
print(f"  Std: {np.std(velocities):.4f}")
print(f"  Max abs: {np.max(np.abs(velocities)):.4f}")
print(f"  Min abs: {np.min(np.abs(velocities)):.4f}")

# Check velocities at key events
print(f"\nVelocities at key events:")
print(f"  Drop GT ({drop_gt}): {velocities[drop_gt]:.4f} (abs: {abs(velocities[drop_gt]):.4f})")
print(f"  Landing GT ({landing_gt}): {velocities[landing_gt]:.4f} (abs: {abs(velocities[landing_gt]):.4f})")
print(f"  Takeoff GT ({takeoff_gt}): {velocities[takeoff_gt]:.4f} (abs: {abs(velocities[takeoff_gt]):.4f})")

# Check standing phase (before drop) - should be very small
standing_phase = velocities[100:drop_gt]  # 40 frames before drop
print(f"\nStanding phase velocities (frames 100-{drop_gt}, before drop):")
print(f"  Mean abs: {np.mean(np.abs(standing_phase)):.4f}")
print(f"  Max abs: {np.max(np.abs(standing_phase)):.4f}")
print(f"  95th percentile: {np.percentile(np.abs(standing_phase), 95):.4f}")

# Check velocities during drop phase (should be large!)
drop_phase = velocities[drop_gt:landing_gt]
print(f"\nDrop phase velocities (frames {drop_gt}-{landing_gt}):")
print(f"  Mean abs: {np.mean(np.abs(drop_phase)):.4f}")
print(f"  Max abs: {np.max(np.abs(drop_phase)):.4f}")
print(f"  All > 0.01? {np.all(np.abs(drop_phase) > 0.01)}")

# Check velocities during flight phase (should be large!)
flight_phase = velocities[takeoff_gt:takeoff_gt+20] if takeoff_gt+20 < len(velocities) else velocities[takeoff_gt:]
print(f"\nFlight phase velocities (frames {takeoff_gt}-{takeoff_gt+20}):")
print(f"  Mean abs: {np.mean(np.abs(flight_phase)):.4f}")
print(f"  Max abs: {np.max(np.abs(flight_phase)):.4f}")
print(f"  All > 0.01? {np.all(np.abs(flight_phase) > 0.01)}")

# Create plot
fig, axes = plt.subplots(3, 1, figsize=(12, 10))

# Plot 1: Positions
axes[0].plot(positions, 'b-', linewidth=0.5)
axes[0].axvline(drop_gt, color='orange', linestyle='--', label='Drop (GT)')
axes[0].axvline(landing_gt, color='red', linestyle='--', label='Landing (GT)')
axes[0].axvline(takeoff_gt, color='green', linestyle='--', label='Takeoff (GT)')
axes[0].set_ylabel('Position (normalized)')
axes[0].set_title(f'{Path(video_path).name} - Foot Position')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# Plot 2: Velocities
axes[1].plot(velocities, 'g-', linewidth=0.5)
axes[1].axhline(0.01, color='red', linestyle=':', label='Threshold (0.01)')
axes[1].axhline(-0.01, color='red', linestyle=':')
axes[1].axvline(drop_gt, color='orange', linestyle='--', label='Drop (GT)')
axes[1].axvline(landing_gt, color='red', linestyle='--', label='Landing (GT)')
axes[1].axvline(takeoff_gt, color='green', linestyle='--', label='Takeoff (GT)')
axes[1].set_ylabel('Velocity')
axes[1].set_title('Foot Velocity (from derivative)')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

# Plot 3: Absolute velocities vs threshold
abs_velocities = np.abs(velocities)
axes[2].plot(abs_velocities, 'purple', linewidth=0.5)
axes[2].axhline(0.01, color='red', linestyle='--', linewidth=2, label='Current threshold (0.01)')
axes[2].axhline(0.02, color='orange', linestyle='--', linewidth=2, label='Potential threshold (0.02)')
axes[2].axvline(drop_gt, color='orange', linestyle='--', label='Drop (GT)')
axes[2].axvline(landing_gt, color='red', linestyle='--', label='Landing (GT)')
axes[2].axvline(takeoff_gt, color='green', linestyle='--', label='Takeoff (GT)')
axes[2].fill_between(range(len(abs_velocities)), 0, 0.01, alpha=0.2, color='red', label='Detected as stationary')
axes[2].set_ylabel('|Velocity|')
axes[2].set_xlabel('Frame')
axes[2].set_title('Absolute Velocity vs Thresholds')
axes[2].legend()
axes[2].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('/tmp/velocity_debug.png', dpi=150)
print(f"\n✓ Plot saved to: /tmp/velocity_debug.png")
