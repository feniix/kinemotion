# Drop Jump API

The drop jump API provides functions for analyzing drop jump videos and extracting kinematic metrics.

## Quick Example

```python
from kinemotion import process_dropjump_video

metrics = process_dropjump_video(
    video_path="dropjump.mp4",
    quality="balanced",  # fast, balanced, or accurate
    output_video="debug.mp4",  # optional
    verbose=True
)

print(f"Ground contact time: {metrics.ground_contact_time:.3f}s")
print(f"Flight time: {metrics.flight_time:.3f}s")
print(f"RSI: {metrics.reactive_strength_index:.2f}")
```

## Main Functions

::: kinemotion.api.process_dropjump_video
options:
show_root_heading: true
show_source: false

::: kinemotion.api.process_dropjump_videos_bulk
options:
show_root_heading: true
show_source: false

## Configuration

::: kinemotion.api.DropJumpVideoConfig
options:
show_root_heading: true
show_source: false

## Results

::: kinemotion.api.DropJumpVideoResult
options:
show_root_heading: true
show_source: false

## Metrics

::: kinemotion.dropjump.kinematics.DropJumpMetrics
options:
show_root_heading: true
show_source: false

## Key Parameters

### quality

Analysis quality preset that determines processing speed and accuracy. The system automatically tunes parameters based on video characteristics and the selected preset.

Options:

- `"fast"` - Quick processing, lower precision
- `"balanced"` - Default, good for most cases
- `"accurate"` - Research-grade, slower processing

Default: `"balanced"`

```python
metrics = process_dropjump_video("video.mp4", quality="accurate")
```

### output_video

Path to write debug video with overlay visualization. If not provided, no debug video is created.

```python
metrics = process_dropjump_video(
    "video.mp4",
    quality="balanced",
    output_video="debug.mp4"
)
```

### json_output

Path to write JSON metrics output. If not provided, metrics are only returned as a Python object.

```python
metrics = process_dropjump_video(
    "video.mp4",
    json_output="metrics.json"
)
```

### Expert Parameters

For advanced users, you can override auto-tuned parameters:

- `smoothing_window` - Override auto-tuned smoothing window size
- `velocity_threshold` - Override velocity threshold for ground contact detection
- `min_contact_frames` - Override minimum contact frames
- `visibility_threshold` - Override visibility threshold
- `detection_confidence` - Override pose detection confidence
- `tracking_confidence` - Override pose tracking confidence
- `drop_start_frame` - Manually specify frame where drop begins
