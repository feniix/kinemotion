---
title: iPhone Video Playback Issue - VP9 Codec Not Supported
type: note
permalink: fixes/i-phone-video-playback-issue-vp9-codec-not-supported
tags:
- video-codec
- ios
- bug-fix
- vp9
---

## Problem
Debug overlay videos were not playing on iPhone 16 Pro (Chrome/Safari) but worked on desktop browsers. The original video played fine on both.

## Root Cause
The debug video encoding was using VP9 codec (vp09), which is:
- ✅ Supported on desktop browsers (Chrome, Firefox)
- ✅ Can be encoded on Linux with libvpx
- ❌ NOT supported on iOS devices (iPhone, iPad)
- ❌ Not supported on iOS Safari or Chrome browsers

The codec selection logic tried in this order: `["avc1", "h264", "vp09", "mp4v"]`

On Cloud Run (Linux with ffmpeg), VP9 encoding succeeds, so VP9 videos were being generated and uploaded, causing playback failure on iOS.

## Solution
Removed VP9 from the codec selection list in `src/kinemotion/core/debug_overlay_utils.py`:
- Changed: `["avc1", "h264", "vp09", "mp4v"]`
- To: `["avc1", "h264", "mp4v"]`

## Why This Works
1. H.264 (avc1/h264) is supported on all platforms including iOS
2. Falls back to mp4v if H.264 unavailable
3. When mp4v is used, ffmpeg re-encodes to H.264 with yuv420p (maximum compatibility)
4. Result: All debug videos are iOS-compatible

## Video Codec Support Reference
### iOS (Safari, Chrome)
- H.264: ✅
- VP9: ❌
- AV1: ⚠️ (very limited)

### Desktop Browsers
- H.264: ✅
- VP9: ✅
- AV1: ⚠️ (limited)

## Impact
- Future debug videos will play on all devices including iPhone
- Desktop browsers unaffected
- No performance regression
- Existing VP9 videos won't be affected (users have the URLs)
