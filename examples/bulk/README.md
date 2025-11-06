# Kinemotion Library API Examples

This directory contains examples demonstrating how to use kinemotion as a Python library for programmatic video analysis.

## Overview

Kinemotion can be used as a library in your Python code, not just as a CLI tool. This is ideal for:

- **Bulk processing**: Analyze hundreds of videos in parallel
- **Automated pipelines**: Integrate into existing workflows
- **Custom analysis**: Build custom analysis tools on top of kinemotion
- **Research**: Batch process datasets for research studies

## Quick Start

### Single Video Processing

```python
from kinemotion import process_dropjump_video

# Process a single video
metrics = process_dropjump_video(
    video_path="athlete_jump.mp4",
    drop_height=0.40,  # 40cm drop box (REQUIRED)
    verbose=True
)

print(f"Jump height: {metrics.jump_height_m:.3f} m")
print(f"Ground contact time: {metrics.ground_contact_time_ms:.1f} ms")
print(f"Flight time: {metrics.flight_time_ms:.1f} ms")
```

### Bulk Video Processing

```python
from kinemotion import DropJumpVideoConfig, process_dropjump_videos_bulk

# Configure multiple videos
configs = [
    DropJumpVideoConfig("video1.mp4", drop_height=0.40),
    DropJumpVideoConfig("video2.mp4", drop_height=0.30),
    DropJumpVideoConfig("video3.mp4", drop_height=0.50),
]

# Process in parallel with 4 workers
results = process_dropjump_videos_bulk(configs, max_workers=4)

# Check results
for result in results:
    if result.success:
        print(f"{result.video_path}: {result.metrics.jump_height_m:.3f} m")
    else:
        print(f"{result.video_path}: ERROR - {result.error}")
```

## Example Scripts

### `simple_example.py`

Basic examples showing:

- Single video processing
- Multiple video processing with parallel workers
- Saving debug videos and JSON output

**Run it:**

```bash
python examples/simple_example.py
```

### `bulk_processing.py`

Advanced examples showing:

- Different quality presets (fast, balanced, accurate)
- Processing entire directories
- Progress callbacks
- Exporting results to CSV
- Custom parameters for challenging videos
- Error handling in batch processing

**Run it:**

```bash
python examples/bulk_processing.py
```

## API Reference

### Core Functions

#### `process_video()`

Process a single drop jump video.

**Parameters:**

- `video_path` (str, required): Path to video file
- `drop_height` (float, required): Drop box height in meters
- `quality` (str, optional): "fast", "balanced" (default), or "accurate"
- `output_video` (str, optional): Path for debug video output
- `json_output` (str, optional): Path for JSON metrics output
- `verbose` (bool, optional): Print processing details
- Expert overrides: `smoothing_window`, `velocity_threshold`, `min_contact_frames`, etc.

**Returns:**

- `DropJumpMetrics`: Object containing analysis results

**Raises:**

- `FileNotFoundError`: Video file not found
- `ValueError`: Invalid parameters or video cannot be processed

#### `process_dropjump_videos_bulk()`

Process multiple videos in parallel.

**Parameters:**

- `configs` (list\[VideoConfig\], required): List of video configurations
- `max_workers` (int, optional): Number of parallel workers (default: 4)
- `progress_callback` (callable, optional): Function called after each video completes

**Returns:**

- `list[VideoResult]`: Results for each video (in completion order)

### Data Classes

#### `VideoConfig`

Configuration for a single video.

```python
DropJumpVideoConfig(
    video_path="video.mp4",
    drop_height=0.40,
    quality="balanced",
    output_video=None,
    json_output=None,
    # Expert parameters...
)
```

#### `VideoResult`

Result of processing a single video.

**Attributes:**

- `video_path` (str): Path to the video
- `success` (bool): Whether processing succeeded
- `metrics` (DropJumpMetrics | None): Analysis results if successful
- `error` (str | None): Error message if failed
- `processing_time` (float): Processing duration in seconds

#### `DropJumpMetrics`

Analysis results for a drop jump.

**Key attributes:**

- `ground_contact_time_ms` (float): Ground contact time in milliseconds
- `flight_time_ms` (float): Flight time in milliseconds
- `jump_height_m` (float): Jump height in meters
- `reactive_strength_index` (float | None): RSI (jump height / contact time)
- `contact_start_frame` (int): Frame where ground contact begins
- `takeoff_frame` (int): Frame where athlete leaves ground
- `landing_frame` (int): Frame where athlete lands
- `fps` (float): Video frame rate

## Common Use Cases

### 1. Batch Process a Directory

```python
from pathlib import Path
from kinemotion import DropJumpVideoConfig, process_dropjump_videos_bulk

# Find all MP4 files
video_dir = Path("athlete_videos")
video_files = list(video_dir.glob("*.mp4"))

# Create configs with consistent settings
configs = [
    DropJumpVideoConfig(
        video_path=str(video_file),
        drop_height=0.40,
        quality="balanced",
        json_output=f"results/{video_file.stem}.json"
    )
    for video_file in video_files
]

# Process with progress tracking
def show_progress(result):
    status = "✓" if result.success else "✗"
    print(f"{status} {result.video_path}")

results = process_dropjump_videos_bulk(
    configs,
    max_workers=4,
    progress_callback=show_progress
)

# Calculate statistics
successful = [r for r in results if r.success]
avg_jump = sum(r.metrics.jump_height_m for r in successful) / len(successful)
print(f"\nAverage jump height: {avg_jump:.3f} m")
```

### 2. Export Results to CSV

```python
import csv
from kinemotion import DropJumpVideoConfig, process_dropjump_videos_bulk

# Process videos
configs = [...]  # Your video configs
results = process_dropjump_videos_bulk(configs, max_workers=4)

# Export successful results
with open("results.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "Video", "GCT (ms)", "Flight Time (ms)",
        "Jump Height (m)", "RSI"
    ])

    for result in results:
        if result.success:
            writer.writerow([
                result.video_path,
                f"{result.metrics.ground_contact_time_ms:.1f}",
                f"{result.metrics.flight_time_ms:.1f}",
                f"{result.metrics.jump_height_m:.3f}",
                f"{result.metrics.reactive_strength_index:.2f}"
                if result.metrics.reactive_strength_index else "N/A"
            ])
```

### 3. Different Quality Settings

```python
from kinemotion import DropJumpVideoConfig, process_dropjump_videos_bulk

configs = [
    # Fast: Quick screening
    DropJumpVideoConfig("video1.mp4", drop_height=0.40, quality="fast"),

    # Balanced: Default, good accuracy/speed
    DropJumpVideoConfig("video2.mp4", drop_height=0.40, quality="balanced"),

    # Accurate: Research-grade, slower
    DropJumpVideoConfig("video3.mp4", drop_height=0.40, quality="accurate"),
]

results = process_dropjump_videos_bulk(configs, max_workers=3)
```

### 4. Custom Parameters for Challenging Videos

```python
from kinemotion import process_dropjump_video

# Low quality video - more aggressive smoothing
metrics = process_dropjump_video(
    video_path="low_quality.mp4",
    drop_height=0.40,
    smoothing_window=7,        # More smoothing
    velocity_threshold=0.025,  # Less sensitive
    quality="accurate"
)

# High speed video - let auto-tuning handle FPS
metrics = process_dropjump_video(
    video_path="high_speed_120fps.mp4",
    drop_height=0.40,
    quality="accurate"  # Auto-adjusts for 120fps
)
```

### 5. Generate Debug Videos

```python
from kinemotion import DropJumpVideoConfig, process_dropjump_videos_bulk

# Process and save debug videos for review
configs = [
    DropJumpVideoConfig(
        video_path="athlete1_trial1.mp4",
        drop_height=0.40,
        output_video="debug/athlete1_trial1_debug.mp4",
        json_output="results/athlete1_trial1.json"
    ),
    # ... more videos
]

results = process_dropjump_videos_bulk(configs, max_workers=2)
```

## Performance Tips

### 1. Choose Appropriate Worker Count

```python
# CPU-bound processing - use 1 worker per CPU core
import multiprocessing
max_workers = multiprocessing.cpu_count()

# Or limit to avoid overloading
max_workers = min(multiprocessing.cpu_count(), 8)
```

### 2. Use Quality Presets Wisely

- **fast**: 50% faster, good for initial screening or large batches
- **balanced**: Default, best for most use cases
- **accurate**: Research-grade, ~2x slower but highest quality

### 3. Skip Debug Videos for Batch Processing

Debug videos are slow to generate. Skip them for large batches:

```python
# Don't set output_video parameter
DropJumpVideoConfig("video.mp4", drop_height=0.40)  # No debug video
```

### 4. Process Videos Sequentially for Single Machine

```python
# Use max_workers=1 if you have limited memory
results = process_dropjump_videos_bulk(configs, max_workers=1)
```

## Error Handling

All errors are isolated per video - one failure doesn't crash the batch:

```python
results = process_dropjump_videos_bulk(configs, max_workers=4)

for result in results:
    if result.success:
        # Process successful result
        print(f"✓ {result.video_path}: {result.metrics.jump_height_m:.3f} m")
    else:
        # Handle error
        print(f"✗ {result.video_path}: {result.error}")

        # Log error to file
        with open("errors.log", "a") as f:
            f.write(f"{result.video_path}: {result.error}\n")
```

## Integration Examples

### With Pandas

```python
import pandas as pd
from kinemotion import DropJumpVideoConfig, process_dropjump_videos_bulk

# Read video list from CSV
df = pd.read_csv("videos.csv")  # Columns: path, drop_height

# Create configs
configs = [
    DropJumpVideoConfig(row.path, row.drop_height)
    for _, row in df.iterrows()
]

# Process
results = process_dropjump_videos_bulk(configs, max_workers=4)

# Create results DataFrame
results_data = []
for result in results:
    if result.success:
        results_data.append({
            "video": result.video_path,
            "gct_ms": result.metrics.ground_contact_time_ms,
            "flight_time_ms": result.metrics.flight_time_ms,
            "jump_height_m": result.metrics.jump_height_m,
            "rsi": result.metrics.reactive_strength_index,
        })

results_df = pd.DataFrame(results_data)
results_df.to_csv("analysis_results.csv", index=False)
```

### With Click for Custom CLI

```python
import click
from kinemotion import DropJumpVideoConfig, process_dropjump_videos_bulk

@click.command()
@click.argument("video_dir", type=click.Path(exists=True))
@click.option("--drop-height", type=float, required=True)
@click.option("--workers", type=int, default=4)
def analyze_directory(video_dir, drop_height, workers):
    """Analyze all videos in a directory."""
    from pathlib import Path

    videos = list(Path(video_dir).glob("*.mp4"))
    configs = [
        DropJumpVideoConfig(str(v), drop_height=drop_height)
        for v in videos
    ]

    click.echo(f"Processing {len(videos)} videos with {workers} workers...")

    results = process_dropjump_videos_bulk(configs, max_workers=workers)

    successful = [r for r in results if r.success]
    click.echo(f"Success: {len(successful)}/{len(results)}")

if __name__ == "__main__":
    analyze_directory()
```

## Troubleshooting

### Import Errors

If you see import errors, make sure kinemotion is installed:

```bash
# From the repository root
uv sync
```

### Memory Issues with Large Batches

Reduce `max_workers` or process videos sequentially:

```python
results = process_dropjump_videos_bulk(configs, max_workers=1)
```

### Video Processing Failures

Check the error message in `VideoResult.error`:

```python
for result in results:
    if not result.success:
        print(f"Failed: {result.video_path}")
        print(f"Reason: {result.error}")
```

Common issues:

- Video file corrupted or unreadable
- No pose detected in video (person not visible)
- Invalid drop height or parameters

## Questions?

For more information, see:

- Main README: `../README.md`
- Parameters documentation: `../docs/PARAMETERS.md`
- Source code: `../src/kinemotion/api.py`
