# GEMINI.md

This file provides guidance to the Gemini model when working with code in this repository.

## Repository Purpose

Kinemotion is a video-based kinematic analysis tool for athletic performance. It analyzes drop-jump videos to estimate ground contact time, flight time, and jump height. The analysis is done by tracking an athlete's movement using MediaPipe pose tracking and applying advanced kinematic calculations. It supports both traditional foot-based tracking and a more accurate center of mass (CoM) tracking.

**IMPORTANT**: The tool's accuracy has not been validated against gold-standard measurements. Any accuracy claims are theoretical.

## Project Setup

### Dependencies

The project uses `uv` for dependency management and `asdf` for Python version management.

- **Python Version**: 3.12.7 (specified in `.tool-versions`). MediaPipe requires Python \<= 3.12.
- **Install Dependencies**: `uv sync`

**Key Libraries:**

- **Production**: `click`, `opencv-python`, `mediapipe`, `numpy`, `scipy`.
- **Development**: `pytest`, `ruff`, `pyright`.

### Development Commands

- **Run CLI**: `uv run kinemotion dropjump-analyze <video_path>`
- **Install/Sync Dependencies**: `uv sync`
- **Run Tests**: `uv run pytest`
- **Format Code**: `uv run ruff format .`
- **Lint Code**: `uv run ruff check`
- **Auto-fix Linting**: `uv run ruff check --fix`
- **Type Check**: `uv run pyright`
- **Run All Checks**: `uv run ruff check && uv run pyright && uv run pytest`

## Architecture

### Module Structure

```text
src/kinemotion/
├── cli.py              # Main CLI entry point
├── core/               # Shared functionality (pose, smoothing, filtering, video_io)
└── dropjump/           # Drop jump specific analysis (cli, analysis, kinematics, debug_overlay)
tests/                  # Unit and integration tests
docs/                   # Documentation (PARAMETERS.md is key)
```

- `core/` contains reusable code for different jump types.
- `dropjump/` contains logic specific to drop jumps.
- The main `cli.py` registers subcommands from modules like `dropjump/cli.py`.

### Analysis Pipeline

#### Drop Jump Analysis

1. **Pose Tracking** (`core/pose.py`): Extracts 13 body landmarks per frame using MediaPipe.
1. **Smoothing** (`core/smoothing.py`): Savitzky-Golay filter for noise reduction.
1. **Contact Detection** (`dropjump/analysis.py`): Velocity-based ground contact detection.
1. **Sub-Frame Interpolation**: Linear interpolation for precise timing.
1. **Trajectory Curvature**: Acceleration-based refinement.
1. **Metrics**: RSI, contact time, jump height.

#### CMJ Analysis (`cmj/analysis.py`)

1. **Strategy**: Uses a **backward search** algorithm starting from the jump peak.
1. **Signed Velocity**: Calculates signed velocity (negative=up, positive=down) to distinguish concentric/eccentric phases.
1. **Phase Detection Sequence**:
   - **Peak Height**: Global minimum y-position.
   - **Takeoff**: Peak *negative* velocity (max upward speed) found by searching backward from peak.
   - **Lowest Point**: Maximum y-position found by searching backward from takeoff.
   - **Landing**: Maximum *positive* acceleration (impact) found by searching forward from peak.
   - **Standing End**: Detected via acceleration thresholds searching backward from lowest point.

## Critical Implementation Details

### 1. Aspect Ratio, Rotation & SAR Handling (`core/video_io.py`)

- **CRITICAL**: The tool must preserve the source video's exact aspect ratio and orientation.
- **FFmpeg/FFprobe**: The `VideoProcessor` class relies on `ffprobe` to extract:
  - **Rotation**: Metadata often ignored by OpenCV (common in mobile videos).
  - **SAR (Sample Aspect Ratio)**: Non-square pixel data.
- **Fallback**: If `ffprobe` is missing, a warning is issued, and defaults are used.
- **DO**: Always use `frame.shape[:2]` from an actual read frame for dimensions, not `cv2.CAP_PROP_*`.

### 2. Internal Physics Validation (`scripts/validate_known_heights.py`)

- **Context**: While clinical validation is pending, the tool undergoes rigorous **internal physics validation**.
- **Methodology**: Objects are dropped from known heights (0.5m, 1.0m, 1.5m). Measured flight times are compared against theoretical physics predictions ($t = \\sqrt{2h/g}$).
- **Passing Criteria**:
  - **MAE**: \< 20ms
  - **RMSE**: \< 30ms
  - **Correlation**: > 0.99

### 3. Sub-Frame Interpolation & Robust Derivatives (`dropjump/analysis.py`, `core/smoothing.py`)

- **CRITICAL**: Timing precision is achieved by interpolating between frames.
- **Velocity/Acceleration Calculation**: Velocity is computed as the **first derivative** and acceleration as the **second derivative** of the smoothed position trajectory using a Savitzky-Golay filter (`savgol_filter(..., deriv=1)` and `deriv=2`). This approach is highly robust and accurate, minimizing noise amplification compared to simple finite-difference methods.
- **Interpolation**: When velocity crosses the contact threshold between two frames, linear interpolation is used to find the fractional frame index of the crossing. This improves timing accuracy from ~33ms to ~10ms at 30fps.

### 4. Trajectory Curvature Analysis (`dropjump/analysis.py`)

- **CRITICAL**: Event timing is further refined using acceleration patterns.
- **Acceleration Calculation**: Acceleration is the **second derivative of the smoothed position** (`savgol_filter(..., deriv=2)`).
- **Event Detection**:
  - **Landing**: A large acceleration spike (impact deceleration).
  - **Takeoff**: A sharp change in acceleration.
- **Blending**: The final transition time is a weighted blend: 70% from the curvature-based estimate and 30% from the velocity-based estimate. This is enabled by default via `--use-curvature`.

### 5. Adaptive Velocity Threshold (`dropjump/analysis.py`)

- **INSIGHT**: The `calculate_adaptive_threshold` function is implemented but currently *not integrated* into the main analysis pipeline.
- **PURPOSE**: This feature dynamically adjusts the `velocity_threshold` based on baseline noise characteristics of the video. This can significantly improve robustness across varying camera distances, lighting conditions, and video quality by making contact detection less sensitive to noise and more resilient to false positives/negatives.
- **STATUS**: Awaiting CLI integration. Its inclusion would enhance the tool's adaptability without manual parameter tuning.

### 6. JSON Serialization of NumPy Types (`dropjump/kinematics.py`)

- **CRITICAL**: Standard `json.dump` cannot serialize NumPy integer types (e.g., `np.int64`).
- **DO**: Explicitly cast all NumPy numbers to standard Python types (`int()`, `float()`) within the `to_dict()` methods of data classes before serialization.

### 7. OpenCV Frame Dimensions

- **CRITICAL**: Be aware of dimension ordering differences.
- **NumPy `frame.shape`**: `(height, width, channels)`
- **OpenCV `cv2.VideoWriter()` size**: `(width, height)`
- Always pass dimensions to OpenCV functions in `(width, height)` order.

## Code Quality & Workflow

**CRITICAL**: Never commit code that fails sanity checks. Always run `ruff`, `pyright`, and `pytest` locally before committing.

When contributing code, strictly adhere to the project's quality standards.

1. **Format Code**: `uv run ruff format .`
1. **Lint and Fix**: `uv run ruff check --fix`
1. **Type Check**: `uv run pyright`
1. **Run Tests**: `uv run pytest`

**Run all checks before committing**: `uv run ruff check && uv run pyright && uv run pytest`

- **Type Safety**: The project uses `pyright` in strict mode. All functions must have full type annotations.
- **Linting**: `ruff` is used for linting. Configuration is in `pyproject.toml`.
- **Formatting**: `ruff` is used for code formatting.

## Common Development Tasks

- **Adding New Metrics**:
  1. Update `DropJumpMetrics` in `dropjump/kinematics.py`.
  1. Add calculation logic in `calculate_drop_jump_metrics()`.
  1. Update `to_dict()` method (remember to cast NumPy types).
  1. (Optional) Add visualization in `DebugOverlayRenderer`.
  1. Add tests in `tests/test_kinematics.py`.
- **Modifying Contact Detection**: Edit `detect_ground_contact()` in `dropjump/analysis.py`.
- **Adjusting Smoothing**: Modify `smooth_landmarks()` in `core/smoothing.py`.

## Parameter Tuning

A comprehensive guide to all CLI parameters is in `docs/PARAMETERS.md`. Refer to it for detailed explanations.

**Key `dropjump-analyze` parameters:**

- `--smoothing-window`: Controls trajectory smoothness. Increase for noisy video.
- `--polyorder`: Polynomial order for smoothing. `2` is ideal for jump physics.
- `--velocity-threshold`: Contact sensitivity. Decrease to detect shorter contacts.
- `--min-contact-frames`: Temporal filter. Increase to remove false contacts.
- `--drop-height`: **Important for accuracy.** Calibrates jump height using a known box height in meters.
- `--use-curvature`: Enables acceleration-based timing refinement (default: True).
- `--outlier-rejection`: Removes tracking glitches before smoothing (default: True).
- `--bilateral-filter`: Experimental edge-preserving smoothing alternative to Savitzky-Golay.

## Testing

- **Run all tests**: `uv run pytest`
- **Run a specific test file**: `uv run pytest tests/test_contact_detection.py -v`
- The project has comprehensive test coverage for core functionalities like aspect ratio, contact detection, CoM estimation, and kinematics.

## CLI Usage Examples

```bash
# Get help for the dropjump command
uv run kinemotion dropjump-analyze --help

# Basic analysis, print JSON to stdout
uv run kinemotion dropjump-analyze video.mp4

# Full analysis: generate debug video, save metrics, and use calibration
uv run kinemotion dropjump-analyze video.mp4 \
  --output debug_video.mp4 \
  --json-output metrics.json \
  --drop-height 0.40
```
