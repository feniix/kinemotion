# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

Drop-jump video analysis tool that estimates ground contact time, flight time, and jump height by tracking athlete's feet using MediaPipe pose tracking and basic kinematics.

## Project Setup

### Dependencies

Managed with `uv` and `asdf`:
- Python version: 3.12.7 (specified in `.tool-versions`)
  - **Important**: MediaPipe requires Python 3.12 or earlier (no 3.13 support yet)
- Install dependencies: `uv sync`
- Run CLI: `dropjump-analyze <video.mp4>`

**Production dependencies:**
- click: CLI framework
- opencv-python: Video processing
- mediapipe: Pose detection and tracking
- numpy: Numerical operations
- scipy: Signal processing (Savitzky-Golay filter)

**Development dependencies:**
- pytest: Testing framework
- black: Code formatting
- ruff: Fast Python linter
- mypy: Static type checking

### Development Commands

- **Run tool**: `uv run dropjump-analyze <video_path>`
- **Install/sync deps**: `uv sync`
- **Run tests**: `uv run pytest`
- **Run specific test**: `uv run pytest tests/test_aspect_ratio.py -v`
- **Format code**: `uv run black src/`
- **Lint code**: `uv run ruff check`
- **Auto-fix lint issues**: `uv run ruff check --fix`
- **Type check**: `uv run mypy src/dropjump`
- **Run all checks**: `uv run ruff check && uv run mypy src/dropjump && uv run pytest`

## Architecture

### Module Structure

```
src/dropjump/
├── cli.py              # Click-based CLI entry point
├── pose_tracker.py     # MediaPipe Pose integration
├── smoothing.py        # Savitzky-Golay landmark smoothing
├── contact_detection.py # Ground contact state detection
├── kinematics.py       # Metric calculations (contact time, flight time, jump height)
└── video_io.py         # Video processing and debug overlay rendering

tests/
├── test_contact_detection.py  # Contact detection unit tests
├── test_kinematics.py          # Metrics calculation tests
└── test_aspect_ratio.py        # Aspect ratio preservation tests

docs/
└── PARAMETERS.md       # Comprehensive guide to all CLI parameters
```

### Analysis Pipeline

1. **Pose Tracking** (pose_tracker.py): MediaPipe extracts foot landmarks (ankles, heels, foot indices) from each frame
2. **Smoothing** (smoothing.py): Savitzky-Golay filter reduces jitter while preserving dynamics
3. **Contact Detection** (contact_detection.py): Analyzes vertical foot velocity to classify ground contact vs. flight
4. **Phase Identification**: Finds continuous ground contact and flight periods
   - Automatically detects drop jumps vs regular jumps
   - For drop jumps: identifies standing on box → drop → ground contact → jump
5. **Sub-Frame Interpolation** (contact_detection.py): Estimates exact transition times
   - Computes velocity from Savitzky-Golay derivative (smoothing.py)
   - Linear interpolation of smooth velocity to find threshold crossings
   - Returns fractional frame indices (e.g., 48.78 instead of 49)
   - Reduces timing error from ±33ms to ±10ms at 30fps (60-70% improvement)
   - Eliminates false threshold crossings from velocity noise
6. **Metrics Calculation** (kinematics.py):
   - Ground contact time from phase duration (using fractional frames)
   - Flight time from phase duration (using fractional frames)
   - Jump height from position tracking with optional calibration
   - Fallback: kinematic estimate from flight time: h = (g × t²) / 8
7. **Output**: JSON metrics + optional debug video overlay

### Key Design Decisions

- **Normalized coordinates**: All positions use MediaPipe's 0-1 normalized coordinates (independent of video resolution)
- **Velocity-based contact detection**: More robust than absolute position thresholds
- **Configurable thresholds**: CLI flags allow tuning for different video qualities and athletes
- **Calibrated jump height**: Position-based measurement with drop height calibration for accuracy
  - Optional `--drop-height` parameter uses known drop box height to calibrate measurements
  - Achieves ~88% accuracy (vs 71% with kinematic-only method)
  - Fallback to empirically-corrected kinematic formula when no calibration provided
- **Aspect ratio preservation**: Output video ALWAYS matches source video dimensions
  - Handles SAR (Sample Aspect Ratio) metadata from mobile videos
  - No hardcoded aspect ratios

## Code Quality & Type Safety

The codebase enforces strict code quality standards using multiple tools:

### Type Checking with mypy

- **Strict mode enabled**: All functions require type annotations
- Configuration in `pyproject.toml` under `[tool.mypy]`
- Key settings:
  - `disallow_untyped_defs`: All functions must have complete type annotations
  - `disallow_incomplete_defs`: Partial type hints not allowed
  - `warn_return_any`: Warns on Any return types
  - Third-party stubs: Ignores missing imports for cv2, mediapipe, scipy
- Run with: `uv run mypy src/dropjump`

### Linting with ruff

- **Comprehensive rule set**: pycodestyle, pyflakes, isort, pep8-naming, pyupgrade, flake8-bugbear, flake8-comprehensions
- Configuration in `pyproject.toml` under `[tool.ruff]`
- Key settings:
  - Line length: 100 characters
  - Target version: Python 3.11+
  - Auto-fixable issues: Use `uv run ruff check --fix`
- Run with: `uv run ruff check`

### Code Formatting with black

- Consistent code style across the project
- Run with: `uv run black src/`

### When Contributing Code

Always run before committing:
```bash
# Format code
uv run black src/

# Check and fix linting issues
uv run ruff check --fix

# Type check
uv run mypy src/dropjump

# Run tests
uv run pytest
```

Or run all checks at once:
```bash
uv run ruff check && uv run mypy src/dropjump && uv run pytest
```

## Critical Implementation Details

### Aspect Ratio Preservation & SAR Handling (video_io.py)

**IMPORTANT**: The tool preserves the exact aspect ratio of the source video, including SAR (Sample Aspect Ratio) metadata. No dimensions are hardcoded.

#### VideoProcessor (`video_io.py:15-110`)

- Reads the **first actual frame** to get true encoded dimensions (not OpenCV properties)
- Critical for mobile videos with rotation metadata
- `CAP_PROP_FRAME_WIDTH` and `CAP_PROP_FRAME_HEIGHT` can return incorrect dimensions
- Always use `frame.shape[:2]` to get actual (height, width)
- **SAR Metadata Extraction**: Uses `ffprobe` to extract Sample Aspect Ratio metadata
  - Many mobile videos use non-square pixels (e.g., 1080x1080 encoded, but 616x1080 display)
  - Calculates display dimensions: `display_width = width × SAR_width / SAR_height`
  - Falls back to encoded dimensions if ffprobe unavailable or SAR = 1:1

```python
# Correct approach (current implementation)
ret, first_frame = self.cap.read()
if ret:
    self.height, self.width = first_frame.shape[:2]  # From actual frame data
```

**Never do this:**
```python
# Wrong - may return incorrect dimensions with rotated videos
self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
```

#### DebugOverlayRenderer (`video_io.py:130-330`)

- Creates output video with **display dimensions** (respecting SAR)
- Resizes frames from encoded dimensions to display dimensions if needed (INTER_LANCZOS4)
- Output video uses square pixels (SAR 1:1) at correct display size
- H.264 codec (avc1) with fallback to mp4v
- Runtime validation in `write_frame()` ensures every frame matches expected encoded dimensions
- Raises `ValueError` if aspect ratio would be corrupted

### Sub-Frame Interpolation (contact_detection.py:113-227)

**IMPORTANT**: The tool uses sub-frame interpolation with derivative-based velocity to achieve timing precision beyond frame boundaries.

#### Derivative-Based Velocity Calculation (smoothing.py:126-172)

Instead of simple frame-to-frame differences, velocity is computed as the derivative of the smoothed position trajectory using Savitzky-Golay filter:

**Advantages:**
- **Smoother velocity curves**: Eliminates noise from frame-to-frame jitter
- **More accurate threshold crossings**: Clean transitions without false positives
- **Better interpolation**: Smoother velocity gradient for sub-frame precision
- **Consistent with smoothing**: Uses same polynomial fit as position smoothing

**Implementation:**
```python
# OLD: Simple differences (noisy)
velocities = np.abs(np.diff(foot_positions, prepend=foot_positions[0]))

# NEW: Derivative from smoothed trajectory (smooth)
velocities = savgol_filter(positions, window_length=5, polyorder=2, deriv=1, delta=1.0)
```

**Key Function:**
- `compute_velocity_from_derivative()`: Computes first derivative using Savitzky-Golay filter

#### Sub-Frame Interpolation Algorithm

At 30fps, each frame represents 33.3ms. Contact events (landing, takeoff) rarely occur exactly at frame boundaries. Sub-frame interpolation estimates the exact moment between frames when velocity crosses the threshold.

**Algorithm:**
1. Calculate smooth velocity using derivative: `v = derivative(smooth_position)`
2. Find frames where velocity crosses threshold (e.g., from 0.025 to 0.015, threshold 0.020)
3. Use linear interpolation to find exact crossing point:
   ```python
   # If v[10] = 0.025 and v[11] = 0.015, threshold = 0.020
   t = (0.020 - 0.025) / (0.015 - 0.025) = 0.5
   # Crossing at frame 10.5
   ```

**Key Functions:**
- `interpolate_threshold_crossing()`: Linear interpolation of velocity crossing
- `find_interpolated_phase_transitions()`: Returns fractional frame indices for all phases

**Accuracy Improvement:**
```
30fps without interpolation: ±33ms (1 frame on each boundary)
30fps with interpolation:    ±10ms (sub-frame precision)
60fps without interpolation: ±17ms
60fps with interpolation:    ±5ms
```

**Velocity Comparison:**
```python
# Frame-to-frame differences: noisy, discontinuous jumps
v_simple = [0.01, 0.03, 0.02, 0.04, 0.02, 0.01]  # Jittery

# Derivative-based: smooth, continuous curve
v_deriv = [0.015, 0.022, 0.025, 0.024, 0.018, 0.012]  # Smooth
```

**Example:**
```python
# Integer frames: contact from frame 49 to 53 (5 frames = 168ms at 30fps)
# With derivative velocity: contact from 49.0 to 53.0 (4 frames = 135ms)
# Result: Cleaner threshold crossings, less sub-frame offset
```

### JSON Serialization (kinematics.py:29-100)

**IMPORTANT**: NumPy integer types (int64, int32) are not JSON serializable.

Always convert to Python `int()` in `to_dict()` method:

```python
"contact_start_frame": (
    int(self.contact_start_frame) if self.contact_start_frame is not None else None
)
```

**Never do this:**
```python
# Wrong - will fail with "Object of type int64 is not JSON serializable"
"contact_start_frame": self.contact_start_frame
```

### Video Codec Handling (video_io.py:78-94)

- Primary codec: H.264 (avc1) - better quality, smaller file size
- Fallback codec: MPEG-4 (mp4v) - broader compatibility
- Raises error if both fail to open

### Frame Dimensions (Throughout)

OpenCV and NumPy use different dimension ordering:

- **NumPy array shape**: `(height, width, channels)`
- **OpenCV VideoWriter size**: `(width, height)` tuple

Example:
```python
frame.shape           # (1080, 1920, 3)  - height first
cv2.VideoWriter(..., (1920, 1080))      # width first
```

Always be careful with dimension ordering to avoid squashed/stretched videos.

## Common Development Tasks

### Adding New Metrics

1. Update `DropJumpMetrics` class in `kinematics.py:10-19`
2. Add calculation logic in `calculate_drop_jump_metrics()` function
3. Update `to_dict()` method for JSON serialization (remember to convert NumPy types to Python types)
4. Optionally add visualization in `DebugOverlayRenderer.render_frame()` in `video_io.py:96`
5. Add tests in `tests/test_kinematics.py`

### Modifying Contact Detection Logic

Edit `detect_ground_contact()` in `contact_detection.py:14`. Key parameters:
- `velocity_threshold`: Tune for different surface/athlete combinations (default: 0.02)
- `min_contact_frames`: Adjust for frame rate and contact duration expectations (default: 3)
- `visibility_threshold`: Minimum landmark visibility score (default: 0.5)

### Adjusting Smoothing

Modify `smooth_landmarks()` in `smoothing.py:9`:
- `window_length`: Controls smoothing strength (must be odd, default: 5)
- `polyorder`: Polynomial order for Savitzky-Golay filter (default: 2)

### Parameter Tuning

**IMPORTANT**: See `docs/PARAMETERS.md` for comprehensive guide on all 7 CLI parameters.

Quick reference:
- **smoothing-window**: Trajectory smoothness (↑ for noisy video)
- **velocity-threshold**: Contact sensitivity (↓ to detect brief contacts)
- **min-contact-frames**: Temporal filter (↑ to remove false contacts)
- **visibility-threshold**: Landmark confidence (↓ for occluded feet)
- **detection-confidence**: Pose detection strictness (MediaPipe)
- **tracking-confidence**: Tracking persistence (MediaPipe)
- **drop-height**: Drop box height in meters for calibration (e.g., 0.40 for 40cm)

The detailed guide includes:
- How each parameter works internally
- Frame rate considerations
- Scenario-based recommended settings
- Debugging workflow with visual indicators
- Parameter interaction effects

### Working with Different Video Formats

The tool handles various video formats and aspect ratios:
- 16:9 landscape (1920x1080)
- 4:3 standard (640x480)
- 9:16 portrait (1080x1920)
- Mobile videos with rotation metadata

Tests in `tests/test_aspect_ratio.py` verify this behavior.

## Testing

### Running Tests

```bash
# All tests (9 tests total)
uv run pytest

# Specific test modules
uv run pytest tests/test_aspect_ratio.py -v
uv run pytest tests/test_contact_detection.py -v
uv run pytest tests/test_kinematics.py -v

# With verbose output
uv run pytest -v
```

### Test Coverage

- **Aspect ratio preservation**: 4 tests covering 16:9, 4:3, 9:16, and validation
- **Contact detection**: 3 tests for ground contact detection and phase identification
- **Kinematics**: 2 tests for metrics calculation and JSON serialization

### Code Quality

All code passes:
- ✅ **Type checking**: Full mypy strict mode compliance
- ✅ **Linting**: ruff checks with comprehensive rule sets
- ✅ **Tests**: 9/9 tests passing
- ✅ **Formatting**: Black code style

## Troubleshooting

### MediaPipe Version Compatibility

- MediaPipe 0.10.x requires Python ≤ 3.12
- If you see "no matching distribution" errors, check Python version in `.tool-versions`

### Video Dimension Issues

If output video has wrong aspect ratio:
1. Check `VideoProcessor` is reading first frame correctly
2. Verify `DebugOverlayRenderer` receives correct width/height from `VideoProcessor`
3. Check that `write_frame()` validation is enabled (should raise error if dimensions mismatch)
4. Run `tests/test_aspect_ratio.py` to verify the mechanism

### JSON Serialization Errors

If you see "Object of type X is not JSON serializable":
1. Check `kinematics.py` `to_dict()` method
2. Ensure all NumPy types are converted to Python types with `int()` or `float()`
3. Run `tests/test_kinematics.py::test_metrics_to_dict` to verify

### Video Codec Issues

If output video won't play:
1. Try different output format: `.avi` instead of `.mp4`
2. Check OpenCV codec support: `cv2.getBuildInformation()`
3. DebugOverlayRenderer will fallback from H.264 to MPEG-4 automatically

### Type Checking Issues

If mypy reports errors:
1. Ensure all function signatures have complete type annotations (parameters and return types)
2. For numpy types, use explicit casts: `int()`, `float()` when converting to Python types
3. For third-party libraries without stubs (cv2, mediapipe, scipy), use `# type: ignore` comments sparingly
4. Check `pyproject.toml` under `[tool.mypy]` for configuration
5. Run `uv run mypy src/dropjump` to verify fixes

## CLI Usage Examples

```bash
# Basic analysis (JSON to stdout)
uv run dropjump-analyze video.mp4

# Save metrics to file
uv run dropjump-analyze video.mp4 --json-output results.json

# Generate debug video
uv run dropjump-analyze video.mp4 --output debug.mp4

# Drop jump with calibration (40cm box)
uv run dropjump-analyze video.mp4 --drop-height 0.40

# Custom parameters for noisy video
uv run dropjump-analyze video.mp4 \
  --smoothing-window 7 \
  --velocity-threshold 0.01 \
  --min-contact-frames 5

# Full analysis with calibration and all outputs
uv run dropjump-analyze video.mp4 \
  --output debug.mp4 \
  --json-output metrics.json \
  --drop-height 0.40 \
  --smoothing-window 7

# Regular jump (no calibration, uses corrected kinematic method)
uv run dropjump-analyze jump.mp4 \
  --output debug.mp4 \
  --json-output metrics.json
```

## MCP Server Configuration

The repository includes MCP server configuration in `.mcp.json`:
- **web-search**: DuckDuckGo search via @dannyboy2042/freebird-mcp
- **sequential**: Sequential thinking via @smithery-ai/server-sequential-thinking
- **context7**: Library documentation via @upstash/context7-mcp
- **terraform**: Terraform registry via terraform-mcp-server
- **basic-memory**: Note-taking for sr-quant-iac project

Enabled via `.claude/settings.local.json` with `enableAllProjectMcpServers: true`.
