#!/usr/bin/env python3
"""Extract a single frame from video."""
import sys
from pathlib import Path
import cv2

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from kinemotion.core.video_io import VideoProcessor

video_path = project_root / "samples/validation/cmj-45-IMG_6733.MOV"
output_dir = project_root / "output/landing_frames"
target_frame = 141

with VideoProcessor(str(video_path)) as video:
    for frame_idx, frame in enumerate(video):
        if frame_idx == target_frame:
            cv2.putText(frame, f"Frame {frame_idx}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            output_path = output_dir / f"cmj-45-IMG_6733_frame_{frame_idx}.jpg"
            cv2.imwrite(str(output_path), frame)
            print(f"Saved: {output_path}")
            break
