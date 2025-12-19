---
title: Kinemotion Logs in Cloud Logging - Ready
type: note
permalink: documentation/kinemotion-logs-in-cloud-logging-ready
tags:
- logging
- cloud-logging
- production
---

## Production Cloud Logging - Kinemotion Library Logs

### ✅ YES - Logs WILL reach Cloud Logging

Both backend AND kinemotion library logs output to `stdout` (not stderr), and Cloud Run automatically captures all stdout → Cloud Logging.

### 🎯 Current State

**Backend logs (structlog):**
- Format: Structured JSON
- ✅ Easily searchable/filterable in Cloud Logging

**Kinemotion logs (standard logging):**
- Format: Plain text message
- ✅ Will appear in Cloud Logging
- ⚠️ Less ideal for searching (not structured JSON)

### 📍 Where to Find Them

```bash
# View all logs (backend + kinemotion mixed)
gcloud run logs read kinemotion-backend --limit 100

# In Cloud Logging Console
https://console.cloud.google.com/logs
```

### 🔍 Example Output in Cloud Logging

```
[Backend] r2_debug_video_upload: duration_ms=3456, url=https://...
[Kinemotion] debug_video_codec_selected: codec=h264, dimensions=1920x1080, fps=60.0
[Kinemotion] debug_video_ffmpeg_reencoding_complete: duration_ms=8234
```

### ⚡ Current Implementation

Both use `logging.basicConfig(stream=sys.stdout)` configured in `logging_config.py:76`

### ✨ Recommendation

**Status: READY**
- Logs are going to Cloud Logging ✅
- You'll get all debug video codec details ✅
- May want structured JSON logging later for better filtering
