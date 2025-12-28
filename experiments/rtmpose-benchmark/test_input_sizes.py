#!/usr/bin/env python3
"""Quick test of input size optimization."""

import sys
from pathlib import Path
from time import perf_counter

import cv2

sys.path.insert(0, str(Path(__file__).parent))
from rtmpose_tracker import RTMPoseTracker

PROJECT_ROOT = Path(__file__).parent.parent.parent
VIDEO_PATH = str(PROJECT_ROOT / "samples/test-videos/dj-45-IMG_6739.mp4")

# Test configurations
INPUT_SIZES = [
    ("192x256 (default)", (192, 256)),
    ("160x160", (160, 160)),
    ("128x128", (128, 128)),
]

print("=" * 60)
print("Input Size Optimization Test")
print("=" * 60)
print(f"Video: {Path(VIDEO_PATH).name}")
print()

results = {}

for name, input_size in INPUT_SIZES:
    print(f"Testing {name}...")

    # Create tracker with specific input size
    tracker = RTMPoseTracker(mode="lightweight", device="cpu", pose_input_size=input_size)

    # Run benchmark
    cap = cv2.VideoCapture(VIDEO_PATH)
    frame_count = 0
    start_time = perf_counter()

    while True:
        ret, frame = cap.read()
        if not ret or frame_count >= 100:  # Test 100 frames
            break
        tracker.process_frame(frame)
        frame_count += 1

    elapsed = perf_counter() - start_time
    fps = frame_count / elapsed if elapsed > 0 else 0

    results[name] = {"fps": fps, "frame_count": frame_count, "time": elapsed}
    print(f"  FPS: {fps:.1f}")

    cap.release()
    tracker.close()

print()
print("=" * 60)
print("RESULTS")
print("=" * 60)
print(f"{'Configuration':<20} {'FPS':<10} {'Improvement':<15}")
print("-" * 60)

baseline = results["192x256 (default)"]["fps"]
for name, data in results.items():
    improvement = (data["fps"] / baseline * 100) - 100 if baseline > 0 else 0
    vs_mp = data["fps"] / 49.6 * 100
    print(
        f"{name:<20} {data['fps']:<10.1f} {improvement:>+6.1f}%        ({vs_mp:.1f}% of MediaPipe)"
    )
