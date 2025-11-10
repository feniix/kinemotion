# Implementation Details

Critical implementation details for Kinemotion development.

## Aspect Ratio Preservation (core/video_io.py)

**Always:**

- Read first actual frame for dimensions: `frame.shape[:2]`
- Handle SAR (Sample Aspect Ratio) metadata with ffprobe
- Validate dimensions in `write_frame()` to prevent corruption

**Never:**

- Use `cv2.CAP_PROP_FRAME_WIDTH/HEIGHT` (wrong for rotated videos)

## Video Rotation (core/video_io.py)

- Extract rotation metadata from ffprobe (`side_data_list`)
- Apply rotation in `read_frame()` using `cv2.rotate()`
- Update width/height after 90°/-90° rotations

## JSON Serialization

**Always convert NumPy types:**

```python
"frame": int(self.frame) if self.frame is not None else None
```

**Never:**

```python
"frame": self.frame  # WRONG - int64 not JSON serializable
```

## CMJ Signed Velocity (cmj/analysis.py)

**Critical difference from drop jump:**

```python
# Drop jump: absolute velocity
velocities = compute_velocity_from_derivative(positions)  # Returns abs()

# CMJ: MUST use signed velocity
velocities = compute_signed_velocity(positions)  # Keeps sign
```

**Why:** CMJ needs to distinguish upward (negative) vs downward (positive) motion for phase detection.

## CMJ Backward Search (cmj/analysis.py)

**Algorithm:**

1. Find peak height first (global argmin)
1. Work backward: takeoff → lowest point
1. Work forward: landing after peak

**Why:** More robust than forward search, avoids false detections from video start.

## Frame Dimensions

OpenCV vs NumPy ordering:

- NumPy shape: `(height, width, channels)`
- OpenCV VideoWriter: `(width, height)` tuple

## Video Processing Gotchas

1. Read first frame for dimensions (not OpenCV properties)
1. Handle rotation metadata (mobile videos)
1. Preserve aspect ratio (SAR)
1. Validate dimensions in write_frame()

## CMJ Specific Gotchas

1. **Lateral view required** - Front view won't work (parallax errors)
1. **Signed velocity** - Critical for phase detection
1. **Backward search** - Requires complete video (not real-time)
1. **MediaPipe limitations** - Ankle/knee only 18-27% visible in side view
