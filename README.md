# Kinemotion

[![PyPI version](https://badge.fury.io/py/kinemotion.svg)](https://badge.fury.io/py/kinemotion)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

A video-based kinematic analysis tool for athletic performance. Analyzes side-view drop-jump videos to estimate key performance metrics: ground contact time, flight time, and jump height. Uses MediaPipe pose tracking and advanced kinematics.

## Features

- **Automatic pose tracking** using MediaPipe Pose landmarks
- **Ground contact detection** based on foot velocity and position
- **Derivative-based velocity** - smooth velocity calculation from position trajectory
- **Trajectory curvature analysis** - acceleration patterns for refined event detection
- **Sub-frame interpolation** - precise timing beyond frame boundaries for improved accuracy
- **Automatic drop jump detection** - identifies box → drop → landing → jump phases
- **Kinematic calculations** for jump metrics:
  - Ground contact time (ms)
  - Flight time (ms)
  - Jump height (m) - with optional calibration using drop box height
- **Calibrated measurements** - use known drop height for theoretically improved accuracy (⚠️ accuracy claims unvalidated)
- **JSON output** for easy integration with other tools
- **Optional debug video** with visual overlays showing contact states and landmarks
- **Configurable parameters** for smoothing, thresholds, and detection

**Note**: Drop jump analysis uses foot-based tracking with fixed velocity thresholds. Center of mass (CoM) tracking and adaptive thresholding (available in `core/` modules) require longer videos (~5+ seconds) with a 3-second standing baseline, making them unsuitable for typical drop jump videos (~3 seconds). These features may be available in future jump types like CMJ (countermovement jump).

## Validation Status

⚠️ **IMPORTANT**: This tool's accuracy has **not been validated** against gold standard measurements (force plates, 3D motion capture). All accuracy claims and improvement estimates are theoretical and based on algorithmic considerations, not empirical testing.

The tool provides consistent measurements and may be useful for:

- Tracking relative changes in an individual athlete over time
- Comparing similar jumps under controlled conditions
- Exploratory analysis and research

For clinical, research, or performance assessment requiring validated accuracy, this tool should be compared against validated measurement systems before use.

## Setup

### Prerequisites

- [asdf](https://asdf-vm.com/) version manager
- asdf plugins for Python and uv

### Installation

1. **Install asdf plugins** (if not already installed):

```bash
asdf plugin add python
asdf plugin add uv
```

1. **Install versions specified in `.tool-versions`**:

```bash
asdf install
```

1. **Install project dependencies using uv**:

```bash
uv sync
```

This will install all dependencies and make the `kinemotion` command available.

## Usage

### Basic Analysis

Analyze a video and output metrics to stdout as JSON:

```bash
kinemotion dropjump-analyze video.mp4
```

### Save Metrics to File

```bash
kinemotion dropjump-analyze video.mp4 --json-output metrics.json
```

### Generate Debug Video

Create an annotated video showing pose tracking and contact detection:

```bash
kinemotion dropjump-analyze video.mp4 --output debug.mp4
```

### Calibrated Drop Jump Analysis

For most accurate measurements, provide the drop box height in meters:

```bash
# 40cm drop box
kinemotion dropjump-analyze drop-jump.mp4 --drop-height 0.40

# 60cm drop box with full outputs
kinemotion dropjump-analyze drop-jump.mp4 \
  --drop-height 0.60 \
  --json-output metrics.json \
  --output debug.mp4
```

### Full Example (Maximum Accuracy)

```bash
# With all accuracy improvements enabled
kinemotion dropjump-analyze jump.mp4 \
  --outlier-rejection \
  --drop-height 0.40 \
  --output debug.mp4 \
  --json-output results.json \
  --smoothing-window 7 \
  --polyorder 3

# Alternative: With experimental bilateral filter
kinemotion dropjump-analyze jump.mp4 \
  --outlier-rejection \
  --bilateral-filter \
  --drop-height 0.40 \
  --output debug.mp4 \
  --json-output results.json
```

## Configuration Options

> **📖 For detailed explanations of all parameters, see [docs/PARAMETERS.md](docs/PARAMETERS.md)**
>
> This section provides a quick reference. The full guide includes:
>
> - How each parameter works internally
> - When and why to adjust them
> - Scenario-based recommendations
> - Debugging workflows
> - Parameter interaction effects

### Smoothing

- `--smoothing-window <int>` (default: 5)
  - Window size for Savitzky-Golay smoothing filter
  - Must be odd and >= 3
  - Larger values = smoother trajectories but less responsive
  - **Tip**: Increase for noisy videos, decrease for high-quality stable footage

- `--polyorder <int>` (default: 2)
  - Polynomial order for Savitzky-Golay smoothing filter
  - Must be < smoothing-window (typically 2 or 3)
  - 2 = quadratic fit (good for parabolic motion like jumps)
  - 3 = cubic fit (better for complex motion patterns)
  - Higher order captures more motion complexity but more sensitive to noise
  - **Tip**: Use 2 for most cases, try 3 for high-quality videos with complex motion
  - **Accuracy improvement**: +1-2% for complex motion patterns

### Advanced Filtering

- `--outlier-rejection / --no-outlier-rejection` (default: --outlier-rejection)
  - Apply RANSAC and median-based outlier rejection to remove tracking glitches
  - **With outlier rejection** (`--outlier-rejection`): Detects and removes MediaPipe tracking errors
    - RANSAC-based polynomial fitting identifies positions that deviate from smooth trajectory
    - Median filtering catches spikes in otherwise smooth motion
    - Outliers replaced with interpolated values from neighboring valid points
    - Removes jumps, jitter, and temporary tracking losses
    - **Accuracy improvement**: +1-2% by eliminating tracking glitches
  - **Without outlier rejection** (`--no-outlier-rejection`): Uses raw tracked positions
    - Faster processing, relies entirely on MediaPipe quality
  - **Tip**: Keep enabled (default) unless debugging or working with perfect tracking

- `--bilateral-filter / --no-bilateral-filter` (default: --no-bilateral-filter)
  - Use bilateral temporal filter for edge-preserving smoothing
  - **With bilateral filter** (`--bilateral-filter`): Preserves sharp transitions while smoothing noise
    - Weights each frame by temporal distance AND position similarity
    - Landing/takeoff transitions remain sharp (not smoothed away)
    - Noise in smooth regions (flight, ground contact) is reduced
    - Edge-preserving alternative to Savitzky-Golay smoothing
    - **Accuracy improvement**: +1-2% by preserving event timing precision
  - **Without bilateral filter** (`--no-bilateral-filter`): Uses standard Savitzky-Golay smoothing
    - Uniform smoothing across all frames
    - Well-tested baseline method
  - **Tip**: Experimental feature; enable for videos with rapid transitions or variable motion
  - **Note**: Cannot be used simultaneously with Savitzky-Golay; bilateral replaces it when enabled

### Contact Detection

- `--velocity-threshold <float>` (default: 0.02)
  - Vertical velocity threshold for detecting stationary feet
  - In normalized coordinates (0-1 range)
  - Lower values = more sensitive (may detect false contacts)
  - Higher values = less sensitive (may miss brief contacts)
  - **Tip**: Start with default, decrease if missing contacts, increase if detecting false contacts

- `--min-contact-frames <int>` (default: 3)
  - Minimum consecutive frames to confirm ground contact
  - Filters out momentary tracking glitches
  - **Tip**: Increase for noisy videos with jittery tracking

### Visibility

- `--visibility-threshold <float>` (default: 0.5)
  - Minimum MediaPipe visibility score (0-1) to trust a landmark
  - Higher values require more confident tracking
  - **Tip**: Lower if landmarks are frequently obscured but tracking seems reasonable

### Pose Tracking

- `--detection-confidence <float>` (default: 0.5)
  - MediaPipe pose detection confidence threshold
  - **Tip**: Increase if getting false pose detections

- `--tracking-confidence <float>` (default: 0.5)
  - MediaPipe pose tracking confidence threshold
  - **Tip**: Increase if tracking is jumping between different people/objects

### Calibration

- `--drop-height <float>` (optional)
  - Height of drop box/platform in meters (e.g., 0.40 for 40cm)
  - Enables calibrated jump height measurement using known drop height
  - Theoretically improves accuracy (⚠️ unvalidated - requires empirical validation)
  - Only applicable for drop jumps (box → drop → landing → jump)
  - **Tip**: Measure your box height accurately for best results

### Trajectory Analysis

- `--use-curvature / --no-curvature` (default: --use-curvature)
  - Enable/disable trajectory curvature analysis for refining transitions
  - **With curvature** (`--use-curvature`): Uses acceleration patterns to refine event timing
    - Landing detection: Finds acceleration spike from impact deceleration
    - Takeoff detection: Finds acceleration change as body transitions from static to upward motion
    - Blends curvature-based refinement (70%) with velocity-based estimate (30%)
    - Provides physics-based validation of velocity threshold crossings
    - **Accuracy improvement**: More precise timing, especially for rapid transitions
  - **Without curvature** (`--no-curvature`): Pure velocity-based detection with sub-frame interpolation
    - Simpler, faster algorithm
    - Still highly accurate with smooth velocity curves
  - **Tip**: Keep enabled (default) for best results; disable only for debugging or comparison

## Output Format

### JSON Metrics

```json
{
  "ground_contact_time_ms": 245.67,
  "flight_time_ms": 456.78,
  "jump_height_m": 0.339,
  "jump_height_kinematic_m": 0.256,
  "jump_height_trajectory_normalized": 0.0845,
  "contact_start_frame": 45,
  "contact_end_frame": 67,
  "flight_start_frame": 68,
  "flight_end_frame": 95,
  "peak_height_frame": 82
}
```

**Fields**:

- `jump_height_m`: Primary jump height measurement (calibrated if --drop-height provided, otherwise corrected kinematic)
- `jump_height_kinematic_m`: Kinematic estimate from flight time: h = (g × t²) / 8
- `jump_height_trajectory_normalized`: Position-based measurement in normalized coordinates (0-1 range)
- `contact_start_frame_precise`, `contact_end_frame_precise`: Sub-frame timing (fractional frames)
- `flight_start_frame_precise`, `flight_end_frame_precise`: Sub-frame timing (fractional frames)

**Note**: Integer frame indices (e.g., `contact_start_frame`) are provided for visualization in debug videos. Precise fractional frames (e.g., `contact_start_frame_precise`) are used for all timing calculations and provide higher accuracy.

### Debug Video

The debug video includes:

- **Green circle**: Average foot position when on ground
- **Red circle**: Average foot position when in air
- **Yellow circles**: Individual foot landmarks (ankles, heels)
- **State indicator**: Current contact state (on_ground/in_air)
- **Phase labels**: "GROUND CONTACT" and "FLIGHT PHASE" during relevant periods
- **Peak marker**: "PEAK HEIGHT" at maximum jump height
- **Frame number**: Current frame index

## Troubleshooting

### Poor Tracking Quality

**Symptoms**: Erratic landmark positions, missing detections, incorrect contact states

**Solutions**:

1. **Check video quality**: Ensure the athlete is clearly visible in profile view
2. **Increase smoothing**: Use `--smoothing-window 7` or higher
3. **Adjust detection confidence**: Try `--detection-confidence 0.6` or `--tracking-confidence 0.6`
4. **Generate debug video**: Use `--output` to visualize what's being tracked

### No Pose Detected

**Symptoms**: "No frames processed" error or all null landmarks

**Solutions**:

1. **Verify video format**: OpenCV must be able to read the video
2. **Check framing**: Ensure full body is visible in side view
3. **Lower confidence thresholds**: Try `--detection-confidence 0.3 --tracking-confidence 0.3`
4. **Test video playback**: Verify video opens correctly with standard video players

### Incorrect Contact Detection

**Symptoms**: Wrong ground contact times, flight phases not detected

**Solutions**:

1. **Generate debug video**: Visualize contact states to diagnose the issue
2. **Adjust velocity threshold**:
   - If missing contacts: decrease to `--velocity-threshold 0.01`
   - If false contacts: increase to `--velocity-threshold 0.03`
3. **Adjust minimum frames**: `--min-contact-frames 5` for longer required contact
4. **Check visibility**: Lower `--visibility-threshold 0.3` if feet are partially obscured

### Jump Height Seems Wrong

**Symptoms**: Unrealistic jump height values

**Solutions**:

1. **Use calibration**: For drop jumps, add `--drop-height` parameter with box height in meters (e.g., `--drop-height 0.40`)
   - Theoretically improves accuracy (⚠️ unvalidated)
2. **Verify flight time detection**: Check `flight_start_frame` and `flight_end_frame` in JSON
3. **Compare measurements**: JSON output includes both `jump_height_m` (primary) and `jump_height_kinematic_m` (kinematic-only)
4. **Check for drop jump detection**: If doing a drop jump, ensure first phase is elevated enough (>5% of frame height)

### Video Codec Issues

**Symptoms**: Cannot write debug video or corrupted output

**Solutions**:

1. **Install additional codecs**: Ensure OpenCV has proper video codec support
2. **Try different output format**: Use `.avi` extension instead of `.mp4`
3. **Check output path**: Ensure write permissions for output directory

## How It Works

1. **Pose Tracking**: MediaPipe extracts 2D pose landmarks (foot points: ankles, heels, foot indices) from each frame
2. **Position Calculation**: Averages ankle, heel, and foot index positions to determine foot location
3. **Smoothing**: Savitzky-Golay filter reduces tracking jitter while preserving motion dynamics
4. **Contact Detection**: Analyzes vertical position velocity to identify ground contact vs. flight phases
5. **Phase Identification**: Finds continuous ground contact and flight periods
   - Automatically detects drop jumps vs regular jumps
   - For drop jumps: identifies box → drop → ground contact → jump sequence
6. **Sub-Frame Interpolation**: Estimates exact transition times between frames
   - Uses Savitzky-Golay derivative for smooth velocity calculation
   - Linear interpolation of velocity to find threshold crossings
   - Achieves sub-millisecond timing precision (at 30fps: ±10ms vs ±33ms)
   - Reduces timing error by 60-70% for contact and flight measurements
   - Smoother velocity curves eliminate false threshold crossings
7. **Trajectory Curvature Analysis**: Refines transitions using acceleration patterns
   - Computes second derivative (acceleration) from position trajectory
   - Detects landing impact by acceleration spike
   - Identifies takeoff by acceleration change patterns
   - Provides independent validation and refinement of velocity-based detection
8. **Metric Calculation**:
   - Ground contact time = contact phase duration (using fractional frames)
   - Flight time = flight phase duration (using fractional frames)
   - Jump height = calibrated position-based measurement (if --drop-height provided)
   - Fallback: kinematic estimate (g × t²) / 8 with optional empirical correction factor (⚠️ unvalidated)

## Development

### Code Quality Standards

This project enforces strict code quality standards:

- **Type safety**: Full mypy strict mode compliance with complete type annotations
- **Linting**: Comprehensive ruff checks (pycodestyle, pyflakes, isort, pep8-naming, etc.)
- **Formatting**: Black code style
- **Testing**: pytest with 25 unit tests

### Development Commands

```bash
# Run the tool
uv run kinemotion dropjump-analyze <video_path>

# Run all tests
uv run pytest

# Run tests with verbose output
uv run pytest -v

# Format code
uv run black src/

# Lint code
uv run ruff check

# Auto-fix linting issues
uv run ruff check --fix

# Type check
uv run mypy src/dropjump

# Run all checks
uv run ruff check && uv run mypy src/dropjump && uv run pytest
```

### Contributing

Before committing code, ensure all checks pass:

1. Format with Black
2. Fix linting issues with ruff
3. Ensure type safety with mypy
4. Run all tests with pytest

See [CLAUDE.md](CLAUDE.md) for detailed development guidelines.

## Limitations

- **2D Analysis**: Only analyzes motion in the camera's view plane
- **Validation Status**: ⚠️ Accuracy has not been validated against gold standard measurements (force plates, 3D motion capture)
- **Side View Required**: Must film from the side to accurately track vertical motion
- **Single Athlete**: Designed for analyzing one athlete at a time
- **Timing precision**:
  - 30fps videos: ±10ms with sub-frame interpolation (vs ±33ms without)
  - 60fps videos: ±5ms with sub-frame interpolation (vs ±17ms without)
  - Higher frame rates still beneficial for better temporal resolution
- **Drop jump detection**: Requires first ground phase to be >5% higher than second ground phase

## Future Enhancements

- Advanced camera calibration (intrinsic parameters, lens distortion)
- Multi-angle analysis support
- Automatic camera orientation detection
- Batch processing for multiple videos
- Real-time analysis from webcam
- Export to CSV/Excel formats
- Comparison with reference values
- Force plate integration for validation

## License

MIT License - feel free to use for personal experiments and research.
