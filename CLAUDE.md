# CLAUDE.md

## Repository Purpose

Kinemotion: Video-based kinematic analysis for athletic performance using MediaPipe pose tracking.

**Supported Jump Types:**
- **Drop Jump**: Ground contact time, flight time, reactive strength index
- **Counter Movement Jump (CMJ)**: Jump height, flight time, countermovement depth, triple extension

## Quick Setup

```bash
asdf install        # Install Python 3.12.7 + uv
uv sync            # Install dependencies
uv run kinemotion dropjump-analyze video.mp4
uv run kinemotion cmj-analyze video.mp4
```

**Development:**
```bash
uv run pytest                           # Run all 75 tests
uv run ruff check --fix && uv run pyright  # Lint + type check
```

## Architecture

### Module Structure

```
src/kinemotion/
├── cli.py                  # Main CLI (registers subcommands)
├── api.py                  # Python API (process_video, process_cmj_video, bulk)
├── core/                   # Shared: pose, smoothing, filtering, auto_tuning, video_io
├── dropjump/               # Drop jump: cli, analysis, kinematics, debug_overlay
└── cmj/                    # CMJ: cli, analysis, kinematics, joint_angles, debug_overlay

tests/                      # 75 tests total (61 drop jump, 9 CMJ, 5 CLI import)
docs/                       # CMJ_GUIDE, TRIPLE_EXTENSION, REAL_TIME_ANALYSIS, etc.
```

**Design**: Each jump type is a sibling module with its own CLI command, metrics, and visualization.

### Key Differences: Drop Jump vs CMJ

| Feature | Drop Jump | CMJ |
|---------|-----------|-----|
| Starting | Elevated box | Floor level |
| Algorithm | Forward search | Backward search from peak |
| Velocity | Absolute (magnitude) | Signed (direction matters) |
| Parameters | Auto-tuned quality presets | Auto-tuned quality presets |
| Key Metric | Ground contact time | Jump height from flight time |

## Critical Implementation Details

### 1. Aspect Ratio Preservation (core/video_io.py)

**Always:**
- Read first actual frame for dimensions: `frame.shape[:2]`
- Handle SAR (Sample Aspect Ratio) metadata with ffprobe
- Validate dimensions in `write_frame()` to prevent corruption

**Never:**
- Use `cv2.CAP_PROP_FRAME_WIDTH/HEIGHT` (wrong for rotated videos)

### 2. Video Rotation (core/video_io.py)

- Extract rotation metadata from ffprobe (`side_data_list`)
- Apply rotation in `read_frame()` using `cv2.rotate()`
- Update width/height after 90°/-90° rotations

### 3. JSON Serialization

**Always convert NumPy types:**
```python
"frame": int(self.frame) if self.frame is not None else None
```

**Never:**
```python
"frame": self.frame  # WRONG - int64 not JSON serializable
```

### 4. CMJ Signed Velocity (cmj/analysis.py)

**Critical difference from drop jump:**

```python
# Drop jump: absolute velocity
velocities = compute_velocity_from_derivative(positions)  # Returns abs()

# CMJ: MUST use signed velocity
velocities = compute_signed_velocity(positions)  # Keeps sign
```

**Why**: CMJ needs to distinguish upward (negative) vs downward (positive) motion for phase detection.

### 5. CMJ Backward Search (cmj/analysis.py)

**Algorithm:**
1. Find peak height first (global argmin)
2. Work backward: takeoff → lowest point
3. Work forward: landing after peak

**Why**: More robust than forward search, avoids false detections from video start.

### 6. Frame Dimensions

OpenCV vs NumPy ordering:
- NumPy shape: `(height, width, channels)`
- OpenCV VideoWriter: `(width, height)` tuple

## Common Tasks

### Add New Jump Type

1. Create `src/kinemotion/newjump/` with cli.py, analysis.py, kinematics.py
2. Register in `src/kinemotion/cli.py`: `cli.add_command(newjump_analyze)`
3. Add API functions in `api.py`
4. Export in `__init__.py`
5. Add tests

### Add Metrics

1. Update dataclass (e.g., `CMJMetrics`)
2. Calculate in `calculate_*_metrics()`
3. Add to `to_dict()` (convert NumPy types!)
4. Add tests

### Modify Detection

**Drop Jump**: Edit `detect_ground_contact()` in dropjump/analysis.py
**CMJ**: Edit `detect_cmj_phases()` in cmj/analysis.py (backward search)

## Testing & Quality

### Before Commit

```bash
uv run ruff check --fix   # Auto-fix linting
uv run pyright            # Type check (strict)
uv run pytest             # All 70 tests
```

### Standards

- Pyright strict mode (all functions typed)
- Ruff (100 char lines)
- Conventional Commits (see below)
- **Code duplication target: < 3%**

### Avoiding Code Duplication

When writing new code, follow these principles to maintain low duplication:

1. **Extract Common Logic**: If you find yourself copying code between modules, extract it to a shared utility
   - Example: `core/smoothing.py` uses `_smooth_landmarks_core()` shared by both standard and advanced smoothing
   - Example: `core/debug_overlay_utils.py` provides `BaseDebugOverlayRenderer` base class

2. **Use Inheritance for Shared Behavior**: When classes share common initialization or methods
   - Example: `DebugOverlayRenderer` and `CMJDebugOverlayRenderer` inherit from `BaseDebugOverlayRenderer`
   - Avoids duplicating `__init__()`, `write_frame()`, `close()`, and context manager methods

3. **Create Helper Functions**: Break down complex functions into smaller, reusable pieces
   - Example: `_extract_landmark_coordinates()`, `_get_landmark_names()`, `_fill_missing_frames()`
   - Makes code more testable and reusable

4. **Use Function Composition**: Pass functions as parameters to share control flow logic
   - Example: `_smooth_landmarks_core()` accepts a `smoother_fn` parameter
   - Allows different smoothing strategies without duplicating iteration logic

5. **Check Duplication**: Run `npx jscpd src/kinemotion` to verify duplication stays below 3%
   - Current: 2.96% (206 duplicated lines out of 6952)
   - Acceptable duplicates: CLI option definitions, small wrapper functions for type safety

## Quick Reference

### CLI

```bash
# Drop jump (auto-tuned parameters)
kinemotion dropjump-analyze video.mp4

# CMJ with debug video
kinemotion cmj-analyze video.mp4 --output debug.mp4

# Batch processing
kinemotion cmj-analyze videos/*.mp4 --batch --workers 4
```

### Python API

```python
# Drop jump
from kinemotion import process_dropjump_video
metrics = process_dropjump_video("video.mp4", quality="balanced")

# CMJ
from kinemotion import process_cmj_video
metrics = process_cmj_video("video.mp4", quality="balanced")
```

## Important Gotchas

### Video Processing

1. Read first frame for dimensions (not OpenCV properties)
2. Handle rotation metadata (mobile videos)
3. Preserve aspect ratio (SAR)
4. Validate dimensions in write_frame()

### CMJ Specific

1. **Lateral view required** - Front view won't work (parallax errors)
2. **Signed velocity** - Critical for phase detection
3. **Backward search** - Requires complete video (not real-time)
4. **MediaPipe limitations** - Ankle/knee only 18-27% visible in side view

### Type Safety

1. Convert NumPy types in `to_dict()`: `int()`, `float()`
2. Type all functions (pyright strict)
3. Handle None in optional fields

## Documentation

**User guides:** docs/guides/cmj-guide.md, docs/guides/camera-setup.md, docs/guides/bulk-processing.md
**Reference:** docs/reference/parameters.md, docs/reference/pose-systems.md
**Technical:** docs/technical/triple-extension.md, docs/technical/real-time-analysis.md
**Research:** docs/research/sports-biomechanics-pose-estimation.md

**See [docs/README.md](docs/README.md) for complete documentation navigation.**

### Documentation Organization

Documentation follows the [Diátaxis framework](https://diataxis.fr/) - a systematic approach that organizes content by user needs:

**Framework categories:**
1. **Tutorials/Guides** (learning-oriented) → `docs/guides/`
   - Goal: Help users accomplish specific tasks
   - Examples: Camera setup, CMJ analysis, bulk processing
   - Characteristic: Step-by-step instructions

2. **Reference** (information-oriented) → `docs/reference/`
   - Goal: Provide technical descriptions and specifications
   - Examples: CLI parameters, pose system comparisons
   - Characteristic: Structured for quick lookup

3. **Explanation** (understanding-oriented) → `docs/technical/`, `docs/research/`
   - Goal: Clarify and illuminate topics
   - Examples: Triple extension biomechanics, pose estimation research
   - Characteristic: Background knowledge, theory

4. **Development** (contributor-oriented) → `docs/development/`
   - Goal: Support project contributors
   - Examples: Validation plans, error findings
   - Characteristic: Internal processes, debugging

**Additional categories:**
- `docs/translations/` - Non-English documentation (e.g., Spanish)

**When adding new documentation:**
- **How-to content?** → `guides/`
- **Parameter specs or quick lookups?** → `reference/`
- **Implementation details or theory?** → `technical/` or `research/`
- **Testing or debugging?** → `development/`
- **Translation?** → `translations/{language-code}/`

## Commit Format

**Required**: [Conventional Commits](https://www.conventionalcommits.org/) - enforced by pre-commit hook

**Format**: `<type>(<scope>): <description>`

**Types** (triggers version bumps):
- `feat`: New feature → minor version bump (0.x.0)
- `fix`: Bug fix → patch version bump (0.0.x)
- `perf`: Performance improvement → patch
- `docs`, `test`, `refactor`, `chore`, `style`, `ci`, `build` → no version bump

**Examples:**
```bash
feat: add CMJ analysis with triple extension tracking
fix: correct takeoff detection in backward search algorithm
docs: add triple extension biomechanics guide
test: add CMJ phase detection tests
refactor: extract signed velocity to separate function
chore(release): 0.11.0 [skip ci]
```

**Breaking changes**: Add `!` or `BREAKING CHANGE:` footer
```bash
feat!: change API signature for process_video
```

**Important**: Commit messages must never reference Claude or AI assistance. Keep messages professional and focused on the technical changes.

## MCP Servers

Configured in `.mcp.json`: web-search, sequential-thinking, context7, etc.
