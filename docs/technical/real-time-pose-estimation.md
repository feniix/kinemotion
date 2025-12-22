# Real-Time Pose Estimation Guide

**Last Updated:** December 2025

This guide covers real-time pose estimation options for kinemotion, comparing architectures, latency characteristics, and implementation strategies.

______________________________________________________________________

## Table of Contents

1. [Overview](#1-overview)
1. [Understanding Real-Time Requirements](#2-understanding-real-time-requirements)
1. [System Comparison](#3-system-comparison)
1. [RTMO: One-Stage Real-Time](#4-rtmo-one-stage-real-time)
1. [Architecture Options](#5-architecture-options)
1. [Implementation Examples](#6-implementation-examples)
1. [Latency Optimization](#7-latency-optimization)
1. [Recommended Strategy for kinemotion](#8-recommended-strategy-for-kinemotion)
1. [References](#9-references)

______________________________________________________________________

## 1. Overview

Real-time pose estimation requires balancing three competing factors:

```
                    ACCURACY
                       ▲
                      /|\
                     / | \
                    /  |  \
                   /   |   \
                  /    |    \
                 /     |     \
                /      |      \
               /       |       \
              ▼────────┴────────▼
           SPEED              SIMPLICITY
```

**Key Trade-offs:**

- **Higher accuracy** → More computation → Lower FPS
- **Lower latency** → Simpler models → Less accuracy
- **Browser deployment** → No server costs → Limited model options

### What "Real-Time" Means

| Term                | Latency | FPS | Use Case               |
| ------------------- | ------- | --- | ---------------------- |
| **Interactive**     | \<100ms | 10+ | Live coaching feedback |
| **Real-time**       | \<50ms  | 20+ | Video games, AR        |
| **Ultra real-time** | \<16ms  | 60+ | VR, motion capture     |

For sports coaching, **interactive (\<100ms)** is typically sufficient.

______________________________________________________________________

## 2. Understanding Real-Time Requirements

### 2.1 Latency Budget

```
Total Latency = Capture + Network (upload) + Processing + Network (download) + Render

Example: Server-side processing
─────────────────────────────────────────────────────────────────────
Camera capture:     ~3ms   ████
Encode frame:       ~5ms   ██████
Network upload:    ~20ms   ████████████████████
Server processing: ~25ms   █████████████████████████
Network download:  ~20ms   ████████████████████
Decode + render:    ~5ms   ██████
─────────────────────────────────────────────────────────────────────
Total:             ~78ms

Example: Browser-only processing
─────────────────────────────────────────────────────────────────────
Camera capture:     ~3ms   ████
Processing:        ~30ms   ██████████████████████████████
Render:             ~2ms   ███
─────────────────────────────────────────────────────────────────────
Total:             ~35ms
```

### 2.2 Frame Rate Requirements by Sport

| Activity          | Min FPS | Recommended | Reason                      |
| ----------------- | ------- | ----------- | --------------------------- |
| **CMJ/Drop Jump** | 15      | 30+         | Capture takeoff/landing     |
| **Sprint**        | 30      | 60+         | Fast limb movement          |
| **Weightlifting** | 15      | 30          | Slower, controlled movement |
| **Wall Ball**     | 20      | 30+         | Explosive throws            |

______________________________________________________________________

## 3. System Comparison

### 3.1 Real-Time Performance Matrix

| System          | Paradigm  | GPU FPS  | CPU FPS | Latency | Multi-Person |
| --------------- | --------- | -------- | ------- | ------- | ------------ |
| **RTMO-l**      | One-stage | **141**  | 20-40   | ~7ms    | Excellent    |
| **RTMO-m**      | One-stage | **200+** | 30-50   | ~5ms    | Excellent    |
| **RTMPose-m**   | Two-stage | 430      | 90      | ~15ms   | Good         |
| **RTMPose-s**   | Two-stage | 600      | 120     | ~10ms   | Good         |
| **MediaPipe**   | Two-stage | 30+      | 30+     | ~30ms   | Limited      |
| **YOLO11-Pose** | One-stage | 200+     | 30+     | ~10ms   | Excellent    |

### 3.2 One-Stage vs Two-Stage

```
TWO-STAGE (RTMPose, MediaPipe)
──────────────────────────────────────────────────────
Step 1: Detect all people in frame
        ┌─────────────────────────────┐
        │  Person Detector (RTMDet)   │  ~5-10ms
        └─────────────────────────────┘
                    │
                    ▼ N bounding boxes
Step 2: Run pose estimation on EACH person
        ┌─────────────────────────────┐
        │  Pose Model × N people      │  ~10ms × N
        └─────────────────────────────┘

Total: 5ms + (10ms × N people)
  1 person:  ~15ms
  3 people:  ~35ms
  6 people:  ~65ms  ← Slows down with more people!


ONE-STAGE (RTMO, YOLO-Pose)
──────────────────────────────────────────────────────
Single pass: Detect people AND poses simultaneously
        ┌─────────────────────────────┐
        │  RTMO (detection + pose)    │  ~7-15ms
        └─────────────────────────────┘

Total: ~7-15ms (constant regardless of people count!)
  1 person:  ~10ms
  3 people:  ~10ms
  6 people:  ~10ms  ← Constant time!
```

### 3.3 When to Use Each

| Scenario                | Recommended | Why                           |
| ----------------------- | ----------- | ----------------------------- |
| Single athlete analysis | RTMPose     | Maximum accuracy              |
| Multiple athletes       | **RTMO**    | Constant time, still accurate |
| Browser preview         | MediaPipe   | No server needed              |
| Mobile app              | MediaPipe   | Native SDKs                   |
| Server real-time        | **RTMO**    | Best speed/accuracy ratio     |
| Detailed analysis       | RTMPose     | Highest accuracy              |

______________________________________________________________________

## 4. RTMO: One-Stage Real-Time

### 4.1 What is RTMO?

**RTMO** (Real-Time Multi-Object) is a one-stage pose estimator from the same team as RTMPose, published at CVPR 2024.

**Key Innovation:** Integrates coordinate classification (SimCC) into a YOLO-style architecture, achieving:

- **74.8% AP** on COCO (comparable to two-stage RTMPose)
- **141 FPS** on V100 GPU
- **9x faster** than equivalent two-stage methods

### 4.2 RTMO Model Variants

| Model  | Input Size | AP (COCO) | FPS (V100) | Params | Use Case         |
| ------ | ---------- | --------- | ---------- | ------ | ---------------- |
| RTMO-s | 640×640    | 68.6%     | 250+       | 9M     | Mobile/edge      |
| RTMO-m | 640×640    | 73.2%     | 180+       | 20M    | Balanced         |
| RTMO-l | 640×640    | **74.8%** | **141**    | 45M    | Maximum accuracy |

### 4.3 RTMO vs RTMPose

| Aspect               | RTMPose-m      | RTMO-l               |
| -------------------- | -------------- | -------------------- |
| **Paradigm**         | Two-stage      | One-stage            |
| **COCO AP**          | 75.8%          | 74.8%                |
| **Speed (1 person)** | ~15ms          | ~7ms                 |
| **Speed (6 people)** | ~65ms          | **~7ms**             |
| **Multi-person**     | Slows down     | **Constant**         |
| **Best for**         | Single athlete | **Groups/real-time** |

### 4.4 RTMO in RTMLib

RTMLib includes RTMO models:

```python
from rtmlib import RTMO

# Initialize RTMO (one-stage)
rtmo = RTMO(
    onnx_model='rtmo-l',  # or 'rtmo-m', 'rtmo-s'
    backend='onnxruntime',
    device='cpu'  # or 'cuda', 'mps'
)

# Process frame - returns all people at once
keypoints, scores = rtmo(frame)
# keypoints: (num_people, 17, 2)
# scores: (num_people, 17)
```

______________________________________________________________________

## 5. Architecture Options

### 5.1 Option A: Browser-Only (Simplest)

```
┌─────────────────────────────────────────────────────────────┐
│                         BROWSER                              │
│  ┌──────────┐         ┌──────────────┐      ┌──────────┐   │
│  │  Webcam  │ ──────▶ │  MediaPipe   │ ───▶ │  Canvas  │   │
│  │  (WebRTC)│         │  (TF.js)     │      │ (render) │   │
│  └──────────┘         └──────────────┘      └──────────┘   │
│                                                             │
│  Latency: ~30-50ms | No server | Good accuracy             │
└─────────────────────────────────────────────────────────────┘
```

**Pros:**

- Zero server costs
- Lowest latency
- Works offline
- Privacy (data never leaves device)

**Cons:**

- Limited to MediaPipe accuracy
- Single-person optimized
- Struggles with motion blur

**Best for:** Camera setup preview, basic form feedback

### 5.2 Option B: Hybrid (Best Balance)

```
┌─────────────────────────────────────────────────────────────┐
│                         BROWSER                              │
│  ┌──────────┐         ┌──────────────┐      ┌──────────┐   │
│  │  Webcam  │ ──────▶ │  MediaPipe   │ ───▶ │ Preview  │   │
│  └──────────┘         │  (instant)   │      │ (30 FPS) │   │
│       │               └──────────────┘      └──────────┘   │
│       │                                                     │
│       │ Periodic frames (every 1-5 sec)                    │
│       ▼                                                     │
└───────┼─────────────────────────────────────────────────────┘
        │ HTTP/WebSocket
        ▼
┌─────────────────────────────────────────────────────────────┐
│                      BACKEND (Cloud Run)                     │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────┐    │
│  │   Receive    │ ──▶ │    RTMO/     │ ──▶ │  Return  │    │
│  │   Frame      │     │   RTMPose    │     │  Metrics │    │
│  └──────────────┘     └──────────────┘     └──────────┘    │
│                                                             │
│  Detailed analysis on keyframes                            │
└─────────────────────────────────────────────────────────────┘
```

**Pros:**

- Instant preview (MediaPipe)
- Detailed analysis when needed (RTMPose/RTMO)
- Lower server costs (periodic, not continuous)
- Best accuracy for metrics

**Cons:**

- More complex implementation
- Requires internet for detailed analysis

**Best for:** Live coaching with detailed feedback

### 5.3 Option C: Full Server-Side (Maximum Accuracy)

```
┌─────────────────────────────────────────────────────────────┐
│                         BROWSER                              │
│  ┌──────────┐                               ┌──────────┐   │
│  │  Webcam  │ ────────────────────────────▶ │  Render  │   │
│  └──────────┘                               │  Poses   │   │
│       │               ▲                     └──────────┘   │
│       │               │                           ▲        │
│       │ WebSocket     │ WebSocket                 │        │
│       │ (frames)      │ (poses)                   │        │
│       ▼               │                           │        │
└───────┼───────────────┼───────────────────────────┼────────┘
        │               │                           │
        ▼               │                           │
┌─────────────────────────────────────────────────────────────┐
│                      BACKEND (Cloud Run)                     │
│  ┌──────────┐     ┌──────────────┐     ┌──────────────┐    │
│  │  Decode  │ ──▶ │    RTMO      │ ──▶ │   Encode     │    │
│  │  Frame   │     │  (7-15ms)    │     │   Results    │────┘
│  └──────────┘     └──────────────┘     └──────────────┘
│                                                             │
│  Continuous real-time processing                           │
└─────────────────────────────────────────────────────────────┘
```

**Pros:**

- Maximum accuracy (RTMO/RTMPose)
- Consistent performance
- Multi-person support
- Advanced metrics

**Cons:**

- Higher latency (~50-100ms)
- Server costs (continuous)
- Requires good internet

**Best for:** Professional coaching, multi-athlete tracking

______________________________________________________________________

## 6. Implementation Examples

### 6.1 RTMLib Real-Time (Python/Backend)

```python
"""Real-time pose estimation server using RTMLib."""
import cv2
import time
import numpy as np
from dataclasses import dataclass
from typing import Iterator
from rtmlib import Body, RTMO


@dataclass
class PoseFrame:
    """Single frame with pose data."""
    timestamp: float
    keypoints: np.ndarray  # (num_people, 17, 2)
    scores: np.ndarray     # (num_people, 17)
    fps: float


class RealTimePoseEstimator:
    """Real-time pose estimation using RTMLib."""

    def __init__(
        self,
        mode: str = 'rtmo',  # 'rtmo' (fast) or 'rtmpose' (accurate)
        quality: str = 'balanced',
        device: str = 'cpu'
    ):
        """Initialize pose estimator.

        Args:
            mode: 'rtmo' for one-stage (fast), 'rtmpose' for two-stage (accurate)
            quality: 'lightweight', 'balanced', or 'performance'
            device: 'cpu', 'cuda', or 'mps'
        """
        if mode == 'rtmo':
            # One-stage: constant time regardless of people count
            self.model = RTMO(backend='onnxruntime', device=device)
        else:
            # Two-stage: more accurate, slows with more people
            self.model = Body(mode=quality, backend='onnxruntime', device=device)

        self.mode = mode
        self._fps_history: list[float] = []

    def process_frame(self, frame: np.ndarray) -> PoseFrame:
        """Process single frame and return poses."""
        start = time.perf_counter()

        keypoints, scores = self.model(frame)

        elapsed = time.perf_counter() - start
        fps = 1.0 / elapsed if elapsed > 0 else 0

        self._fps_history.append(fps)
        if len(self._fps_history) > 30:
            self._fps_history.pop(0)

        return PoseFrame(
            timestamp=time.time(),
            keypoints=keypoints,
            scores=scores,
            fps=sum(self._fps_history) / len(self._fps_history)
        )

    def process_webcam(self, camera_id: int = 0) -> Iterator[PoseFrame]:
        """Stream poses from webcam."""
        cap = cv2.VideoCapture(camera_id)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                yield self.process_frame(frame)

        finally:
            cap.release()


def draw_skeleton(
    frame: np.ndarray,
    keypoints: np.ndarray,
    scores: np.ndarray,
    threshold: float = 0.5
) -> np.ndarray:
    """Draw skeleton on frame."""
    # COCO skeleton connections
    SKELETON = [
        (0, 1), (0, 2), (1, 3), (2, 4),  # Head
        (5, 6), (5, 7), (7, 9), (6, 8), (8, 10),  # Arms
        (5, 11), (6, 12), (11, 12),  # Torso
        (11, 13), (13, 15), (12, 14), (14, 16)  # Legs
    ]

    output = frame.copy()

    for person_kpts, person_scores in zip(keypoints, scores):
        # Draw keypoints
        for i, (kpt, score) in enumerate(zip(person_kpts, person_scores)):
            if score > threshold:
                x, y = int(kpt[0]), int(kpt[1])
                cv2.circle(output, (x, y), 4, (0, 255, 0), -1)

        # Draw skeleton
        for i, j in SKELETON:
            if person_scores[i] > threshold and person_scores[j] > threshold:
                pt1 = tuple(map(int, person_kpts[i]))
                pt2 = tuple(map(int, person_kpts[j]))
                cv2.line(output, pt1, pt2, (0, 255, 255), 2)

    return output


# Usage example
if __name__ == '__main__':
    estimator = RealTimePoseEstimator(mode='rtmo', device='cpu')

    for pose_frame in estimator.process_webcam():
        # Here you would send pose_frame to frontend via WebSocket
        print(f"FPS: {pose_frame.fps:.1f}, People: {len(pose_frame.keypoints)}")
```

### 6.2 MediaPipe Browser Real-Time (TypeScript/React)

```typescript
// real-time-pose.tsx
import { useEffect, useRef, useState, useCallback } from 'react';
import {
  PoseLandmarker,
  FilesetResolver,
  DrawingUtils
} from '@mediapipe/tasks-vision';

interface PoseResults {
  landmarks: Array<Array<{ x: number; y: number; z: number; visibility: number }>>;
  worldLandmarks: Array<Array<{ x: number; y: number; z: number; visibility: number }>>;
}

export function useRealTimePose() {
  const [poseLandmarker, setPoseLandmarker] = useState<PoseLandmarker | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [fps, setFps] = useState(0);
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const lastTimeRef = useRef(0);
  const fpsHistoryRef = useRef<number[]>([]);

  // Initialize MediaPipe
  useEffect(() => {
    async function init() {
      const vision = await FilesetResolver.forVisionTasks(
        'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@latest/wasm'
      );

      const landmarker = await PoseLandmarker.createFromOptions(vision, {
        baseOptions: {
          modelAssetPath:
            'https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task',
          delegate: 'GPU'
        },
        runningMode: 'VIDEO',
        numPoses: 1,
        minPoseDetectionConfidence: 0.5,
        minPosePresenceConfidence: 0.5,
        minTrackingConfidence: 0.5
      });

      setPoseLandmarker(landmarker);
      setIsLoading(false);
    }

    init();
  }, []);

  // Start webcam
  const startWebcam = useCallback(async () => {
    if (!videoRef.current) return;

    const stream = await navigator.mediaDevices.getUserMedia({
      video: {
        width: { ideal: 640 },
        height: { ideal: 480 },
        frameRate: { ideal: 30 }
      }
    });

    videoRef.current.srcObject = stream;
    await videoRef.current.play();
  }, []);

  // Process frame
  const processFrame = useCallback((timestamp: number) => {
    if (!poseLandmarker || !videoRef.current || !canvasRef.current) {
      requestAnimationFrame(processFrame);
      return;
    }

    const video = videoRef.current;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');

    if (!ctx || video.readyState < 2) {
      requestAnimationFrame(processFrame);
      return;
    }

    // Calculate FPS
    if (lastTimeRef.current > 0) {
      const currentFps = 1000 / (timestamp - lastTimeRef.current);
      fpsHistoryRef.current.push(currentFps);
      if (fpsHistoryRef.current.length > 30) {
        fpsHistoryRef.current.shift();
      }
      const avgFps = fpsHistoryRef.current.reduce((a, b) => a + b, 0) /
                     fpsHistoryRef.current.length;
      setFps(Math.round(avgFps));
    }
    lastTimeRef.current = timestamp;

    // Detect poses
    const results = poseLandmarker.detectForVideo(video, timestamp);

    // Draw results
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    if (results.landmarks.length > 0) {
      const drawingUtils = new DrawingUtils(ctx);

      for (const landmarks of results.landmarks) {
        drawingUtils.drawLandmarks(landmarks, {
          radius: 3,
          color: '#00FF00'
        });
        drawingUtils.drawConnectors(landmarks, PoseLandmarker.POSE_CONNECTIONS, {
          color: '#FFFF00',
          lineWidth: 2
        });
      }
    }

    // Draw FPS
    ctx.fillStyle = '#00FF00';
    ctx.font = '20px monospace';
    ctx.fillText(`FPS: ${fps}`, 10, 30);

    requestAnimationFrame(processFrame);
  }, [poseLandmarker, fps]);

  return {
    videoRef,
    canvasRef,
    isLoading,
    fps,
    startWebcam,
    processFrame
  };
}

// React component
export function RealTimePoseView() {
  const { videoRef, canvasRef, isLoading, fps, startWebcam, processFrame } =
    useRealTimePose();

  useEffect(() => {
    if (!isLoading) {
      startWebcam().then(() => {
        requestAnimationFrame(processFrame);
      });
    }
  }, [isLoading, startWebcam, processFrame]);

  return (
    <div className="relative">
      <video ref={videoRef} className="hidden" playsInline />
      <canvas
        ref={canvasRef}
        width={640}
        height={480}
        className="rounded-lg shadow-lg"
      />
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-black/50">
          <span className="text-white">Loading pose model...</span>
        </div>
      )}
    </div>
  );
}
```

### 6.3 WebSocket Streaming (Full Server-Side)

```python
# backend/realtime_server.py
"""WebSocket server for real-time pose streaming."""
import asyncio
import json
import base64
import cv2
import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from rtmlib import RTMO

app = FastAPI()

# Initialize model once
pose_model = RTMO(backend='onnxruntime', device='cpu')


def decode_frame(data: str) -> np.ndarray:
    """Decode base64 frame from client."""
    # Remove data URL prefix if present
    if ',' in data:
        data = data.split(',')[1]

    img_bytes = base64.b64decode(data)
    nparr = np.frombuffer(img_bytes, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return frame


def encode_results(keypoints: np.ndarray, scores: np.ndarray) -> dict:
    """Encode pose results for transmission."""
    return {
        'keypoints': keypoints.tolist(),
        'scores': scores.tolist(),
        'num_people': len(keypoints)
    }


@app.websocket('/ws/pose')
async def pose_websocket(websocket: WebSocket):
    """WebSocket endpoint for real-time pose estimation."""
    await websocket.accept()

    try:
        while True:
            # Receive frame from client
            data = await websocket.receive_text()
            message = json.loads(data)

            if message['type'] == 'frame':
                # Decode and process frame
                frame = decode_frame(message['data'])
                keypoints, scores = pose_model(frame)

                # Send results back
                results = encode_results(keypoints, scores)
                await websocket.send_json({
                    'type': 'pose',
                    'data': results,
                    'timestamp': message.get('timestamp', 0)
                })

    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"Error: {e}")
        await websocket.close()
```

```typescript
// frontend/websocket-pose-client.ts
/**
 * WebSocket client for real-time pose streaming to server.
 */
export class PoseStreamClient {
  private ws: WebSocket | null = null;
  private video: HTMLVideoElement;
  private canvas: HTMLCanvasElement;
  private isStreaming = false;
  private onPose: (poses: PoseResult) => void;

  constructor(
    video: HTMLVideoElement,
    canvas: HTMLCanvasElement,
    onPose: (poses: PoseResult) => void
  ) {
    this.video = video;
    this.canvas = canvas;
    this.onPose = onPose;
  }

  connect(url: string): Promise<void> {
    return new Promise((resolve, reject) => {
      this.ws = new WebSocket(url);

      this.ws.onopen = () => {
        console.log('Connected to pose server');
        resolve();
      };

      this.ws.onmessage = (event) => {
        const message = JSON.parse(event.data);
        if (message.type === 'pose') {
          this.onPose(message.data);
        }
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        reject(error);
      };

      this.ws.onclose = () => {
        console.log('Disconnected from pose server');
        this.isStreaming = false;
      };
    });
  }

  startStreaming(targetFps: number = 15): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      throw new Error('WebSocket not connected');
    }

    this.isStreaming = true;
    const interval = 1000 / targetFps;

    const sendFrame = () => {
      if (!this.isStreaming) return;

      const ctx = this.canvas.getContext('2d');
      if (!ctx) return;

      // Draw video frame to canvas
      ctx.drawImage(this.video, 0, 0, this.canvas.width, this.canvas.height);

      // Encode as JPEG (smaller than PNG)
      const dataUrl = this.canvas.toDataURL('image/jpeg', 0.8);

      // Send to server
      this.ws?.send(JSON.stringify({
        type: 'frame',
        data: dataUrl,
        timestamp: Date.now()
      }));

      setTimeout(sendFrame, interval);
    };

    sendFrame();
  }

  stopStreaming(): void {
    this.isStreaming = false;
  }

  disconnect(): void {
    this.stopStreaming();
    this.ws?.close();
    this.ws = null;
  }
}

interface PoseResult {
  keypoints: number[][][];  // [person][keypoint][x,y]
  scores: number[][];       // [person][keypoint]
  num_people: number;
}
```

______________________________________________________________________

## 7. Latency Optimization

### 7.1 Model Selection

| Priority | Model Choice       | Expected Latency |
| -------- | ------------------ | ---------------- |
| Speed    | RTMO-s             | ~5ms             |
| Balance  | RTMO-m / RTMPose-s | ~7-10ms          |
| Accuracy | RTMPose-m          | ~15ms            |

### 7.2 Resolution Trade-offs

| Resolution | Speed    | Accuracy | Use Case             |
| ---------- | -------- | -------- | -------------------- |
| 320×240    | Fastest  | Lower    | Preview only         |
| 640×480    | Balanced | Good     | **Recommended**      |
| 1280×720   | Slower   | Better   | High-detail analysis |

### 7.3 Skip-Frame Strategy

For video analysis where not every frame needs processing:

```python
def process_with_skip(video_path: str, skip_frames: int = 2):
    """Process every Nth frame for faster throughput."""
    cap = cv2.VideoCapture(video_path)
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        if frame_count % (skip_frames + 1) != 0:
            continue

        # Process this frame
        keypoints, scores = model(frame)
        yield keypoints, scores

    cap.release()
```

### 7.4 Async Processing

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=2)

async def process_frame_async(frame: np.ndarray) -> tuple:
    """Run pose estimation in thread pool."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, model, frame)
```

______________________________________________________________________

## 8. Recommended Strategy for kinemotion

### 8.1 Phase-Based Approach

```
PHASE 1: MVP (Current)
────────────────────────────────────────────────
• Video upload → Backend analysis → Results
• No real-time needed
• Focus: Validate accuracy with coaches

PHASE 2: Camera Preview (If Requested)
────────────────────────────────────────────────
• MediaPipe in browser
• "Is my camera angle correct?"
• "Am I fully in frame?"
• Zero latency, no server cost
• Implementation: ~2-3 days

PHASE 3: Live Feedback (If Coaches Want It)
────────────────────────────────────────────────
Option A: Browser-Only
  • MediaPipe for everything
  • ~30ms latency
  • Good enough for basic feedback
  • Implementation: ~1 week

Option B: Hybrid (Recommended)
  • MediaPipe for instant preview
  • Backend (RTMO) for detailed metrics
  • Best accuracy where it matters
  • Implementation: ~2 weeks

Option C: Full Server-Side
  • RTMO via WebSocket
  • ~50-100ms latency
  • Maximum accuracy
  • Higher server costs
  • Implementation: ~2-3 weeks
```

### 8.2 Decision Framework

```
┌─────────────────────────────────────────────────────────────┐
│              DO COACHES WANT REAL-TIME FEEDBACK?            │
└─────────────────────────────────────────────────────────────┘
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
           NO                          YES
           │                            │
           ▼                            ▼
    Keep current              What kind of feedback?
    upload → analyze                    │
    workflow                 ┌──────────┴──────────┐
                             ▼                     ▼
                        Basic                  Detailed
                        (form check)           (metrics)
                             │                     │
                             ▼                     ▼
                      MediaPipe               Hybrid or
                      browser-only            server-side
```

### 8.3 Implementation Priority

1. **First:** Add MediaPipe preview during video recording

   - Helps users position camera correctly
   - Shows if they're in frame
   - No backend changes needed

1. **If needed:** Add hybrid real-time

   - MediaPipe preview + periodic RTMO analysis
   - Best balance of UX and accuracy

1. **Only if demanded:** Full server-side streaming

   - WebSocket infrastructure
   - Higher operational complexity

______________________________________________________________________

## 9. References

### Papers

1. **RTMO (CVPR 2024):** Lu, P., et al. "RTMO: Towards High-Performance One-Stage Real-Time Multi-Person Pose Estimation." arXiv:2312.07526

1. **RTMPose (2023):** Jiang, T., et al. "RTMPose: Real-Time Multi-Person Pose Estimation based on MMPose." arXiv:2303.07399

1. **MediaPipe BlazePose (2020):** Bazarevsky, V., et al. "BlazePose: On-device Real-time Body Pose Tracking." arXiv:2006.10204

### Code & Libraries

- **RTMLib:** https://github.com/Tau-J/rtmlib
- **MMPose:** https://github.com/open-mmlab/mmpose
- **MediaPipe:** https://developers.google.com/mediapipe
- **MediaPipe Tasks Vision (JS):** https://www.npmjs.com/package/@mediapipe/tasks-vision

### Related Documentation

- [RTMPose vs RTMLib vs MediaPipe Comparison](../research/rtmpose-rtmlib-mediapipe-comparison.md)
- [Pose Estimator Comparison 2025](../research/pose-estimator-comparison-2025.md)
- [Pose Systems Quick Reference](../reference/pose-systems.md)

______________________________________________________________________

**Document History:**

- December 21, 2025: Initial comprehensive guide
