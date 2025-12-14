---
title: Backend Granular Logging Implementation
type: note
permalink: development/backend-granular-logging-implementation
---

# Backend Granular Logging Implementation

## Complete Logging Coverage

All logging has been restored and enhanced with comprehensive instrumentation throughout the video analysis pipeline.

## Logging Stages by Category

### 1. Endpoint Level (routes/analysis.py) - 2 stages
- **`analyzing_video_started`** - Before analysis begins (includes jump_type, quality, debug flags)
- **`analyzing_video_completed`** - After analysis finishes (includes duration_ms, status_code)

### 2. Validation & Setup (analysis_service.py) - 5 stages
- **`validating_video_file`** - Starting video file validation
- **`validating_video_file_completed`** - File validation complete (duration_ms)
- **`validating_jump_type`** - Starting jump type validation (includes jump_type)
- **`validating_jump_type_completed`** - Jump type validation complete (normalized_jump_type, duration_ms)
- **`generating_storage_key`** - Starting storage key generation (includes filename)
- **`generating_storage_key_completed`** - Key generation complete (storage_key, duration_ms)

### 3. File Operations (analysis_service.py) - 2 stages
- **`saving_uploaded_file`** - Starting file save to temp disk (temp_path)
- **`saving_uploaded_file_completed`** - File save complete (file_size_mb, duration_ms)

### 4. Video Processing Pipeline (analysis_service.py) - 2 main + N granular
- **`video_processing_started`** - Starting core kinemotion analysis
- **Individual pipeline stages** (via timer.get_metrics()) - Each stage from kinemotion library:
  - `frame_read` - Reading video frames
  - `frame_rotation` - Rotating frames for correct orientation
  - `frame_conversion` - Converting frame formats
  - `mediapipe_inference` - MediaPipe pose detection (DOMINANT: 88-94% of time)
  - `landmark_extraction` - Extracting pose landmarks
  - `smoothing_outlier_rejection` - Outlier rejection in smoothing
  - `smoothing_bilateral` - Bilateral filter smoothing
  - `smoothing_savgol` - Savitzky-Golay smoothing
  - `parameter_auto_tuning` - Auto-tuning algorithm parameters
  - `vertical_position_extraction` - Extracting Y-axis positions
  - `phase_detection` - Detecting jump phases (CMJ-specific)
  - `dj_detect_drop_start` - Detecting drop start (Drop Jump-specific)
  - `dj_find_phases` - Finding drop jump phases
  - `dj_identify_contact` - Ground contact detection
  - `dj_analyze_flight` - Analyzing flight phase
  - `dj_compute_velocity` - Computing velocity
  - `dj_find_contact_frames` - Finding contact frames
  - `cmj_compute_derivatives` - Computing derivatives
  - `cmj_find_takeoff` - Finding takeoff point
  - `cmj_find_lowest_point` - Finding lowest point
  - `cmj_find_landing` - Finding landing point
  - `cmj_find_standing_end` - Finding standing phase end
  - `metrics_calculation` - Computing final metrics
  - `quality_assessment` - Quality assessment
  - `debug_video_generation` - Generating debug overlay video
  - `debug_video_resize` - Resizing debug video frames
  - `debug_video_write` - Writing debug video to disk
  - `debug_video_copy` - Copying frames for debug video
  - `debug_video_draw` - Drawing annotations on debug video
- **`video_processing_completed`** - Processing complete (total_duration_s, duration_ms)

### 5. Cloud Storage Operations (analysis_service.py) - 5 stages
- **`uploading_original_video`** - Starting upload (storage_key)
- **`original_video_uploaded`** - Upload complete (url)
- **`uploading_analysis_results`** - Starting results JSON upload (storage_key)
- **`r2_results_upload`** - Results upload complete (duration_ms, url, key)
- **`uploading_debug_video`** - Starting debug video upload (storage_key)
- **`r2_debug_video_upload`** - Debug video upload complete (duration_ms, url, key)
- **`debug_video_empty_skipping_upload`** - Debug video empty, skipping upload

### 6. Response Building & Cleanup (analysis_service.py) - 3 stages
- **`response_serialization`** - Converting metrics to JSON response (duration_ms)
- **`cleaning_up_temporary_files`** - Starting cleanup
- **`temp_file_cleanup`** - Cleanup complete (duration_ms)

### 7. Success Summary (analysis_service.py) - 1 stage
- **`video_analysis_completed`** - Final summary (jump_type, duration_ms, metrics_count)

### 8. Error Handling (routes/analysis.py + analysis_service.py) - 2 stages
- **`analyze_endpoint_validation_error`** - (WARNING) Validation failed at endpoint
- **`analyze_endpoint_error`** - (ERROR) Unexpected error at endpoint
- **`video_analysis_validation_error`** - (ERROR) Validation failed in service
- **`video_analysis_failed`** - (ERROR) Processing failed in service

## Total Logging Coverage

**Total granular logging events: 30+ individual events** including:
- 2 endpoint-level events
- 5 validation/setup events
- 2 file operation events
- 2 + N processing pipeline events (N = individual kinemotion stages)
- 5 cloud storage events
- 3 response/cleanup events
- 1 success summary event
- 4 error events

## Key Features

✅ **End-to-End Visibility** - Every major operation emits events
✅ **Detailed Timing** - All operations include duration_ms where relevant
✅ **Contextual Data** - Each log includes relevant identifiers (storage_key, filename, urls, etc.)
✅ **Bottleneck Identification** - MediaPipe pose tracking consistently shows 88-94% of total time
✅ **Test Coverage** - All 89 backend tests pass with instrumentation
✅ **Code Quality** - Passes ruff linting and pyright type checking
✅ **Request Tracing** - Can follow requests through entire pipeline via upload_id in error cases
✅ **Performance Metrics** - Granular timing for optimization decisions

## Log Output Examples

### Successful Analysis Flow
```
analyzing_video_started jump_type=cmj quality=balanced debug=false
validating_video_file
validating_video_file_completed duration_ms=1.2
validating_jump_type jump_type=cmj
validating_jump_type_completed normalized_jump_type=cmj duration_ms=0.5
generating_storage_key filename=video.mp4
generating_storage_key_completed storage_key=abc123 duration_ms=0.8
saving_uploaded_file temp_path=/tmp/video.mp4
saving_uploaded_file_completed file_size_mb=45.23 duration_ms=250.4
video_processing_started
frame_read duration_ms=324.5
mediapipe_inference duration_ms=5183.1
smoothing_bilateral duration_ms=188.6
metrics_calculation duration_ms=0.2
video_processing_completed total_duration_s=5.72 duration_ms=5721.4
uploading_original_video storage_key=abc123
original_video_uploaded url=https://r2.example.com/videos/abc123.mp4
uploading_analysis_results storage_key=abc123
r2_results_upload duration_ms=234.0 url=https://r2.example.com/results/abc123.json key=results/abc123.json
response_serialization duration_ms=1.5
cleaning_up_temporary_files
temp_file_cleanup duration_ms=45.2
video_analysis_completed jump_type=cmj duration_ms=5721.4 metrics_count=12
analyzing_video_completed duration_ms=6200.5 status_code=200
```

## Implementation Files

- **routes/analysis.py** - Endpoint-level logging (analyzing_video_started/completed)
- **services/analysis_service.py** - Core pipeline logging (validation, processing, storage, cleanup)
- **services/video_processor.py** - Video processor logging wrapper

## Testing

✅ All 89 backend tests pass
✅ All 16 API endpoint tests pass
✅ Ruff linting: All checks passed
✅ Pyright type checking: 0 errors
✅ No breaking changes to existing functionality
