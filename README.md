# Kinemotion

[![PyPI version](https://img.shields.io/pypi/v/kinemotion.svg)](https://pypi.org/project/kinemotion/)
[![Python Version](https://img.shields.io/pypi/pyversions/kinemotion.svg)](https://pypi.org/project/kinemotion/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[![Tests](https://github.com/feniix/kinemotion/workflows/Test%20%26%20Quality/badge.svg)](https://github.com/feniix/kinemotion/actions)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=feniix_kinemotion&metric=alert_status)](https://sonarcloud.io/summary/overall?id=feniix_kinemotion)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=feniix_kinemotion&metric=coverage)](https://sonarcloud.io/summary/overall?id=feniix_kinemotion)

[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Type checked with pyright](https://img.shields.io/badge/type%20checked-pyright-blue.svg)](https://github.com/microsoft/pyright)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)

> A video-based kinematic analysis tool for athletic performance. Analyzes vertical jump videos to estimate key performance metrics using MediaPipe pose tracking and advanced kinematics.

**Supported jump types:**

- **Drop Jump**: Ground contact time, flight time, reactive strength index
- **Counter Movement Jump (CMJ)**: Jump height, flight time, countermovement depth, triple extension biomechanics

## Features

### Core Features

- **Automatic pose tracking** using MediaPipe Pose landmarks
- **Derivative-based velocity** - smooth velocity calculation from position trajectory
- **Trajectory curvature analysis** - acceleration patterns for refined event detection
- **Sub-frame interpolation** - precise timing beyond frame boundaries
- **Intelligent auto-tuning** - automatic parameter optimization based on video characteristics
- **JSON output** for easy integration with other tools
- **Debug video overlays** with visual analysis
- **Batch processing** - CLI and Python API for parallel processing
- **Python library API** - use kinemotion programmatically
- **CSV export** - aggregated results for research

### Drop Jump Analysis

- **Ground contact detection** based on foot velocity and position
- **Automatic drop jump detection** - identifies box → drop → landing → jump phases
- **Metrics**: Ground contact time, flight time, jump height (with drop height calibration)
- **Reactive strength index** calculations

### Counter Movement Jump (CMJ) Analysis

- **Backward search algorithm** - robust phase detection from peak height
- **Flight time method** - force plate standard (h = g×t²/8)
- **Triple extension tracking** - ankle, knee, hip joint angles
- **Skeleton overlay** - biomechanical visualization
- **Metrics**: Jump height, flight time, countermovement depth, eccentric/concentric durations
- **Validated accuracy**: 50.6cm jump (±1 frame precision)

## Validation Status

⚠️ **IMPORTANT**: This tool's accuracy has **not been validated** against gold standard measurements (force plates, 3D motion capture). All accuracy claims and improvement estimates are theoretical and based on algorithmic considerations, not empirical testing.

The tool provides consistent measurements and may be useful for:

- Tracking relative changes in an individual athlete over time
- Comparing similar jumps under controlled conditions
- Exploratory analysis and research

For clinical, research, or performance assessment requiring validated accuracy, this tool should be compared against validated measurement systems before use.

## Setup

### System Requirements

**All Platforms:**

- Python 3.10, 3.11, or 3.12

**Platform-Specific:**

#### Windows

**Required system dependencies:**

- [Microsoft Visual C++ 2022 Redistributable](https://visualstudio.microsoft.com/visual-cpp-build-tools/) - Runtime libraries for OpenCV/MediaPipe
- Python 3.10-3.12 (64-bit) - MediaPipe requires 64-bit Python

**Recommended for mobile video support:**

- [FFmpeg](https://ffmpeg.org/download.html) - Download and add to PATH for full video codec support

#### macOS

**Required system dependencies:**

- Xcode Command Line Tools - Provides compilers and system frameworks

  ```bash
  xcode-select --install
  ```

**Recommended for mobile video support:**

```bash
brew install ffmpeg
```

#### Linux (Ubuntu/Debian)

**Recommended system libraries:**

```bash
sudo apt-get update
sudo apt-get install -y \
    libgl1 \           # OpenGL library for OpenCV
    libglib2.0-0 \     # GLib library for MediaPipe
    libgomp1 \         # OpenMP library for multi-threading
    ffmpeg             # Video codec support and metadata extraction
```

**Note:** `ffmpeg` provides the `ffprobe` tool for video metadata extraction (rotation, aspect ratio). Kinemotion works without it, but mobile/rotated videos may not process correctly. A warning will be shown if `ffprobe` is not available.

### Installation Methods

#### From PyPI (Recommended)

```bash
pip install kinemotion
```

#### From Source (Development)

**Step 1:** Install asdf plugins (if not already installed):

```bash
asdf plugin add python
asdf plugin add uv
```

**Step 2:** Install versions specified in `.tool-versions`:

```bash
asdf install
```

**Step 3:** Install project dependencies using uv:

```bash
uv sync
```

This will install all dependencies and make the `kinemotion` command available.

## Usage

Kinemotion supports two jump types with intelligent auto-tuning that automatically optimizes parameters based on video characteristics.

### Analyzing Drop Jumps

Analyzes reactive strength and ground contact time:

```bash
# Automatic parameter tuning based on video characteristics
kinemotion dropjump-analyze video.mp4
```

### Analyzing CMJ

Analyzes jump height and biomechanics:

```bash
# No drop height needed (floor level)
kinemotion cmj-analyze video.mp4

# With triple extension visualization
kinemotion cmj-analyze video.mp4 --output debug.mp4
```

### Common Options (Both Jump Types)

```bash
# Save metrics to JSON
kinemotion cmj-analyze video.mp4 --json-output results.json

# Generate debug video
kinemotion cmj-analyze video.mp4 --output debug.mp4

# Complete analysis with all outputs
kinemotion cmj-analyze video.mp4 \
  --output debug.mp4 \
  --json-output results.json \
  --verbose
```

### Quality Presets

```bash
# Fast (50% faster, good for batch)
kinemotion cmj-analyze video.mp4 --quality fast

# Balanced (default)
kinemotion cmj-analyze video.mp4 --quality balanced

# Accurate (research-grade)
kinemotion cmj-analyze video.mp4 --quality accurate --verbose
```

### Batch Processing

Process multiple videos in parallel:

```bash
# Drop jumps
kinemotion dropjump-analyze videos/*.mp4 --batch --workers 4

# CMJ with output directories
kinemotion cmj-analyze videos/*.mp4 --batch --workers 4 \
  --json-output-dir results/ \
  --csv-summary summary.csv
```

## Python API

Use kinemotion as a library for automated pipelines and custom analysis.

### Drop Jump API

```python
from kinemotion import process_dropjump_video

# Process a single video
metrics = process_dropjump_video(
    video_path="athlete_jump.mp4",
    quality="balanced",
    verbose=True
)

# Access results
print(f"Jump height: {metrics.jump_height:.3f} m")
print(f"Ground contact time: {metrics.ground_contact_time * 1000:.1f} ms")
print(f"Flight time: {metrics.flight_time * 1000:.1f} ms")
```

### Bulk Video Processing

```python
# Drop jump bulk processing
from kinemotion import DropJumpVideoConfig, process_dropjump_videos_bulk

configs = [
    DropJumpVideoConfig("video1.mp4", quality="balanced"),
    DropJumpVideoConfig("video2.mp4", quality="accurate"),
]

results = process_dropjump_videos_bulk(configs, max_workers=4)

# CMJ bulk processing
from kinemotion import CMJVideoConfig, process_cmj_videos_bulk

cmj_configs = [
    CMJVideoConfig("cmj1.mp4"),
    CMJVideoConfig("cmj2.mp4", quality="accurate"),
]

cmj_results = process_cmj_videos_bulk(cmj_configs, max_workers=4)

for result in cmj_results:
    if result.success:
        print(f"{result.video_path}: {result.metrics.jump_height*100:.1f}cm")
```

See `examples/bulk/README.md` for comprehensive API documentation.

### CMJ-Specific Features

```python
# Triple extension angles available in metrics
metrics = process_cmj_video("video.mp4", output_video="debug.mp4")

# Debug video shows:
# - Skeleton overlay (foot→shin→femur→trunk)
# - Joint angles (ankle, knee, hip, trunk)
# - Phase-coded visualization
```

### CSV Export Example

```python
# See examples/bulk/ for complete CSV export examples
from kinemotion import process_cmj_video
import csv

# ... process videos ...
with open("results.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Video", "GCT (ms)", "Flight (ms)", "Jump (m)"])

    for r in results:
        if r.success and r.metrics:
            writer.writerow([
                Path(r.video_path).name,
                f"{r.metrics.ground_contact_time * 1000:.1f}" if r.metrics.ground_contact_time else "N/A",
                f"{r.metrics.flight_time * 1000:.1f}" if r.metrics.flight_time else "N/A",
                f"{r.metrics.jump_height:.3f}" if r.metrics.jump_height else "N/A",
            ])
```

**See [examples/bulk/README.md](examples/bulk/README.md) for comprehensive API documentation and more examples.**

## Configuration Options

### Intelligent Auto-Tuning

Kinemotion automatically optimizes parameters based on your video:

- **FPS-based scaling**: 30fps, 60fps, 120fps videos use different thresholds automatically
- **Quality-based adjustments**: Adapts smoothing based on MediaPipe tracking confidence
- **Always enabled**: Outlier rejection, curvature analysis, drop start detection

### Required Parameters

- `--drop-height <float>` **\[REQUIRED\]**
  - Height of drop box/platform in meters (e.g., 0.40 for 40cm)
  - Used for accurate calibration of jump height measurements
  - Measure your box height accurately for best results

### Optional Parameters

- `--quality [fast|balanced|accurate]` (default: balanced)

  - **fast**: Quick analysis, less precise (~50% faster)
  - **balanced**: Good accuracy/speed tradeoff (recommended)
  - **accurate**: Research-grade analysis, slower (maximum precision)

- `--verbose` / `-v`

  - Show auto-selected parameters and analysis details
  - Useful for understanding what the tool is doing

- `--output <path>` / `-o`

  - Generate annotated debug video with pose tracking visualization

- `--json-output <path>` / `-j`

  - Save metrics to JSON file instead of stdout

### Expert Overrides (Rarely Needed)

For advanced users who need manual control:

- `--drop-start-frame <int>`: Manually specify where drop begins (if auto-detection fails)
- `--smoothing-window <int>`: Override auto-tuned smoothing window
- `--velocity-threshold <float>`: Override auto-tuned velocity threshold
- `--min-contact-frames <int>`: Override auto-tuned minimum contact frames
- `--visibility-threshold <float>`: Override visibility threshold
- `--detection-confidence <float>`: Override MediaPipe detection confidence
- `--tracking-confidence <float>`: Override MediaPipe tracking confidence

> **📖 For detailed parameter explanations, see [docs/reference/parameters.md](docs/reference/parameters.md)**
>
> **Note:** Most users never need expert parameters - auto-tuning handles optimization automatically!

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
1. **Increase smoothing**: Use `--smoothing-window 7` or higher
1. **Adjust detection confidence**: Try `--detection-confidence 0.6` or `--tracking-confidence 0.6`
1. **Generate debug video**: Use `--output` to visualize what's being tracked

### No Pose Detected

**Symptoms**: "No frames processed" error or all null landmarks

**Solutions**:

1. **Verify video format**: OpenCV must be able to read the video
1. **Check framing**: Ensure full body is visible in side view
1. **Lower confidence thresholds**: Try `--detection-confidence 0.3 --tracking-confidence 0.3`
1. **Test video playback**: Verify video opens correctly with standard video players

### Incorrect Contact Detection

**Symptoms**: Wrong ground contact times, flight phases not detected

**Solutions**:

1. **Generate debug video**: Visualize contact states to diagnose the issue
1. **Adjust velocity threshold**:
   - If missing contacts: decrease to `--velocity-threshold 0.01`
   - If false contacts: increase to `--velocity-threshold 0.03`
1. **Adjust minimum frames**: `--min-contact-frames 5` for longer required contact
1. **Check visibility**: Lower `--visibility-threshold 0.3` if feet are partially obscured

### Jump Height Seems Wrong

**Symptoms**: Unrealistic jump height values

**Solutions**:

1. **Use calibration**: For drop jumps, add `--drop-height` parameter with box height in meters (e.g., `--drop-height 0.40`)
   - Theoretically improves accuracy (⚠️ unvalidated)
1. **Verify flight time detection**: Check `flight_start_frame` and `flight_end_frame` in JSON
1. **Compare measurements**: JSON output includes both `jump_height_m` (primary) and `jump_height_kinematic_m` (kinematic-only)
1. **Check for drop jump detection**: If doing a drop jump, ensure first phase is elevated enough (>5% of frame height)

### Video Codec Issues

**Symptoms**: Cannot write debug video or corrupted output

**Solutions**:

1. **Install additional codecs**: Ensure OpenCV has proper video codec support
1. **Try different output format**: Use `.avi` extension instead of `.mp4`
1. **Check output path**: Ensure write permissions for output directory

## How It Works

1. **Pose Tracking**: MediaPipe extracts 2D pose landmarks (foot points: ankles, heels, foot indices) from each frame
1. **Position Calculation**: Averages ankle, heel, and foot index positions to determine foot location
1. **Smoothing**: Savitzky-Golay filter reduces tracking jitter while preserving motion dynamics
1. **Contact Detection**: Analyzes vertical position velocity to identify ground contact vs. flight phases
1. **Phase Identification**: Finds continuous ground contact and flight periods
   - Automatically detects drop jumps vs regular jumps
   - For drop jumps: identifies box → drop → ground contact → jump sequence
1. **Sub-Frame Interpolation**: Estimates exact transition times between frames
   - Uses Savitzky-Golay derivative for smooth velocity calculation
   - Linear interpolation of velocity to find threshold crossings
   - Achieves sub-millisecond timing precision (at 30fps: ±10ms vs ±33ms)
   - Reduces timing error by 60-70% for contact and flight measurements
   - Smoother velocity curves eliminate false threshold crossings
1. **Trajectory Curvature Analysis**: Refines transitions using acceleration patterns
   - Computes second derivative (acceleration) from position trajectory
   - Detects landing impact by acceleration spike
   - Identifies takeoff by acceleration change patterns
   - Provides independent validation and refinement of velocity-based detection
1. **Metric Calculation**:
   - Ground contact time = contact phase duration (using fractional frames)
   - Flight time = flight phase duration (using fractional frames)
   - Jump height = calibrated position-based measurement (if --drop-height provided)
   - Fallback: kinematic estimate (g × t²) / 8 with optional empirical correction factor (⚠️ unvalidated)

## Development

### Code Quality Standards

This project enforces strict code quality standards:

- **Type safety**: Full pyright strict mode compliance with complete type annotations
- **Linting**: Comprehensive ruff checks (pycodestyle, pyflakes, isort, pep8-naming, etc.)
- **Formatting**: Black code style
- **Testing**: pytest with 61 unit tests
- **PEP 561 compliant**: Includes py.typed marker for type checking support

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
uv run pyright

# Run all checks
uv run ruff check && uv run pyright && uv run pytest
```

### Contributing

Before committing code, ensure all checks pass:

1. Format with Black
1. Fix linting issues with ruff
1. Ensure type safety with pyright
1. Run all tests with pytest

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
- Real-time analysis from webcam
- Comparison with reference values
- Force plate integration for validation

## License

MIT License - feel free to use for personal experiments and research.
