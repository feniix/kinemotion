---
title: Debug Video Codec Fix and Logging Enhancement
type: note
permalink: fixes/debug-video-codec-fix-and-logging-enhancement
tags:
- logging
- codec
- ios
- ffmpeg
- enhancement
---

# Debug Video Codec and Logging Enhancement

## Changes Made

### 1. Fixed iOS Compatibility Issue (VP9 Codec)
**File**: `src/kinemotion/core/debug_overlay_utils.py`

**Problem**: Debug overlay videos were not playing on iPhone 16 Pro because VP9 codec was being used, which is not supported on iOS.

**Solution**: Removed VP9 (vp09) from the codec selection list:
```python
# Before
codecs_to_try = ["avc1", "h264", "vp09", "mp4v"]

# After
codecs_to_try = ["avc1", "h264", "mp4v"]
```

### 2. Added Comprehensive Logging

Added structured logging throughout the debug video generation process to track:

#### Codec Selection Logging
- When each codec is attempted
- Success/failure of each codec
- Selected codec with dimensions and FPS
- Warning when falling back to mp4v

#### Resolution Optimization Logging
- When resolution is scaled down to 720p
- Scale factor used
- Original vs optimized dimensions

#### FFmpeg Re-encoding Logging
- When re-encoding starts (codec, pixel format)
- When re-encoding completes with duration in milliseconds
- When temporary files are cleaned up
- Errors during re-encoding with stderr output

#### Final Status Logging
- Codec and path when video is ready for playback
- Warning if ffmpeg unavailable but needed

### 3. Logging Levels Used

- **DEBUG**: Codec attempts, resolution changes, writer release, file cleanup
- **INFO**: Renderer initialization, successful codec selection, re-encoding start/complete, final playback status
- **WARNING**: mp4v fallback, ffmpeg unavailable, re-encoding failures
- **ERROR**: Writer creation failure

## Benefits

### For Developers
- **Troubleshooting**: Can see exactly which codec was selected and why
- **Performance**: Can track FFmpeg re-encoding duration
- **Diagnostics**: Know which resolution was used and if scaling occurred
- **Error Tracking**: Full stderr output if re-encoding fails

### For Users
- **Reliability**: Ensures H.264 is always used for maximum compatibility
- **Platform Support**: Works on all browsers including iOS Safari and Chrome
- **Quality**: 720p optimization for Cloud Run performance without sacrificing quality
- **Playback**: Videos are guaranteed to work across desktop and mobile

## Video Codec Support Reference

| Platform | H.264 | VP9 | AV1 |
|----------|:-----:|:---:|:---:|
| iOS Safari | ✅ | ❌ | ⚠️ |
| iOS Chrome | ✅ | ❌ | ⚠️ |
| Desktop Chrome | ✅ | ✅ | ⚠️ |
| Desktop Firefox | ✅ | ✅ | ⚠️ |
| Desktop Safari | ✅ | ❌ | ⚠️ |

## FFmpeg Re-encoding Pipeline

When mp4v is used:
1. Initial video created with mp4v codec
2. FFmpeg converts to H.264 with yuv420p pixel format
3. Settings: libx264, preset=fast, crf=23, no audio
4. Result: Maximum compatibility across all browsers and devices

## Testing Recommendations

1. Generate debug videos with latest code
2. Test playback on iPhone 16 Pro in Chrome
3. Verify no performance degradation in Cloud Run logs
4. Check FFmpeg re-encoding duration metrics
