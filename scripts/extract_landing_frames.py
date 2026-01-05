#!/usr/bin/env python3
"""
Extract frames around landing detection for visual verification.

Creates side-by-side comparison images showing:
- Current algorithm detection frame
- Vel deriv onset detection frame
- Ground truth frame (if available)
"""

import json
import sys
from pathlib import Path

import cv2
import numpy as np

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from kinemotion.core.video_io import VideoProcessor


def extract_frames(video_path: Path, frames: dict[str, int], output_dir: Path):
    """Extract specific frames from video and save as images."""
    output_dir.mkdir(parents=True, exist_ok=True)

    video_name = video_path.stem

    with VideoProcessor(str(video_path)) as video:
        # Get all unique frames to extract (sorted)
        all_frames = sorted(set(frames.values()))
        min_frame = min(all_frames) - 3
        max_frame = max(all_frames) + 3

        frame_images = {}

        for frame_idx, frame in enumerate(video):
            if frame_idx < min_frame:
                continue
            if frame_idx > max_frame:
                break

            if frame_idx in all_frames or min_frame <= frame_idx <= max_frame:
                # Convert BGR to RGB for display
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_images[frame_idx] = frame_rgb

    # Create comparison images
    frame_list = sorted(frame_images.keys())

    # Create a strip of frames around landing
    strip_frames = []
    labels = []

    for f in frame_list:
        img = frame_images[f].copy()

        # Add frame number
        cv2.putText(img, f"Frame {f}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        # Mark detection points
        markers = []
        for name, frame_num in frames.items():
            if f == frame_num:
                markers.append(name)

        if markers:
            marker_text = " | ".join(markers)
            cv2.putText(img, marker_text, (10, 70),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            # Add green border
            cv2.rectangle(img, (0, 0), (img.shape[1]-1, img.shape[0]-1),
                         (0, 255, 0), 5)

        strip_frames.append(img)
        labels.append(f)

    # Resize frames for strip
    target_width = 320
    resized_frames = []
    for img in strip_frames:
        h, w = img.shape[:2]
        scale = target_width / w
        new_h = int(h * scale)
        resized = cv2.resize(img, (target_width, new_h))
        resized_frames.append(resized)

    # Stack horizontally
    if resized_frames:
        strip = np.hstack(resized_frames)
        strip_bgr = cv2.cvtColor(strip, cv2.COLOR_RGB2BGR)
        output_path = output_dir / f"{video_name}_landing_comparison.jpg"
        cv2.imwrite(str(output_path), strip_bgr)
        print(f"Saved: {output_path}")

    # Also save individual annotated frames
    for name, frame_num in frames.items():
        if frame_num in frame_images:
            img = frame_images[frame_num].copy()
            cv2.putText(img, f"Frame {frame_num} - {name}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            output_path = output_dir / f"{video_name}_{name}_f{frame_num}.jpg"
            cv2.imwrite(str(output_path), img_bgr)


def main():
    # Define detection results from validation script
    results = {
        "cmj-45-IMG_6733.MOV": {
            "ground_truth": 142,
            "current": 142,
            "vel_deriv_onset": 140,
            "foot_velocity": 145,
        },
        "cmj-45-IMG_6734.MOV": {
            "ground_truth": 144,
            "current": 144,
            "vel_deriv_onset": 143,
            "foot_velocity": 147,
        },
        "cmj-45-IMG_6735.MOV": {
            "ground_truth": 130,
            "current": 130,
            "vel_deriv_onset": 128,
            "foot_velocity": 132,
        },
    }

    validation_dir = project_root / "samples" / "validation"
    output_dir = project_root / "output" / "landing_frames"

    for video_name, frames in results.items():
        video_path = validation_dir / video_name
        if video_path.exists():
            print(f"\nProcessing: {video_name}")
            extract_frames(video_path, frames, output_dir)
        else:
            print(f"Video not found: {video_path}")


if __name__ == "__main__":
    main()
