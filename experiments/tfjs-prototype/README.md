# TF.js Pose Detection Prototype

## Goal

To evaluate the feasibility and performance of client-side pose estimation using TensorFlow.js and MediaPipe.

## Tech Stack

- **Framework**: Vite + TypeScript
- **ML Library**: TensorFlow.js (WebGPU, WebGL, WASM)
- **Model**: MediaPipe BlazePose (Full)

## How to Run

1. **Install dependencies**:

   ```bash
   cd experiments/tfjs-prototype
   yarn install
   ```

2. **Start Dev Server**:

   ```bash
   yarn dev
   ```

3. **Open Browser**:
   Navigate to the URL shown (usually `http://localhost:5173`).
   **Note**: For WebGPU support, use Chrome/Edge 113+ or similar modern browsers.

## Features

- **Auto-Backend Selection**: Tries WebGPU → WebGL → WASM.
- **Real-time Stats**: Displays current backend and FPS.
- **Visuals**: Overlays skeleton on the video feed.

## Build

```bash
yarn build
```

Builds to `dist/` with chunk splitting for optimal loading.
