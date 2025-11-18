---
title: api-reference-quick-commands
type: note
permalink: api/api-reference-quick-commands
tags:
- api
- cli
- quick-reference
---

# API Reference & Quick Commands

## Quick Setup

```bash
asdf install        # Install Python 3.12.7 + uv
uv sync            # Install dependencies
```

## CLI Commands

### Drop Jump Analysis
```bash
# Auto-tuned analysis
kinemotion dropjump-analyze video.mp4

# With debug output
kinemotion dropjump-analyze video.mp4 --output debug.mp4

# Batch processing
kinemotion dropjump-analyze videos/*.mp4 --batch --workers 4
```

### CMJ Analysis
```bash
# Auto-tuned analysis
kinemotion cmj-analyze video.mp4

# With debug video output
kinemotion cmj-analyze video.mp4 --output debug.mp4

# Batch processing
kinemotion cmj-analyze videos/*.mp4 --batch --workers 4
```

## Python API

### Drop Jump
```python
from kinemotion import process_dropjump_video

metrics = process_dropjump_video(
    "video.mp4",
    quality="balanced"  # or "fast", "quality"
)
# Returns: ground_contact_time, flight_time, rsi
```

### CMJ
```python
from kinemotion import process_cmj_video

metrics = process_cmj_video(
    "video.mp4",
    quality="balanced"  # or "fast", "quality"
)
# Returns: jump_height, flight_time, countermovement_depth, triple_extension
```

### Bulk Processing
```python
from kinemotion import bulk_process_videos

results = bulk_process_videos(
    "videos/*.mp4",
    analysis_type="cmj",
    workers=4,
    quality="balanced"
)
```

## Testing

```bash
# All tests with coverage
uv run pytest

# Generate HTML report
uv run pytest --cov-report=html
open htmlcov/index.html

# Run specific test
uv run pytest tests/path/to/test_file.py::test_name

# Run with markers
uv run pytest -m "not slow"
```

## Code Quality

```bash
# Lint (auto-fix)
uv run ruff check --fix

# Type check
uv run pyright

# Format
uv run ruff format .

# All checks
uv run ruff check --fix && uv run pyright && uv run pytest
```

## Key Dependencies

| Library | Version | Purpose |
|---------|---------|---------|
| Python | 3.12.7 | Runtime (supports >=3.10,<3.13) |
| MediaPipe | >=0.10.9 | Pose detection |
| OpenCV | >=4.9.0 | Video I/O |
| NumPy | >=1.26.0 | Numerical computation |
| SciPy | >=1.11.0 | Signal processing |
| pytest | 9.0.0 | Testing |

## Environment Setup

All handled by `uv`:
- Python 3.12.7 via asdf
- Virtual environment
- Dependencies from pyproject.toml

No manual venv needed.

## Documentation Structure

- **docs/guides/** - How-to tutorials
- **docs/reference/** - Technical specs
- **docs/technical/** - Implementation details
- **docs/development/** - Testing, typing, contribution
- **docs/research/** - Background theory

See docs/README.md for complete navigation.
