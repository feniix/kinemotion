# JSON Output Format Specification

**Version:** 2.0 (v0.26.0+)
**Status:** Alpha - subject to change

______________________________________________________________________

## Overview

Kinemotion uses a structured JSON format that separates measurement data from metadata. This design follows REST API best practices and enables easy data analysis while providing full context for reproducibility.

**Structure:**

```json
{
  "data": {
    // Physical measurements and metrics
  },
  "metadata": {
    "quality": {      // Tracking quality and confidence
    },
    "video": {        // Source video characteristics
    },
    "processing": {   // Processing context
    },
    "algorithm": {    // Algorithm configuration
    }
  }
}
```

______________________________________________________________________

## Complete Example: CMJ Analysis

```json
{
  "data": {
    "jump_height_m": 0.506,
    "flight_time_ms": 642.0,
    "countermovement_depth_m": 0.045,
    "eccentric_duration_ms": 412.0,
    "concentric_duration_ms": 305.0,
    "total_movement_time_ms": 717.0,
    "peak_eccentric_velocity_m_s": -1.234,
    "peak_concentric_velocity_m_s": 2.634,
    "transition_time_ms": 135.0,
    "standing_start_frame": 145.0,
    "lowest_point_frame": 146.0,
    "takeoff_frame": 154.3,
    "landing_frame": 172.8,
    "tracking_method": "foot"
  },
  "metadata": {
    "quality": {
      "confidence": "high",
      "score": 87.5,
      "indicators": {
        "avg_visibility": 0.736,
        "min_visibility": 0.687,
        "tracking_stable": true,
        "phase_detection_clear": true,
        "outliers_detected": 0,
        "outlier_percentage": 0.0,
        "position_variance": 0.000286,
        "fps": 29.6
      },
      "warnings": [
        "Moderate landmark visibility (avg 0.74). Results may be less accurate.",
        "Low frame rate (30 fps). Recommend recording at 60fps or higher."
      ]
    },
    "video": {
      "source_path": "athlete_cmj.mp4",
      "fps": 29.58,
      "resolution": {
        "width": 720,
        "height": 1280
      },
      "duration_s": 7.98,
      "frame_count": 236,
      "codec": "h264"
    },
    "processing": {
      "version": "0.26.0",
      "timestamp": "2025-01-13T18:30:45.123Z",
      "quality_preset": "balanced",
      "processing_time_s": 12.437
    },
    "algorithm": {
      "detection_method": "backward_search",
      "tracking_method": "mediapipe_pose",
      "model_complexity": 1,
      "smoothing": {
        "window_size": 5,
        "polynomial_order": 2,
        "use_bilateral_filter": true,
        "use_outlier_rejection": true
      },
      "detection": {
        "velocity_threshold": 0.02,
        "min_contact_frames": 3,
        "visibility_threshold": 0.5,
        "use_curvature_refinement": true
      }
    }
  }
}
```

______________________________________________________________________

## Complete Example: Drop Jump Analysis

```json
{
  "data": {
    "jump_height_m": 0.352,
    "flight_time_ms": 534.2,
    "ground_contact_time_ms": 213.5,
    "reactive_strength_index": 1.65,
    "contact_start_frame": 89.0,
    "contact_end_frame": 95.4,
    "flight_start_frame": 95.4,
    "flight_end_frame": 111.3,
    "peak_height_frame": 103.0,
    "contact_start_frame_precise": 89.23,
    "contact_end_frame_precise": 95.67,
    "flight_start_frame_precise": 95.67,
    "flight_end_frame_precise": 111.45
  },
  "metadata": {
    "quality": {
      "confidence": "high",
      "score": 86.6,
      "indicators": {
        "avg_visibility": 0.865,
        "min_visibility": 0.734,
        "tracking_stable": true,
        "phase_detection_clear": true,
        "outliers_detected": 1,
        "outlier_percentage": 1.1,
        "position_variance": 0.000738,
        "fps": 29.7
      },
      "warnings": [
        "Low frame rate (30 fps). Recommend recording at 60fps or higher."
      ]
    },
    "video": {
      "source_path": "dropjump_box40cm.mp4",
      "fps": 29.70,
      "resolution": {
        "width": 1920,
        "height": 1080
      },
      "duration_s": 5.45,
      "frame_count": 162
    },
    "processing": {
      "version": "0.26.0",
      "timestamp": "2025-01-13T18:32:10.456Z",
      "quality_preset": "balanced",
      "processing_time_s": 8.234
    },
    "algorithm": {
      "detection_method": "forward_search",
      "tracking_method": "mediapipe_pose",
      "model_complexity": 1,
      "drop_detection": {
        "auto_detect_drop_start": true,
        "detected_drop_frame": 45.0,
        "min_stationary_duration_s": 0.5
      },
      "smoothing": {
        "window_size": 5,
        "polynomial_order": 2,
        "use_bilateral_filter": true,
        "use_outlier_rejection": true
      },
      "detection": {
        "velocity_threshold": 0.02,
        "min_contact_frames": 3,
        "visibility_threshold": 0.5,
        "use_curvature_refinement": true
      }
    }
  }
}
```

______________________________________________________________________

## Field Specifications

### `data` Object

**Required fields:** Physical measurements from the jump analysis

**CMJ-specific fields:**

- `jump_height_m` (float): Maximum vertical displacement
- `flight_time_ms` (float): Time in the air in milliseconds
- `countermovement_depth_m` (float): Depth of eccentric phase
- `eccentric_duration_ms` (float): Time from start to lowest point in milliseconds
- `concentric_duration_ms` (float): Time from lowest point to takeoff in milliseconds
- `total_movement_time_ms` (float): Total time from start to takeoff in milliseconds
- `peak_eccentric_velocity_m_s` (float): Max downward velocity (negative)
- `peak_concentric_velocity_m_s` (float): Max upward velocity (negative in coords)
- `transition_time_ms` (float | null): Amortization phase duration in milliseconds
- `standing_start_frame` (float | null): Frame where movement begins
- `lowest_point_frame` (float): Frame at deepest countermovement
- `takeoff_frame` (float): Frame where feet leave ground
- `landing_frame` (float): Frame where feet contact ground
- `tracking_method` (string): "foot" or "com"

**Drop jump-specific fields:**

- `jump_height_m` (float | null): Maximum vertical displacement
- `flight_time_ms` (float | null): Time in the air
- `ground_contact_time_ms` (float | null): Time on ground between landing and takeoff
- `reactive_strength_index` (float | null): RSI = jump_height / ground_contact_time
- `contact_start_frame` (int | null): First frame of ground contact
- `contact_end_frame` (int | null): Last frame of ground contact
- `flight_start_frame` (int | null): First frame of flight
- `flight_end_frame` (int | null): Last frame of flight
- `peak_height_frame` (int | null): Frame at maximum height
- `contact_start_frame_precise` (float | null): Sub-frame precision timing
- `contact_end_frame_precise` (float | null): Sub-frame precision timing
- `flight_start_frame_precise` (float | null): Sub-frame precision timing
- `flight_end_frame_precise` (float | null): Sub-frame precision timing

______________________________________________________________________

### `metadata.quality` Object

**Tracking quality assessment and confidence scoring**

- `confidence` (string): "high" | "medium" | "low"
- `score` (float): Numerical quality score 0-100
- `indicators` (object): Detailed quality metrics
  - `avg_visibility` (float): Mean landmark visibility 0-1
  - `min_visibility` (float): Minimum visibility encountered
  - `tracking_stable` (boolean): Low jitter/variance detected
  - `phase_detection_clear` (boolean): Clear phase transitions
  - `outliers_detected` (int): Number of outlier frames corrected
  - `outlier_percentage` (float): Percentage of frames with outliers
  - `position_variance` (float): Position tracking variance (lower = better)
  - `fps` (float): Video frame rate
- `warnings` (array\[string\]): List of quality warnings

**Confidence levels:**

- **High (≥75)**: Trust these results, good tracking quality
- **Medium (50-74)**: Use with caution, review quality indicators
- **Low (\<50)**: Results may be unreliable, check warnings

______________________________________________________________________

### `metadata.video` Object

**Source video characteristics**

- `source_path` (string): Original video file path
- `fps` (float): Frames per second (actual, not nominal)
- `resolution` (object): Video dimensions
  - `width` (int): Width in pixels
  - `height` (int): Height in pixels
- `duration_s` (float): Total video duration in seconds
- `frame_count` (int): Total number of frames
- `codec` (string | null): Video codec (e.g., "h264", "hevc")

______________________________________________________________________

### `metadata.processing` Object

**Processing context and environment**

- `version` (string): Kinemotion version used (e.g., "0.26.0")
- `timestamp` (string): ISO 8601 timestamp of analysis
- `quality_preset` (string): "fast" | "balanced" | "accurate"
- `processing_time_s` (float): Time taken to process video

______________________________________________________________________

### `metadata.algorithm` Object

**Algorithm configuration for reproducibility**

**Common fields:**

- `detection_method` (string): "backward_search" (CMJ) or "forward_search" (drop jump)
- `tracking_method` (string): "mediapipe_pose"
- `model_complexity` (int): MediaPipe model complexity (0, 1, or 2)

**Smoothing configuration:**

- `smoothing` (object):
  - `window_size` (int): Savitzky-Golay window size
  - `polynomial_order` (int): Polynomial degree for SG filter
  - `use_bilateral_filter` (boolean): Bilateral temporal filtering enabled
  - `use_outlier_rejection` (boolean): RANSAC/median outlier rejection enabled

**Detection configuration:**

- `detection` (object):
  - `velocity_threshold` (float): Velocity threshold for contact detection
  - `min_contact_frames` (int): Minimum frames to confirm contact
  - `visibility_threshold` (float): Minimum landmark visibility to trust
  - `use_curvature_refinement` (boolean): Acceleration-based refinement enabled

**Drop jump-specific:**

- `drop_detection` (object | null):
  - `auto_detect_drop_start` (boolean): Auto-detection enabled
  - `detected_drop_frame` (int | null): Frame where drop begins
  - `min_stationary_duration_s` (float): Minimum standing time before drop

______________________________________________________________________

## Usage Examples

### Access Measurements

```python
import json

with open("results.json") as f:
    result = json.load(f)

# Get jump height
height = result['data']['jump_height_m']

# Get all measurements for analysis
measurements = result['data']
```

### Check Quality

```python
quality = result['metadata']['quality']

if quality['confidence'] == 'high':
    print(f"✅ High quality: {height:.3f}m")
elif quality['confidence'] == 'medium':
    print(f"⚠️ Medium quality: review warnings")
    print(f"Warnings: {quality['warnings']}")
else:
    print(f"❌ Low quality: results unreliable")
```

### DataFrame Export

```python
import pandas as pd

# Process multiple videos
results = [process_cmj_video(v) for v in videos]

# Extract just measurements
df = pd.DataFrame([r.to_dict()['data'] for r in results])

# Or add quality score
df = pd.DataFrame([
    {**r['data'], 'quality_score': r['metadata']['quality']['score']}
    for r in [res.to_dict() for res in results]
])
```

### Filter by Quality

```python
# Only use high-confidence results
high_quality = [
    r for r in results
    if r.to_dict()['metadata']['quality']['confidence'] == 'high'
]

print(f"High quality: {len(high_quality)}/{len(results)}")
```

### Get Processing Context

```python
meta = result['metadata']

print(f"Video: {meta['video']['fps']:.1f} fps")
print(f"Resolution: {meta['video']['resolution']['width']}x{meta['video']['resolution']['height']}")
print(f"Algorithm: {meta['algorithm']['detection_method']}")
print(f"Quality preset: {meta['processing']['quality_preset']}")
print(f"Processing time: {meta['processing']['processing_time_s']:.2f}s")
```

______________________________________________________________________

## Migration from v0.25.0

### Old Format (v0.25.0)

```json
{
  "jump_height_m": 0.352,
  "flight_time_s": 0.534,
  "confidence": "high",
  "quality_score": 87.5,
  "quality_indicators": {...},
  "warnings": [...]
}
```

### New Format (v0.26.0+)

```json
{
  "data": {
    "jump_height_m": 0.352,
    "flight_time_ms": 534.0
  },
  "metadata": {
    "quality": {
      "confidence": "high",
      "score": 87.5,
      "indicators": {...},
      "warnings": [...]
    },
    "video": {...},
    "processing": {...},
    "algorithm": {...}
  }
}
```

### Migration Code

```python
# Old access
height = result['jump_height_m']

# New access (add 'data' wrapper)
height = result['data']['jump_height_m']

# Quality fields moved
confidence = result['metadata']['quality']['confidence']  # was result['confidence']
score = result['metadata']['quality']['score']            # was result['quality_score']
```

______________________________________________________________________

## Benefits of New Structure

**For Analysis:**

- ✅ Clean DataFrame export: `pd.DataFrame([r['data'] for r in results])`
- ✅ Easy quality filtering: `if r['metadata']['quality']['confidence'] == 'high'`
- ✅ Clear separation: measurements vs context

**For Reproducibility:**

- ✅ Full algorithm configuration captured
- ✅ Video characteristics recorded
- ✅ Processing environment documented
- ✅ Quality assessment included

**For Extensibility:**

- ✅ Add new metadata fields without breaking data access
- ✅ Room for: calibration info, athlete details, session metadata
- ✅ Follows REST API patterns for future web service

**For Research:**

- ✅ All context needed for validation studies
- ✅ Can compare results across different algorithms
- ✅ Reproducible analysis with full parameter documentation

______________________________________________________________________

## Design Principles

1. **`data` = what was measured** - Physical metrics and results only
1. **`metadata` = how/context** - Quality, video info, processing details
1. **Flat data structure** - Easy DataFrame conversion, no deep nesting
1. **Nested metadata** - Organized by category (quality, video, processing, algorithm)
1. **Future-proof** - Can add fields without breaking existing code
1. **Industry standard** - Follows REST API patterns

______________________________________________________________________

## Future Additions (Non-Breaking)

Future versions may add to `metadata`:

**Calibration data:**

```json
{
  "metadata": {
    "calibration": {
      "drop_height_m": 0.40,
      "athlete_mass_kg": 75.0,
      "measured_reference_height_m": 0.30
    }
  }
}
```

**Session metadata:**

```json
{
  "metadata": {
    "session": {
      "athlete_id": "ATH001",
      "session_date": "2025-01-13",
      "session_type": "baseline_testing",
      "notes": "Post-training assessment"
    }
  }
}
```

**Batch processing:**

```json
{
  "metadata": {
    "batch": {
      "batch_id": "batch_20250113",
      "video_index": 5,
      "total_videos": 12
    }
  }
}
```

All additions go in `metadata`, never affecting `data` access.

______________________________________________________________________

## Changelog

**Version 2.0 (v0.26.0):**

- Breaking change: Restructured to `{data, metadata}` format
- Added `metadata.video` with source video characteristics
- Added `metadata.processing` with version and timing info
- Added `metadata.algorithm` with full algorithm configuration
- Moved quality fields to `metadata.quality`
- Improved extensibility for future additions

**Version 1.0 (v0.25.0):**

- Added quality assessment fields (confidence, quality_score, warnings)
- Flat structure with measurements and quality at top level
