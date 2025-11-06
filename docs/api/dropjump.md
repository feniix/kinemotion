# Drop Jump API

The drop jump API provides functions for analyzing drop jump videos and extracting kinematic metrics.

## Quick Example

```python
from kinemotion import process_dropjump_video

metrics = process_video(
    video_path="dropjump.mp4",
    drop_height=0.40,  # meters
    output_path="debug.mp4",  # optional
    smoothing=True
)

print(f"Ground contact time: {metrics.ground_contact_time:.3f}s")
print(f"Flight time: {metrics.flight_time:.3f}s")
print(f"RSI: {metrics.reactive_strength_index:.2f}")
```

## Main Functions

::: kinemotion.api.process_video
options:
show_root_heading: true
show_source: false

::: kinemotion.api.process_videos_bulk
options:
show_root_heading: true
show_source: false

## Configuration

::: kinemotion.api.VideoConfig
options:
show_root_heading: true
show_source: false

## Results

::: kinemotion.api.VideoResult
options:
show_root_heading: true
show_source: false

## Metrics

::: kinemotion.dropjump.kinematics.DropJumpMetrics
options:
show_root_heading: true
show_source: false

## Key Parameters

### drop_height

**Required.** The height of the drop box in meters. This is critical for accurate velocity calculations.

```python
metrics = process_video("video.mp4", drop_height=0.40)  # 40cm box
```

### smoothing

Apply Savitzky-Golay smoothing to landmark positions before analysis. Reduces noise but may slightly delay event detection.

Default: `True`

### output_path

Path to write debug video with overlay visualization. If not provided, no debug video is created.

```python
metrics = process_video(
    "video.mp4",
    drop_height=0.40,
    output_path="debug.mp4"
)
```
