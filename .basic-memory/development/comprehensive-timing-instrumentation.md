---
title: Comprehensive Timing Instrumentation
type: note
permalink: development/comprehensive-timing-instrumentation
---

# Comprehensive Timing Instrumentation

## Overview

Complete timing instrumentation implemented across the entire backend and core analysis pipeline. Every significant operation now emits structured timing events for full end-to-end visibility. Analysis reveals **MediaPipe pose tracking dominates processing time (88-94%)**.

## Architecture & Data Flow

### Complete Data Flow
```
process_cmj_video / process_dropjump_video (API)
    ↓
    stage_times dict (collected during analysis)
    ├─ timing_video_initialization
    ├─ timing_pose_tracking
    ├─ timing_parameter_auto_tuning
    ├─ timing_smoothing
    ├─ timing_vertical_position_extraction
    ├─ timing_phase_detection
    ├─ timing_metrics_calculation
    └─ timing_quality_assessment
    ↓
ProcessingInfo.timing_breakdown (stored in metrics metadata)
    ↓
metrics.to_dict() includes timing_breakdown_ms
    ↓
Backend extracts and emits individual timing events
    ↓
Structured logs (JSON in production, colored in development)
```

## Complete List of All Timing Events (20 Total)

### Backend Operations (5 events)
1. **`timing_video_validation`** - Validating uploaded video file format/codec
2. **`timing_video_file_save`** - Writing uploaded video file to temporary disk
3. **`timing_r2_input_video_upload`** - Uploading input video to R2 storage
4. **`timing_response_serialization`** - Converting metrics to JSON and building HTTP response
5. **`timing_temp_file_cleanup`** - Cleaning up temporary video files

### Core Analysis Pipeline (8 events)
6. **`timing_video_initialization`** - VideoProcessor setup and frame reading
7. **`timing_pose_tracking`** - MediaPipe pose detection on all frames (~90% of total)
8. **`timing_parameter_auto_tuning`** - Auto-tuning algorithm parameters
9. **`timing_smoothing`** - Savitzky-Golay smoothing filter
10. **`timing_vertical_position_extraction`** - Extracting Y-axis positions
11. **`timing_phase_detection`** - Detecting jump phases
12. **`timing_metrics_calculation`** - Computing final metrics
13. **`timing_quality_assessment`** - Quality assessment

### Output Generation (3 events)
14. **`timing_metadata_building`** - Creating VideoInfo, ProcessingInfo, AlgorithmConfig, ResultMetadata
15. **`timing_metrics_validation`** - Running DropJumpMetricsValidator or CMJMetricsValidator
16. **`timing_json_serialization`** - Converting metrics.to_dict() to JSON string

### Debug Video Processing (2 events)
17. **`timing_debug_video_generation`** - Rendering annotated frames and writing to disk (always logged when requested)
18. **`timing_debug_video_reencode`** - FFmpeg re-encoding for browser compatibility (only if codec fallback)

### Cloud Storage (2 events)
19. **`timing_r2_results_upload`** - Uploading metrics JSON to R2
20. **`timing_r2_debug_video_upload`** - Uploading debug video to R2

## Implementation Details

### Core API Changes (src/kinemotion/api.py)

**Renamed function for consistency:**
- `_generate_outputs()` → `_generate_dropjump_outputs()`
- Ensures both jump types use consistent naming pattern

**Updated `_generate_dropjump_outputs()` and `_generate_cmj_outputs()`:**
- Now returns `tuple[float, float, float]` instead of `None`
- Returns: `(generation_duration, reencode_duration, json_duration)`
- Measures JSON serialization, debug video generation, and re-encoding separately

**Updated both `process_dropjump_video()` and `process_cmj_video()`:**
- Capture timing for metadata building (VideoInfo, ProcessingInfo, AlgorithmConfig, ResultMetadata)
- Capture timing for metrics validation
- Unpack all three duration values from output generator
- Add all timings to `stage_times` dict

### Backend Changes (backend/src/kinemotion_backend/app.py)

**Added timing event emissions:**
- `timing_video_validation` (line 507) - Validates uploaded video
- `timing_video_file_save` (line 519) - Writes to temporary disk
- `timing_r2_input_video_upload` (line 534) - Renamed from `video_uploaded_to_r2` for consistency
- `timing_response_serialization` (line 654) - JSON serialization overhead
- `timing_temp_file_cleanup` (line 732) - Temporary file cleanup

All backend timings logged at INFO level with `logger.info()` and `duration_ms` field.

### Metadata Changes (src/kinemotion/core/metadata.py)

**Added to `ProcessingInfo` dataclass:**
- `timing_breakdown: dict[str, float] | None = None`
- `to_dict()` converts timings to milliseconds as `timing_breakdown_ms`
- Included in returned metrics metadata

### Debug Overlay Changes (src/kinemotion/core/debug_overlay_utils.py)

**Updated `BaseDebugOverlayRenderer`:**
- Added `reencode_duration_s = 0.0` attribute
- `close()` method captures FFmpeg re-encoding time
- Only populated if codec fallback occurs (mp4v → H.264)

## Log Output Examples

### Development Mode (Colored)
```
2024-12-10T14:23:45.123456+00:00 [INFO] timing_pose_tracking duration_ms=5183.1
2024-12-10T14:23:45.234567+00:00 [INFO] timing_debug_video_generation duration_ms=850.3
2024-12-10T14:23:48.234567+00:00 [INFO] timing_debug_video_reencode duration_ms=400.2
2024-12-10T14:23:49.345678+00:00 [INFO] timing_r2_results_upload duration_ms=234.0
```

### Production Mode (JSON)
```json
{"timestamp": "2025-12-10T14:23:45.123456Z", "severity": "INFO", "event": "timing_pose_tracking", "duration_ms": 5183.1}
{"timestamp": "2025-12-10T14:23:45.234567Z", "severity": "INFO", "event": "timing_debug_video_generation", "duration_ms": 850.3}
{"timestamp": "2025-12-10T14:23:48.234567Z", "severity": "INFO", "event": "timing_debug_video_reencode", "duration_ms": 400.2}
{"timestamp": "2025-12-10T14:23:49.345678Z", "severity": "INFO", "event": "timing_r2_results_upload", "duration_ms": 234.0}
```

### Metrics JSON Response
```json
{
  "metadata": {
    "processing": {
      "version": "0.39.1",
      "timestamp": "2025-12-10T13:41:33.547498+00:00",
      "quality_preset": "balanced",
      "processing_time_s": 5.713,
      "timing_breakdown_ms": {
        "Video initialization": 325.4,
        "Pose tracking": 5183.1,
        "Parameter auto-tuning": 2.0,
        "Smoothing": 188.6,
        "Vertical position extraction": 4.6,
        "Phase detection": 1.2,
        "Metrics calculation": 0.2,
        "Quality assessment": 7.7
      }
    }
  }
}
```

## Performance Analysis

### CMJ Analysis (236 frames @ 29.58fps, 8s video)
```
Video initialization.....................    128ms (  2.3%)
Pose tracking...........................   5196ms ( 94.1%)  ← BOTTLENECK
Parameter auto-tuning...................      2ms (  0.0%)
Smoothing...............................    179ms (  3.2%)
Vertical position extraction............      5ms (  0.1%)
Phase detection.........................      1ms (  0.0%)
Metrics calculation.....................      0ms (  0.0%)
Quality assessment......................      8ms (  0.2%)
Total...................................   5521ms (100.0%)
```

### Drop Jump Analysis (89 frames @ 29.73fps, 3s video)
```
Pose tracking...........................   2114ms ( 92.1%)  ← BOTTLENECK
Parameter auto-tuning...................      1ms (  0.0%)
Smoothing...............................     70ms (  3.0%)
Vertical position extraction............      1ms (  0.0%)
Ground contact detection................      0ms (  0.0%)
Metrics calculation.....................      4ms (  0.2%)
Quality assessment......................      3ms (  0.1%)
Total...................................   2294ms (100.0%)
```

### Key Findings
- **Primary Bottleneck**: MediaPipe pose tracking (88-94% of time)
  - Processes every frame through neural network
  - ~22-23ms per frame on average
  - Scales linearly with frame count

- **Fast Operations**:
  - Smoothing: 3%
  - Video initialization: 2-4%
  - All other operations: <1% each

## Google Cloud Logging Queries

**Find all timing events:**
```
jsonPayload.event=~"^timing_"
```

**Find specific stage:**
```
jsonPayload.event="timing_pose_tracking"
```

**Find R2 operations:**
```
jsonPayload.event=~"^timing_r2_"
```

**Find analysis pipeline only (exclude R2/debug):**
```
jsonPayload.event=~"^timing_" AND NOT jsonPayload.event=~"^timing_r2_|timing_debug"
```

**Find slow stages (>1 second):**
```
jsonPayload.event=~"^timing_" AND jsonPayload.duration_ms > 1000
```

**Timeline of all operations:**
```
jsonPayload.event=~"^timing_" AND timestamp>="2025-12-10T14:23:45Z" AND timestamp<"2025-12-10T14:24:00Z"
```

**Average duration per stage:**
```
# Use Cloud Monitoring to aggregate by event name and calculate mean(duration_ms)
```

## Optimization Recommendations

### High Impact (Address Pose Tracking Bottleneck)
1. **Reduce frame rate** - Process every Nth frame (e.g., 15fps instead of 30fps)
2. **GPU acceleration** - MediaPipe supports GPU if available
3. **Async processing** - Pre-process poses while waiting for upload
4. **Frame batching** - Process multiple frames in parallel if memory permits

### Medium Impact
1. **Optimize smoothing** - Already efficient (3%), but FFT possible for large videos
2. **Lazy output generation** - Only generate debug video if requested

### Low Impact (Already fast)
- Phase detection, metrics calculation, quality assessment already negligible

## Benefits of Complete Instrumentation

✅ **Full Pipeline Visibility** - See every stage from upload to response
✅ **Bottleneck Identification** - Pose tracking consistently ~90% (MediaPipe limitation)
✅ **Backend vs Analysis** - Measure server overhead vs. analysis time
✅ **Debug Overhead** - Track cost of generating debug videos
✅ **Storage Costs** - Monitor R2 upload times
✅ **Response Latency** - Measure serialization overhead
✅ **Validation Performance** - Track metrics validation timing
✅ **Metadata Building** - Measure config object creation time
✅ **Granular Querying** - Each event independently queryable
✅ **Optimization Targets** - Data-driven decisions on improvements

## Testing

✅ All 38 API tests pass (cmj and dropjump)
✅ All 85 backend tests pass
✅ Type checking passes (pyright strict)
✅ Linting passes (ruff)
✅ Timing data flows correctly through entire pipeline
✅ JSON output includes timing_breakdown_ms
✅ Individual timing events properly logged at INFO level

## Files Modified

- `src/kinemotion/api.py` - Renamed `_generate_outputs()`, added timing capture for all stages
- `src/kinemotion/core/metadata.py` - Added `timing_breakdown` field to `ProcessingInfo`
- `src/kinemotion/core/debug_overlay_utils.py` - Added `reencode_duration_s` attribute
- `backend/src/kinemotion_backend/app.py` - Added 5 new timing event emissions
