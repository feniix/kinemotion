# Core Utilities

Lower-level utilities for advanced usage and custom analysis pipelines.

## Pose Detection

::: kinemotion.core.pose.PoseTracker
options:
show_root_heading: true
show_source: false

::: kinemotion.core.pose.compute_center_of_mass
options:
show_root_heading: true
show_source: false

## Smoothing & Filtering

::: kinemotion.core.smoothing.smooth_landmarks
options:
show_root_heading: true
show_source: false

::: kinemotion.core.smoothing.smooth_landmarks_advanced
options:
show_root_heading: true
show_source: false

## Video Processing

::: kinemotion.core.video_io.VideoProcessor
options:
show_root_heading: true
show_source: false

## Auto-Tuning

::: kinemotion.core.auto_tuning.auto_tune_parameters
options:
show_root_heading: true
show_source: false

::: kinemotion.core.auto_tuning.analyze_video_sample
options:
show_root_heading: true
show_source: false

::: kinemotion.core.auto_tuning.QualityPreset
options:
show_root_heading: true
show_source: false

## Usage Example

```python
from kinemotion.core.pose import PoseTracker
from kinemotion.core.smoothing import smooth_landmarks
from kinemotion.core.video_io import VideoProcessor

# Initialize pose tracker
tracker = PoseTracker(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# Process video
video = VideoProcessor("video.mp4")
landmarks = []

for frame in video:
    result = tracker.process_frame(frame)
    if result:
        landmarks.append(result)

# Apply smoothing
smoothed = smooth_landmarks(
    landmarks,
    window_length=13,
    polyorder=3
)
```
