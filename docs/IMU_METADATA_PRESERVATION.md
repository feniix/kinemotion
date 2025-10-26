# IMU Data and Video Editing Metadata Preservation

## What is IMU Data?

**IMU (Inertial Measurement Unit)** sensors in smartphones include:

### Accelerometer

- Measures linear acceleration in 3 axes (x, y, z)
- Captures device movement forces including gravity
- Provides direct measurement of acceleration during motion

### Gyroscope

- Measures angular velocity (rotation speed) around 3 axes
- Captures device orientation changes
- Helps distinguish gravity vector from actual acceleration

## How iPhones Store IMU Data

iPhone videos embed IMU sensor data in **extended metadata tracks** within the MOV container:

- **Location**: Stored as additional data streams alongside video/audio
- **Format**: Proprietary Apple metadata atoms
- **Timestamps**: Synchronized with video frames for precise alignment
- **Access**: Extractable via `ffprobe`, MediaInfo, or specialized tools

## Video Editing Impact on IMU Data

### ❌ Operations That Destroy IMU Data

**Re-encoding processes**:

- Photos app trimming/splitting
- Any video compression or format conversion that re-compresses video
- Online video converters
- Social media uploads (compress video)

**Why lost**: Re-encoding creates a new video file, only preserving standard metadata (creation date, GPS, camera settings). Extended sensor data tracks are stripped.

### ✅ Operations That Preserve IMU Data

**Container remuxing (stream copying)**:

- No re-compression of video/audio streams
- Metadata streams copied unchanged
- File container changes without touching contents

## Safe Video Processing Methods

### Container Format Conversion (MOV → MP4)

```bash
# Preserves all metadata including IMU
ffmpeg -i input.mov -c copy -map 0 output.mp4
```

### Video Trimming Without Re-encoding

```bash
# Trim while preserving all metadata
ffmpeg -i input.mov -ss 00:00:05 -t 00:00:10 -c copy segment.mov
```

### Professional Video Editors

Tools that preserve extended metadata:

- LumaFusion (iOS)
- Adobe Premiere Rush
- DaVinci Resolve (desktop)
- Final Cut Pro

## Testing IMU Data Preservation

### Check Original Metadata

```bash
ffprobe -v quiet -print_format json -show_streams -show_format input.mov
```

### Safe Conversion

```bash
ffmpeg -i input.mov -c copy -map 0 output.mp4
```

### Verify Preservation

```bash
ffprobe -v quiet -print_format json -show_streams -show_format output.mp4
```

## Practical Implications for Video Analysis

### Multi-Jump Videos

- **Don't split in Photos app**: IMU data will be lost
- **Keep original file**: Process time ranges without splitting
- **Use proper trimming**: `-c copy` preserves all data

### Workflow Recommendations

1. Record video with iPhone
2. Keep original file intact
3. Use FFmpeg for any necessary trimming/splitting
4. Process time ranges rather than creating separate files
5. Convert formats only with stream copying

## Key Commands Reference

```bash
# Inspect metadata streams
ffprobe -v quiet -select_streams s -show_entries stream=index,codec_name input.mov

# Safe format conversion
ffmpeg -i input.mov -c copy -map 0 output.mp4

# Safe trimming
ffmpeg -i input.mov -ss 00:01:30 -t 00:00:15 -c copy trimmed.mov

# Split into segments while preserving metadata
ffmpeg -i input.mov -c copy -map 0 -f segment -segment_time 10 output_%03d.mov
```
