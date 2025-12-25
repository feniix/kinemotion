"""Quick test to compare CPU vs CoreML EP performance using rtmlib-coreml."""

import time
from pathlib import Path

import cv2
import numpy as np

# Test with the rtmlib-coreml fork's Body class
from rtmlib import Body

VIDEO_PATH = "samples/test-videos/cmj-45-IMG_6733.mp4"

print("=== CoreML EP Performance Test ===")
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
print("1. Testing CPU baseline...")
body_cpu = Body(mode="lightweight", backend="onnxruntime", device="cpu", to_openpose=False)

# Warmup
for _ in range(5):
    ret, frame = cap.read()
    if not ret:
        break
    body_cpu(frame)

# Benchmark
cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
frame_times_cpu = []
start = time.time()

while True:
    ret, frame = cap.read()
    if not ret:
        break
    t0 = time.time()
    keypoints, scores = body_cpu(frame)
    frame_times_cpu.append(time.time() - t0)

total_time_cpu = time.time() - start
fps_cpu = len(frame_times_cpu) / total_time_cpu
avg_ms = np.mean(frame_times_cpu) * 1000

print(f"   FPS: {fps_cpu:.2f}")
print(f"   Avg frame time: {avg_ms:.2f} ms")
print()

# Test 2: CoreML EP
print("2. Testing CoreML EP...")
try:
    body_coreml = Body(
        mode="lightweight", backend="onnxruntime", device="coreml", to_openpose=False
    )

    # Warmup
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    for _ in range(5):
        ret, frame = cap.read()
        if not ret:
            break
        body_coreml(frame)

    # Benchmark
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    frame_times_coreml = []
    start = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        t0 = time.time()
        keypoints, scores = body_coreml(frame)
        frame_times_coreml.append(time.time() - t0)

    total_time_coreml = time.time() - start
    fps_coreml = len(frame_times_coreml) / total_time_coreml
    avg_ms_coreml = np.mean(frame_times_coreml) * 1000

    print(f"   FPS: {fps_coreml:.2f}")
    print(f"   Avg frame time: {avg_ms_coreml:.2f} ms")

    # Compare
    improvement = (fps_coreml / fps_cpu - 1) * 100
    print()
    print("=== Comparison ===")
    print(f"CPU:        {fps_cpu:.2f} FPS ({avg_ms:.2f} ms)")
    print(f"CoreML EP:  {fps_coreml:.2f} FPS ({avg_ms_coreml:.2f} ms)")
    print(f"Difference: {improvement:+.1f}%")

except Exception as e:
    print(f"   ERROR: {e}")
    import traceback

    traceback.print_exc()

cap.release()
