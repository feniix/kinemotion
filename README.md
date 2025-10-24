# Drop-Jump Video Analysis

A Python tool for analyzing side-view drop-jump videos to estimate key performance metrics: ground contact time, flight time, and jump height. Uses MediaPipe pose tracking and basic kinematics.

## Features

- **Automatic pose tracking** using MediaPipe Pose landmarks
- **Ground contact detection** based on foot velocity and position
- **Automatic drop jump detection** - identifies box → drop → landing → jump phases
- **Kinematic calculations** for jump metrics:
  - Ground contact time (ms)
  - Flight time (ms)
  - Jump height (m) - with optional calibration using drop box height
- **Calibrated measurements** - use known drop height for ~88% accuracy (vs 71% uncalibrated)
- **JSON output** for easy integration with other tools
- **Optional debug video** with visual overlays showing contact states and landmarks
- **Configurable parameters** for smoothing, thresholds, and detection

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

2. **Install versions specified in `.tool-versions`**:

```bash
asdf install
```

3. **Install project dependencies using uv**:

```bash
uv sync
```

This will install all dependencies and make the `dropjump-analyze` command available.

## Usage

### Basic Analysis

Analyze a video and output metrics to stdout as JSON:

```bash
dropjump-analyze video.mp4
```

### Save Metrics to File

```bash
dropjump-analyze video.mp4 --json-output metrics.json
```

### Generate Debug Video

Create an annotated video showing pose tracking and contact detection:

```bash
dropjump-analyze video.mp4 --output debug.mp4
```

### Calibrated Drop Jump Analysis

For most accurate measurements, provide the drop box height in meters:

```bash
# 40cm drop box
dropjump-analyze drop-jump.mp4 --drop-height 0.40

# 60cm drop box with full outputs
dropjump-analyze drop-jump.mp4 \
  --drop-height 0.60 \
  --json-output metrics.json \
  --output debug.mp4
```

### Full Example

```bash
dropjump-analyze jump.mp4 \
  --json-output results.json \
  --output debug.mp4 \
  --drop-height 0.40 \
  --smoothing-window 7 \
  --velocity-threshold 0.015
```

## Configuration Options

> **📖 For detailed explanations of all parameters, see [docs/PARAMETERS.md](docs/PARAMETERS.md)**
>
> This section provides a quick reference. The full guide includes:
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
  - Improves accuracy from ~71% to ~88%
  - Only applicable for drop jumps (box → drop → landing → jump)
  - **Tip**: Measure your box height accurately for best results

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
   - This improves accuracy from ~71% to ~88%
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

1. **Pose Tracking**: MediaPipe extracts 2D pose landmarks (ankles, heels, foot indices) from each frame
2. **Smoothing**: Savitzky-Golay filter reduces tracking jitter while preserving motion dynamics
3. **Contact Detection**: Analyzes vertical foot velocity to identify ground contact vs. flight phases
4. **Phase Identification**: Finds continuous ground contact and flight periods
   - Automatically detects drop jumps vs regular jumps
   - For drop jumps: identifies box → drop → ground contact → jump sequence
5. **Metric Calculation**:
   - Ground contact time = contact phase duration (after drop landing, before jump takeoff)
   - Flight time = flight phase duration
   - Jump height = calibrated position-based measurement (if --drop-height provided)
   - Fallback: corrected kinematic estimate (g × t²) / 8 × 1.35

## Development

### Code Quality Standards

This project enforces strict code quality standards:
- **Type safety**: Full mypy strict mode compliance with complete type annotations
- **Linting**: Comprehensive ruff checks (pycodestyle, pyflakes, isort, pep8-naming, etc.)
- **Formatting**: Black code style
- **Testing**: pytest with 9 unit tests

### Development Commands

```bash
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
- **Calibration accuracy**: With drop height calibration, achieves ~88% accuracy; without calibration ~71% accuracy
- **Side View Required**: Must film from the side to accurately track vertical motion
- **Single Athlete**: Designed for analyzing one athlete at a time
- **Frame Rate**: Higher frame rates (60+ fps) provide more accurate timing
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
