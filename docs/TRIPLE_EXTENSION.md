# Triple Extension Analysis for CMJ

## Overview

The CMJ debug video now includes **triple extension tracking** - real-time visualization of ankle, knee, and hip joint angles during the jump movement.

## What is Triple Extension?

**Triple extension** is the simultaneous extension (straightening) of three key joints during the propulsive phase of jumping:

1. **Ankle Extension** (plantarflexion) - Pushing through the toes
1. **Knee Extension** - Straightening the legs
1. **Hip Extension** - Driving the hips upward/forward

### Why It Matters

- **Performance indicator**: Proper triple extension maximizes power transfer
- **Technique assessment**: Identifies incomplete extension (power leaks)
- **Coaching tool**: Visual feedback for athletes
- **Progress tracking**: Monitor improvement over time

## Visualization in Debug Video

### Skeleton Overlay

**Color-coded segments:**

- 🟦 **Cyan**: Foot (heel → ankle/toe)
- 🔴 **Light Red**: Shin/tibia (ankle → knee)
- 🟢 **Light Green**: Femur/thigh (knee → hip)
- 🔵 **Light Blue**: Trunk (hip → shoulder)

### Joint Angle Display (Top Right Panel)

**Shows real-time angles:**

- **Ankle**: Dorsiflexion/plantarflexion angle
- **Knee**: Flexion/extension angle
- **Hip**: Flexion/extension angle
- **Trunk**: Forward/backward tilt

**Angle indicators at joints:**

- 🟢 Green ring: Extended (>160°) - Good!
- 🟠 Orange ring: Moderate (90-160°)
- 🔴 Red ring: Flexed (\<90°) - Deep squat

### Typical Angle Values

**At Lowest Point (Countermovement Bottom):**

```text
Ankle:  70-90°  (neutral to slight dorsiflexion)
Knee:   90-110° (moderate squat)
Hip:    90-110° (hip flexion)
Trunk:  0-20°   (slight forward lean)
```

**At Takeoff (Leaving Ground):**

```text
Ankle:  110-130° (strong plantarflexion)
Knee:   160-180° (near full extension)
Hip:    170-180° (full extension)
Trunk:  0-10°    (nearly vertical)
```

**During Flight:**

```text
All joints: ~180° (full extension)
```

## MediaPipe Limitations

### Ankle and Knee Visibility Issues

**Important Note**: In lateral (side) view videos, MediaPipe may struggle to detect ankle and knee landmarks:

**Test video results:**

- Heel: 100% visible ✓
- Hip: 100% visible ✓
- Shoulder: 100% visible ✓
- **Ankle: 27% visible** ⚠️
- **Knee: 18% visible** ⚠️

### Why This Happens

1. **Occlusion**: In side view, ankle/knee may be hidden by the body
1. **Angle**: MediaPipe trained primarily on frontal/oblique views
1. **Contrast**: Ankle/knee may blend with background
1. **Resolution**: Lower resolution reduces detection accuracy

### What We Do About It

**Graceful Degradation:**

- Shows "N/A" for angles that can't be calculated
- Draws available skeleton segments only
- Always shows hip-shoulder (trunk) which is reliably detected
- Falls back to left side if right side unavailable
- Lower visibility threshold (0.2) to capture more landmarks

**When Triple Extension Works Best:**

- ✅ Higher resolution videos (1080p+)
- ✅ Good contrast/lighting
- ✅ Athlete wearing contrasting clothing
- ✅ Clean background
- ✅ Slight oblique angle (not perfectly perpendicular)

**When It May Be Limited:**

- ⚠️ Perfect side view (perpendicular)
- ⚠️ Low resolution (720p or less)
- ⚠️ Poor lighting
- ⚠️ Busy background
- ⚠️ Loose/baggy clothing

## Interpreting Results

### Good Triple Extension Pattern

**Progressive extension from lowest point to takeoff:**

| Phase          | Ankle    | Knee     | Hip      | Notes                |
| -------------- | -------- | -------- | -------- | -------------------- |
| Lowest Point   | 75°      | 95°      | 100°     | Deep countermovement |
| Mid-Concentric | 95°      | 135°     | 145°     | Rapid extension      |
| **Takeoff**    | **120°** | **175°** | **178°** | **Full extension** ✓ |
| Flight         | 125°     | 180°     | 180°     | Maintained           |

**Indicators of good technique:**

- All three joints extend simultaneously
- Near-full extension at takeoff (knee >170°, hip >170°)
- Smooth progression through concentric phase

### Poor Extension Patterns

#### Problem 1: Incomplete knee extension

```text
Takeoff: Ankle 120°, Knee 150°, Hip 175°
→ Power leak: Not fully utilizing leg strength
```

#### Problem 2: Sequential extension (not simultaneous)

```text
Early concentric: Hip 170°, Knee 120°, Ankle 80°
→ Poor coordination: Extending in sequence instead of together
```

#### Problem 3: Excessive trunk lean

```text
Takeoff: Trunk 30° forward
→ Sub-optimal: Reduces vertical force component
```

## Usage

### CLI

```bash
# Generate debug video with triple extension
kinemotion cmj-analyze video.mp4 --output debug.mp4

# The debug video will automatically include:
# - Skeleton overlay
# - Joint angles (when visible)
# - Phase-coded visualization
```

### What You'll See

**Throughout the video:**

- Phase-colored overlay (standing/eccentric/concentric/flight/landing)
- Skeleton segments (whatever MediaPipe detects)
- Joint markers (white circles with black borders)

**When ankle/knee are visible (typically ~20-30% of frames):**

- Complete skeleton from heel to shoulder
- All joint angles displayed
- Angle arcs at each joint

**When ankle/knee are NOT visible:**

- Heel-hip-shoulder segments shown
- Trunk angle displayed
- "N/A" shown for missing angles

## Tips for Better Triple Extension Tracking

### Camera Setup

1. **Slight oblique angle** - Not perfectly perpendicular (try 80° instead of 90°)

   - Helps MediaPipe see ankle/knee better
   - Still captures vertical motion accurately

1. **Higher resolution** - 1080p minimum, 4K better

   - Improves landmark detection
   - Reduces tracking loss

1. **Contrasting clothing** - Wear fitted, solid-color clothing

   - Different color than background
   - Helps landmark detection

1. **Good lighting** - Even, bright lighting

   - No harsh shadows
   - Improves tracking accuracy

1. **Clean background** - Minimal visual clutter

   - Solid color wall ideal
   - Reduces false detections

### Video Quality Checklist

Before recording:

- ✅ 1080p or 4K resolution
- ✅ 60fps (better temporal resolution)
- ✅ Bright, even lighting
- ✅ Clean background
- ✅ Contrasting clothing
- ✅ Slightly oblique camera angle (~80°, not 90°)
- ✅ Stable tripod
- ✅ Full body in frame throughout jump

## Validation

The triple extension feature has been tested with:

✅ Real CMJ video (samples/cmjs/cmj.mp4)
✅ Handles missing landmarks gracefully
✅ Shows trunk angle throughout (100% visibility)
✅ Shows ankle/knee/hip when available (~20-30% of frames)
✅ All 70 tests passing
✅ No errors or crashes

## Limitations

**Current implementation:**

- Joint angles shown only when landmarks detected by MediaPipe
- In pure lateral view, ankle/knee have low visibility (~20-30%)
- Trunk angle (hip-shoulder) always available (100% visibility)

**Workarounds:**

- Use slightly oblique camera angle for better detection
- Focus on trunk angle for lateral videos
- Use frontal/oblique view if triple extension is primary goal
  - **Note**: Frontal view reduces jump height accuracy!

**Future improvements:**

- Could interpolate missing joint positions using IK
- Could use temporal smoothing to fill gaps
- Could estimate joint positions from hip-heel trajectory

## Example Output

**Debug video shows:**

```text
Frame 140-155 (Concentric phase):
  ┌─────────────────────┐
  │ TRIPLE EXTENSION    │
  │ Ankle:  N/A         │ ← Not detected
  │ Knee:   N/A         │ ← Not detected
  │ Hip:    N/A         │ ← Not detected
  │ Trunk:  12°         │ ← Always shown! ✓
  └─────────────────────┘

Frame 160-165 (Flight):
  ┌─────────────────────┐
  │ TRIPLE EXTENSION    │
  │ Ankle:  118° 🟠     │ ← Detected!
  │ Knee:   172° 🟢     │ ← Extended
  │ Hip:    175° 🟢     │ ← Extended
  │ Trunk:  5°          │ ← Vertical
  └─────────────────────┘
```

## Conclusion

Triple extension tracking is a **valuable coaching tool** that:

- ✅ Works well when MediaPipe detects ankle/knee
- ✅ Shows trunk angle throughout entire video
- ✅ Provides visual feedback on technique
- ⚠️ Limited by MediaPipe detection in pure lateral view
- 💡 Works better with slightly oblique camera angle

**For this CMJ video**: Trunk angle available 100% of the time, ankle/knee angles available ~20-30% (when visible during flight phase).

______________________________________________________________________

*Kinemotion CMJ Module - Triple Extension Feature*
*Biomechanical analysis with joint angle tracking*
