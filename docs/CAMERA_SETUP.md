# Camera Setup Guide

> **Versión en español disponible:** [CAMERA_SETUP_ES.md](CAMERA_SETUP_ES.md)

This guide provides best practices for recording drop jump videos to ensure accurate analysis with kinemotion.

## Overview

Proper camera positioning is critical for accurate drop jump analysis. The current implementation uses **2D sagittal plane analysis**, which requires a side-view camera setup to capture vertical motion accurately.

## Drop Jump Camera Setup

### Required Camera Position

Camera must be positioned at a side view angle, perpendicular to the sagittal plane (90°).

#### Camera Positioning Diagram

```text
                    Top View (looking down from above)
                    ===================================

                       [Drop Box]
    [Camera]               |
 Positioned to the SIDE  → | (athlete drops straight down)
      3-5m                 |
(perpendicular to athlete) ↓
                           ⬤  ← Landing spot (next to box)
```

**Key Points:**

- **Horizontal alignment:** Camera positioned to the **side** of the drop-jump area, centered between box and landing spot
- **Perpendicular angle:** 90° to the plane of movement (athlete moves vertically, not toward/away from camera)
- **Distance:** 3-5 meters away
- **Height:** Camera lens at athlete's hip height

### Setup Requirements

| Parameter           | Specification                              | Reason                                     |
| ------------------- | ------------------------------------------ | ------------------------------------------ |
| **Camera Position** | Side view, perpendicular to sagittal plane | Captures vertical motion (y-axis) directly |
| **Distance**        | 3-5 meters from athlete                    | Full body visibility without distortion    |
| **Height**          | Camera lens at athlete's hip height        | Minimizes perspective distortion           |
| **Framing**         | Head to feet visible throughout jump       | Ensures all landmarks tracked              |
| **Orientation**     | Landscape (horizontal)                     | Wider field of view for movement           |

### Detailed Instructions

#### 1. Camera Positioning

**Horizontal Position:**

- Place camera **perpendicular** to the athlete's jumping plane (90° angle)
- **Align camera horizontally at a point between the box and landing spot**
  - The landing spot is immediately adjacent to the box (athlete drops straight down)
  - Camera should be centered on this drop-jump area
  - This ensures the athlete moves primarily vertically in frame, not toward/away from camera
- Position camera to capture the full drop-jump sequence:
  - Standing on box
  - Dropping down (right next to box)
  - Landing on ground (immediately adjacent to box)
  - Jumping up
  - Landing again

**Vertical Position:**

- Set camera lens at approximately **hip height** of the athlete
- This minimizes perspective distortion at the extremes (head and feet)
- For adjustable tripods: typically 0.8-1.2m height

**Distance:**

- **Minimum 3 meters**: Closer increases perspective distortion
- **Maximum 5 meters**: Farther reduces tracking accuracy
- **Optimal ~4 meters**: Balance of accuracy and field of view

#### 2. Framing

**Full Body Coverage:**

```text
Frame boundaries:
┌──────────────────────┐
│        [head]        │ ← Top: 10-20cm above head at full standing
│                      │
│         /|\          │
│        / | \         │
│         / \          │ ← Body: Entire torso and limbs visible
│        /   \         │
│       /     \        │
│      [feet]          │ ← Bottom: Include floor/landing surface
└──────────────────────┘
```

**Important:**

- ✅ Keep athlete centered in frame throughout jump
- ✅ Include landing surface (floor) in frame
- ✅ Leave margin above head (~10-20cm) for full jump height
- ❌ Don't crop any body parts during movement
- ❌ Don't pan or zoom during recording

#### 3. Lighting

**Recommended:**

- Even lighting across athlete's body
- Avoid backlighting (athlete as silhouette)
- Indoor: overhead gym lights typically sufficient
- Outdoor: avoid harsh shadows (overcast conditions ideal)

**Why it matters:**

- MediaPipe relies on visual contrast for landmark detection
- Poor lighting reduces landmark visibility scores
- Auto-tuning may compensate but accuracy decreases

#### 4. Background

**Best practices:**

- Plain, contrasting background (e.g., wall behind athlete)
- Avoid busy backgrounds (multiple people, equipment)
- Minimize movement in background

**Why it matters:**

- MediaPipe works best with clear figure-ground separation
- Busy backgrounds can interfere with pose detection

### Recording Settings

| Setting           | Recommendation         | Notes                                            |
| ----------------- | ---------------------- | ------------------------------------------------ |
| **Frame Rate**    | 30-60 fps              | Higher is better; auto-tuning adjusts parameters |
| **Resolution**    | 1080p minimum          | Higher resolution improves landmark detection    |
| **Orientation**   | Landscape (horizontal) | Better field of view for lateral framing         |
| **Format**        | MP4, MOV, AVI          | Most common video formats supported              |
| **Stabilization** | Use tripod             | Hand-held videos may reduce accuracy             |

### Common Mistakes to Avoid

#### ❌ Front/Back View Instead of Side View

```text
❌ INCORRECT: Front view

    [Camera]
       ↓
      ---
     | O |  ← Athlete facing camera
      ---
     / | \
      / \
```

**Problem:** Vertical motion becomes depth (z-axis), which is:

- Less accurate in 2D computer vision
- Not validated in research literature
- Cannot measure jump height reliably

**Solution:** Always use side view as specified above.

#### ❌ Camera Too Close (\< 3m)

**Problem:**

- Perspective distortion increases measurement error
- Risk of athlete moving out of frame
- Wide-angle lens distortion at edges

#### ❌ Camera Too High/Low

**Problem:**

- Looking down/up at athlete creates parallax error
- Hip height positioning minimizes this effect

#### ❌ Camera Angle Not Perpendicular

```text
❌ INCORRECT: Camera at 45° angle

         [Camera]
           ↙
         /
        /
      ⬤ ← Athlete
```

**Problem:**

- Motion path shortened by projection angle
- Jump height underestimated
- Ground contact time calculation affected

**Solution:** Position camera at true 90° angle (perpendicular to sagittal plane).

### Camera Setup Checklist

Before recording, verify:

- [ ] Camera on stable tripod (no movement during recording)
- [ ] Side view: Camera perpendicular to athlete's jumping plane
- [ ] Distance: 3-5 meters from drop box/landing area
- [ ] Height: Camera lens at athlete's hip height
- [ ] Framing: Full body visible (head to feet + margin)
- [ ] Lighting: Even, no harsh shadows or backlighting
- [ ] Background: Plain, minimal distractions
- [ ] Settings: 30+ fps, 1080p+ resolution, landscape orientation
- [ ] Test recording: Verify athlete stays in frame throughout jump

## Why Side View?

### Biomechanical Rationale

Drop jumps are **primarily vertical movements** in the sagittal plane:

1. **Drop phase**: Vertical descent (gravity)
1. **Landing**: Vertical deceleration (ground reaction force)
1. **Ground contact**: Minimal vertical displacement
1. **Takeoff**: Vertical acceleration (jump)
1. **Flight**: Vertical motion (parabolic trajectory)

### Measurement Requirements

**What we measure:**

- ✅ **Vertical displacement** (y-axis): Jump height
- ✅ **Vertical velocity** (dy/dt): Contact detection
- ✅ **Joint angles in sagittal plane**: Ankle, knee, hip extension

**What we don't need (for drop jumps):**

- ❌ Horizontal displacement (x, z): Should be minimal in proper technique
- ❌ Frontal plane motion: Not primary metric for drop jumps
- ❌ Rotation/twist: Not applicable to drop jumps

### Research Validation

Standard protocols for drop jump biomechanics research universally employ **side-view camera positioning**:

- Direct visualization of sagittal plane kinematics
- Accurate vertical displacement measurement
- Clear observation of triple extension (ankle-knee-hip)
- Validated against force plates and 3D motion capture

**Reference:** 2D sagittal plane analysis shows strong correlation (r = 0.51-0.93) with 3D motion capture for lower body joint angles during jumping tasks.

## Video Quality Impact on Analysis

### High Quality Video (Recommended)

**Characteristics:**

- 60 fps frame rate
- 1080p or 4K resolution
- Good lighting (landmark visibility > 0.7)
- Stable camera (tripod)
- Clean background

**Auto-tuning adjustments:**

- Minimal smoothing (preserves detail)
- Bilateral filter disabled (not needed)
- Standard confidence thresholds

**Expected accuracy:** Research-grade measurements

### Medium Quality Video (Acceptable)

**Characteristics:**

- 30 fps frame rate
- 720p resolution
- Moderate lighting (landmark visibility 0.4-0.7)
- Stable camera
- Some background clutter

**Auto-tuning adjustments:**

- Moderate smoothing
- Bilateral filter enabled
- Standard confidence thresholds

**Expected accuracy:** Good for training and assessment

### Low Quality Video (May Work)

**Characteristics:**

- \< 30 fps frame rate
- \< 720p resolution
- Poor lighting (landmark visibility \< 0.4)
- Hand-held camera (slight movement)
- Busy background

**Auto-tuning adjustments:**

- Aggressive smoothing
- Bilateral filter enabled
- Lowered confidence thresholds

**Expected accuracy:** Reduced accuracy, use for preliminary screening only

**Recommendation:** If possible, re-record with better conditions.

## Multi-Camera Setup (Future Feature)

**Note:** Current implementation uses single side-view camera. Future versions may support multi-camera analysis.

### Potential Multi-Camera Configuration

```text
                Top View
                ========

    [Camera 2]
    (Front view)
         ↓

         ⬤  <-- Athlete
         |

[Camera 1] ◄──┤
(Side view)
```

**Camera 1 (Side view):** Sagittal plane analysis

- Jump height
- Ground contact time
- Triple extension angles

**Camera 2 (Front view):** Frontal plane analysis (requires 3D implementation)

- Knee valgus/varus
- Bilateral asymmetries
- Lateral stability

**Status:** Not currently supported. Stay tuned for future updates.

## Troubleshooting

### "Poor landmark visibility" warning

**Cause:** MediaPipe cannot reliably detect body landmarks

**Solutions:**

1. Improve lighting (add light source, avoid shadows)
1. Ensure contrasting background
1. Check camera focus (athlete should be in sharp focus)
1. Move camera closer (but maintain 3m minimum)
1. Increase video resolution

### Jump height seems incorrect

**Possible causes:**

1. Camera angle not perpendicular (jump path appears shorter)
1. Missing `--drop-height` calibration parameter
1. Athlete moving horizontally during jump (drift)
1. Poor tracking quality (check debug video overlay)

**Solutions:**

1. Verify camera is at true 90° angle
1. Provide known drop box height: `--drop-height 0.40`
1. Ensure athlete jumps straight up (coaching)
1. Improve video quality as described above

### "No drop jump detected" error

**Possible causes:**

1. Video doesn't include full sequence (missing standing on box phase)
1. Camera framing cuts off athlete
1. Very poor tracking quality

**Solutions:**

1. Start recording before athlete steps on box
1. Ensure full body visible throughout
1. Improve video quality
1. Use manual `--drop-start-frame` if auto-detection fails

## Camera Equipment Recommendations

### Budget Option ($100-300)

- Smartphone on tripod (iPhone, Android with 1080p/60fps)
- Inexpensive tripod with phone mount
- Free video recording apps with manual controls

**Pros:** Accessible, portable, sufficient quality
**Cons:** Limited zoom, smaller sensor

### Mid-Range Option ($300-800)

- Action camera (GoPro, DJI) with wide FOV
- Sturdy tripod
- Good in varied lighting conditions

**Pros:** Durable, high frame rates (120fps+), good image quality
**Cons:** Wide-angle distortion at edges

### Professional Option ($800+)

- Mirrorless/DSLR camera (Sony, Canon, Nikon)
- Professional tripod with fluid head
- Prime or zoom lens (24-70mm range)

**Pros:** Best image quality, manual control, interchangeable lenses
**Cons:** Expensive, more complex setup

**Recommendation:** Most smartphones (2020+) are sufficient for drop jump analysis. Prioritize proper positioning over expensive equipment.

## Summary

**Key Takeaways:**

1. ✅ **Side view is mandatory** for current drop jump analysis
1. ✅ Position camera **perpendicular** to jumping plane
1. ✅ Maintain **3-5 meter distance** at **hip height**
1. ✅ Frame **full body** with margin for jump height
1. ✅ Use **tripod** for stability
1. ✅ Record at **30+ fps, 1080p+ resolution**
1. ✅ Ensure **good lighting** and **clean background**

Follow these guidelines to maximize analysis accuracy and reliability.

## Related Documentation

- **[Versión en Español](CAMERA_SETUP_ES.md)** - Spanish version of this guide
- [CLI Parameters Guide](PARAMETERS.md) - Detailed explanation of all analysis parameters
- [Bulk Processing Guide](BULK_PROCESSING.md) - Processing multiple videos efficiently
- Main [CLAUDE.md](../CLAUDE.md) - Complete project documentation
