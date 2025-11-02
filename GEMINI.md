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
- **Development**: `pytest`, `black`, `ruff`, `mypy`.

### Development Commands

- **Run CLI**: `uv run kinemotion dropjump-analyze <video_path>`
- **Install/Sync Dependencies**: `uv sync`
- **Run Tests**: `uv run pytest`
- **Format Code**: `uv run black src/`
- **Lint Code**: `uv run ruff check`
- **Auto-fix Linting**: `uv run ruff check --fix`
- **Type Check**: `uv run mypy src/kinemotion`
- **Run All Checks**: `uv run ruff check && uv run mypy src/kinemotion && uv run pytest`

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

1. **Pose Tracking** (`core/pose.py`): Extracts 13 body landmarks per frame using MediaPipe.
1. **Center of Mass (CoM) Estimation** (`core/pose.py`): Optional, more accurate tracking using a biomechanical model.
1. **Smoothing** (`core/smoothing.py`): A Savitzky-Golay filter reduces jitter.
1. **Contact Detection** (`dropjump/analysis.py`): Analyzes vertical velocity to determine ground contact vs. flight.
1. **Phase Identification**: Finds continuous ground contact and flight periods.
1. **Sub-Frame Interpolation** (`dropjump/analysis.py`): Estimates exact transition times between frames using linear interpolation on the velocity curve, improving timing precision significantly.
1. **Trajectory Curvature Analysis** (`dropjump/analysis.py`): Refines transition timing by detecting acceleration spikes (e.g., landing impact).
1. **Metrics Calculation** (`dropjump/kinematics.py`): Calculates ground contact time, flight time, and jump height.
1. **Output**: Provides metrics in JSON format and an optional debug video.

## Critical Implementation Details

### 1. Aspect Ratio Preservation & SAR Handling (`core/video_io.py`)

- **CRITICAL**: The tool must preserve the source video's exact aspect ratio, including Sample Aspect Ratio (SAR) from mobile videos.
- **DO**: Get frame dimensions from the first actual frame read from the video (`frame.shape[:2]`), not from `cv2.CAP_PROP_*` properties, which can be wrong for rotated videos.
- **DO**: Use `ffprobe` to extract SAR and calculate correct display dimensions.
- The `DebugOverlayRenderer` uses these display dimensions for the output video.

### 2. Sub-Frame Interpolation (`dropjump/analysis.py`)

- **CRITICAL**: Timing precision is achieved by interpolating between frames.
- **Velocity Calculation**: Velocity is computed as the **first derivative of the smoothed position trajectory** using a Savitzky-Golay filter (`savgol_filter(..., deriv=1)`). This is much smoother and more accurate than simple frame-to-frame differences.
- **Interpolation**: When velocity crosses the contact threshold between two frames, linear interpolation is used to find the fractional frame index of the crossing. This improves timing accuracy from ~33ms to ~10ms at 30fps.

### 3. Trajectory Curvature Analysis (`dropjump/analysis.py`)

- **CRITICAL**: Event timing is further refined using acceleration patterns.
- **Acceleration Calculation**: Acceleration is the **second derivative of the smoothed position** (`savgol_filter(..., deriv=2)`).
- **Event Detection**:
  - **Landing**: A large acceleration spike (impact deceleration).
  - **Takeoff**: A sharp change in acceleration.
- **Blending**: The final transition time is a weighted blend: 70% from the curvature-based estimate and 30% from the velocity-based estimate. This is enabled by default via `--use-curvature`.

### 4. JSON Serialization of NumPy Types (`dropjump/kinematics.py`)

- **CRITICAL**: Standard `json.dump` cannot serialize NumPy integer types (e.g., `np.int64`).
- **DO**: Explicitly cast all NumPy numbers to standard Python types (`int()`, `float()`) within the `to_dict()` methods of data classes before serialization.

### 5. OpenCV Frame Dimensions

- **CRITICAL**: Be aware of dimension ordering differences.
- **NumPy `frame.shape`**: `(height, width, channels)`
- **OpenCV `cv2.VideoWriter()` size**: `(width, height)`
- Always pass dimensions to OpenCV functions in `(width, height)` order.

## Code Quality & Workflow

When contributing code, strictly adhere to the project's quality standards.

1. **Format Code**: `uv run black src/`
1. **Lint and Fix**: `uv run ruff check --fix`
1. **Type Check**: `uv run mypy src/kinemotion`
1. **Run Tests**: `uv run pytest`

**Run all checks before committing**: `uv run ruff check && uv run mypy src/kinemotion && uv run pytest`

- **Type Safety**: The project uses `mypy` in strict mode. All functions must have full type annotations.
- **Linting**: `ruff` is used for linting. Configuration is in `pyproject.toml`.
- **Formatting**: `black` is used for code formatting.

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
