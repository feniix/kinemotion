# CMJ API

The CMJ API provides functions for analyzing counter movement jump videos and extracting kinematic metrics including triple extension analysis.

## Quick Example

```python
from kinemotion import process_cmj_video

metrics = process_cmj_video(
    video_path="cmj.mp4",
    quality="balanced",  # fast, balanced, or accurate
    output_video="debug.mp4",  # optional
    verbose=True
)

print(f"Jump height: {metrics.jump_height:.2f}m")
print(f"Flight time: {metrics.flight_time:.3f}s")
print(f"Countermovement depth: {metrics.countermovement_depth:.3f}m")
print(f"Triple extension: {metrics.triple_extension_percentage:.1f}%")
```

## Main Functions

::: kinemotion.api.process_cmj_video
options:
show_root_heading: true
show_source: false

::: kinemotion.api.process_cmj_videos_bulk
options:
show_root_heading: true
show_source: false

## Configuration

::: kinemotion.api.CMJVideoConfig
options:
show_root_heading: true
show_source: false

## Results

::: kinemotion.api.CMJVideoResult
options:
show_root_heading: true
show_source: false

## Metrics

::: kinemotion.cmj.kinematics.CMJMetrics
options:
show_root_heading: true
show_source: false

## Key Differences from Drop Jump

### No Calibration Required

Unlike drop jumps, CMJ analysis doesn't require a `drop_height` parameter. All measurements are relative to the starting position.

### Backward Search Algorithm

CMJ detection uses a backward search algorithm starting from the peak height, making it more robust than forward search.

### Signed Velocity

CMJ analysis uses signed velocity (direction matters) to distinguish upward vs downward motion phases.

### Lateral View Required

CMJ analysis requires a lateral (side) view for accurate depth and triple extension measurements. Front view will not work due to parallax errors.

## Triple Extension Analysis

The CMJ API includes detailed triple extension analysis:

```python
metrics = process_cmj_video("cmj.mp4")

# Triple extension metrics
print(f"Hip extension: {metrics.hip_extension_angle:.1f}°")
print(f"Knee extension: {metrics.knee_extension_angle:.1f}°")
print(f"Ankle plantar flexion: {metrics.ankle_plantar_flexion_angle:.1f}°")
print(f"Overall triple extension: {metrics.triple_extension_percentage:.1f}%")
```

See [Triple Extension Technical Documentation](../technical/triple-extension.md) for biomechanics details.
