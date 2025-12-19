---
title: Backend Debug Video Logging Reference
type: note
permalink: documentation/backend-debug-video-logging-reference
tags:
- logging
- debug-video
- backend
- monitoring
---

## Backend Debug Video Logging

**File**: `backend/src/kinemotion_backend/services/analysis_service.py`

### Request Flow Log Events:
1. `validating_video_file_completed` - Input validation time
2. `saving_uploaded_file_completed` - File size, save duration
3. `debug_video_path_created` - Temp file created (if debug=true)
4. `video_processing_started`
   - **[KINEMOTION LOGS HAPPEN HERE]**
   - Examples: codec selection, FFmpeg re-encoding, resolution optimization
5. `video_processing_completed` - Total processing time
6. `uploading_original_video` - Original video upload starts
7. `original_video_uploaded` - URL of uploaded video
8. `uploading_debug_video` - Debug video upload starts
9. `r2_debug_video_upload` - Duration, URL, storage key
   - OR `debug_video_empty_skipping_upload` if video failed
10. `video_analysis_completed` - Total duration, metrics count

### Key Metrics to Monitor:
- `video_processing_completed: duration_ms` → Total analysis time
- `r2_debug_video_upload: duration_ms` → Upload performance
- Check both backend logs AND kinemotion library logs for full picture

### Finding Logs:
- **Development**: Terminal/IDE console (human-readable)
- **Production (Cloud Run)**: Google Cloud Logging with JSON format
- Filter: `event="r2_debug_video_upload"` or `event="debug_video_codec_selected"`

### Troubleshooting:
- Missing debug video? Check `debug_video_path_created`
- Empty video? Check `debug_video_empty_skipping_upload` warning
- Slow? Check `video_processing_completed` for analysis time + `r2_debug_video_upload` for network
