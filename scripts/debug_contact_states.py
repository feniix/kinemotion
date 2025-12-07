#!/usr/bin/env python3
"""
Debug contact states for drop jump videos to see why takeoff isn't detected.
"""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from kinemotion.core.pose import PoseTracker
from kinemotion.core.video_io import VideoProcessor
from kinemotion.dropjump.analysis import (
    ContactState,
    detect_ground_contact,
    extract_foot_positions_and_visibilities,
    find_contact_phases,
)

# Test the failing videos
videos = [
    ("samples/validation/dj-45-IMG_6739.MOV", 118, 131, 144),  # Video 1 - takeoff fails
    ("samples/validation/dj-45-IMG_6740.MOV", 141, 154, 166),  # Video 2 - both fail
]

for video_path, drop_gt, landing_gt, takeoff_gt in videos:
    print("=" * 80)
    print(f"Testing: {Path(video_path).name}")
    print(f"GT: drop={drop_gt}, landing={landing_gt}, takeoff={takeoff_gt}")
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

    # Extract foot positions
    positions, visibilities = extract_foot_positions_and_visibilities(landmarks_sequence)

    # Detect contact states with NEW optimized threshold
    contact_states = detect_ground_contact(
        positions,
        velocity_threshold=0.002,  # NEW: Empirically optimized (was 0.01)
        min_contact_frames=6,
        visibility_threshold=0.5,
        visibilities=visibilities,
    )

    # Find phases
    phases = find_contact_phases(contact_states)

    print(f"\nTotal frames: {len(contact_states)}")
    print(f"Total phases detected: {len(phases)}")
    print("\nPhases:")
    for i, (start, end, state) in enumerate(phases[:10]):  # Show first 10
        duration = (end - start) / fps * 1000
        state_name = "ON_GROUND" if state == ContactState.ON_GROUND else "IN_AIR"
        print(f"  {i+1}. Frames {start:3d}-{end:3d} ({duration:6.1f}ms): {state_name}")
        if i == 9 and len(phases) > 10:
            print(f"  ... and {len(phases) - 10} more phases")

    # Check contact states around key events
    print(f"\nContact states around key events:")
    print(f"  Drop GT ({drop_gt}): {contact_states[drop_gt].name if drop_gt < len(contact_states) else 'OUT OF RANGE'}")
    print(f"  Landing GT ({landing_gt}): {contact_states[landing_gt].name if landing_gt < len(contact_states) else 'OUT OF RANGE'}")
    print(f"  Takeoff GT ({takeoff_gt}): {contact_states[takeoff_gt].name if takeoff_gt < len(contact_states) else 'OUT OF RANGE'}")

    # Count state distribution
    on_ground = sum(1 for s in contact_states if s == ContactState.ON_GROUND)
    in_air = sum(1 for s in contact_states if s == ContactState.IN_AIR)
    unknown = sum(1 for s in contact_states if s == ContactState.UNKNOWN)

    print(f"\nContact state distribution:")
    print(f"  ON_GROUND: {on_ground} frames ({on_ground/len(contact_states)*100:.1f}%)")
    print(f"  IN_AIR: {in_air} frames ({in_air/len(contact_states)*100:.1f}%)")
    print(f"  UNKNOWN: {unknown} frames ({unknown/len(contact_states)*100:.1f}%)")
    print()
