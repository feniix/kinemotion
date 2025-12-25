"""Test RTMPose with device='mps' (CoreML EP)."""

import sys
import time
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from rtmpose_tracker import RTMPoseTracker

VIDEO_PATH = "samples/test-videos/cmj-45-IMG_6733.mp4"

print("=== RTMPose CoreML (device='mps') Performance Test ===")
print(f"Video: {Path(VIDEO_PATH).name}")
print()

cap = cv2.VideoCapture(VIDEO_PATH)
if not cap.isOpened():
    print(f"Error: Could not open video: {VIDEO_PATH}")
    exit(1)

total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
print(f"Total frames: {total_frames}")
print()

# Test 1: CPU baseline
print("1. Testing CPU (device='cpu')...")
tracker_cpu = RTMPoseTracker(mode="lightweight", device="cpu")

# Warmup
for _ in range(5):
    ret, frame = cap.read()
    if not ret:
        break
    tracker_cpu.process_frame(frame)

# Benchmark
cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
frame_times_cpu = []
start = time.time()

while True:
    ret, frame = cap.read()
    if not ret:
        break
    t0 = time.time()
    result = tracker_cpu.process_frame(frame)
    frame_times_cpu.append(time.time() - t0)

total_time_cpu = time.time() - start
fps_cpu = len(frame_times_cpu) / total_time_cpu
avg_ms_cpu = np.mean(frame_times_cpu) * 1000

print(f"   FPS: {fps_cpu:.2f}")
print(f"   Avg frame time: {avg_ms_cpu:.2f} ms")
print()

# Test 2: MPS/CoreML
print("2. Testing MPS/CoreML (device='mps')...")
try:
    tracker_mps = RTMPoseTracker(mode="lightweight", device="mps")

    # Warmup
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    for _ in range(5):
        ret, frame = cap.read()
        if not ret:
            break
        tracker_mps.process_frame(frame)

    # Benchmark
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    frame_times_mps = []
    start = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        t0 = time.time()
        result = tracker_mps.process_frame(frame)
        frame_times_mps.append(time.time() - t0)

    total_time_mps = time.time() - start
    fps_mps = len(frame_times_mps) / total_time_mps
    avg_ms_mps = np.mean(frame_times_mps) * 1000

    print(f"   FPS: {fps_mps:.2f}")
    print(f"   Avg frame time: {avg_ms_mps:.2f} ms")

    # Compare
    improvement = (fps_mps / fps_cpu - 1) * 100
    print()
    print("=== Comparison ===")
    print(f"CPU (device='cpu'):     {fps_cpu:.2f} FPS ({avg_ms_cpu:.2f} ms)")
    print(f"MPS/CoreML (device='mps'): {fps_mps:.2f} FPS ({avg_ms_mps:.2f} ms)")
    print(f"Difference: {improvement:+.1f}%")

    if fps_mps > fps_cpu:
        speedup = fps_mps / fps_cpu
        print(f"Speedup: {speedup:.2f}x")
    else:
        slowdown = fps_cpu / fps_mps
        print(f"Slowdown: {slowdown:.2f}x")

except Exception as e:
    print(f"   ERROR: {e}")
    import traceback

    traceback.print_exc()

cap.release()
