# API Overview

Kinemotion provides a Python API for video-based kinematic analysis. The API is organized around two main jump types:

## Main Functions

### Drop Jump Analysis

Process drop jump videos and extract kinematic metrics:

- `process_video()` - Analyze a single drop jump video
- `process_videos_bulk()` - Batch process multiple drop jump videos
- `VideoConfig` - Configuration for drop jump analysis
- `VideoResult` - Results from drop jump analysis
- `DropJumpMetrics` - Kinematic metrics for drop jumps

See [Drop Jump API](dropjump.md) for detailed documentation.

### CMJ Analysis

Process counter movement jump videos and extract kinematic metrics:

- `process_cmj_video()` - Analyze a single CMJ video
- `process_cmj_videos_bulk()` - Batch process multiple CMJ videos
- `CMJVideoConfig` - Configuration for CMJ analysis
- `CMJVideoResult` - Results from CMJ analysis
- `CMJMetrics` - Kinematic metrics for CMJs

See [CMJ API](cmj.md) for detailed documentation.

## Basic Usage

```python
from kinemotion import process_dropjump_video, process_cmj_video

# Drop jump analysis
drop_metrics = process_video("dropjump.mp4", drop_height=0.40)

# CMJ analysis
cmj_metrics = process_cmj_video("cmj.mp4")
```

## Batch Processing

```python
from kinemotion import process_dropjump_videos_bulk, process_cmj_videos_bulk

# Batch drop jump analysis
results = process_videos_bulk(
    video_paths=["video1.mp4", "video2.mp4"],
    drop_height=0.40,
    output_dir="results/",
    workers=4
)

# Batch CMJ analysis
cmj_results = process_cmj_videos_bulk(
    video_paths=["cmj1.mp4", "cmj2.mp4"],
    output_dir="results/",
    workers=4
)
```

## Core Utilities

For advanced usage, you can access lower-level utilities:

- Pose detection and tracking
- Velocity computation
- Smoothing and filtering
- Video I/O with rotation handling

See [Core Utilities](core.md) for detailed documentation.
