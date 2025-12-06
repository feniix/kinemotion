# 📹 CMJ Recording Protocol: Optimal Camera Angle for MediaPipe

**Recommendation:** Use **45° oblique view** for best MediaPipe tracking accuracy

**Based on:** Empirical validation study (December 2025) showing 45° provides superior landmark tracking vs 90° lateral

______________________________________________________________________

## ⚡ Essential

| Element            | Specification                                |
| ------------------ | -------------------------------------------- |
| **Camera Angle**   | **45° oblique** (RECOMMENDED)                |
| **Why 45°?**       | Better MediaPipe landmark separation         |
| **Avoid 90°**      | Lateral view causes ankle landmark occlusion |
| **Resolution**     | 1080p minimum                                |
| **Frame Rate**     | 60fps minimum (120fps preferred)             |
| **Protocol**       | Hands on hips, 45° oblique view              |
| **Ankle Tracking** | Expect 120-150° at takeoff                   |

______________________________________________________________________

## 📸 Camera Setup

**Position:**

- Distance: 4m (ideal) or 3-5m
- Camera height: Mid-chest level of athlete (~100-120cm)
- **Camera angle: 45° oblique** (RECOMMENDED)
  - Position camera between lateral (90°) and frontal (0°)
  - Athlete visible from ~45° angle to side
  - ✅ **Why 45°?** Better ankle landmark separation for MediaPipe
  - ❌ **Avoid 90° lateral:** Causes ankle landmark overlap → poor tracking

**Configuration:**

- Format: MP4 or MOV, H.264 codec
- Lighting: Consistent, no shadows falling on the ankle
- Background: High-contrast backdrop relative to athlete's clothing
- Tripod: Secure and level

______________________________________________________________________

## 🎬 Recording Protocol

**Recommended Setup (45° oblique view):**

1. **Position camera at 45° angle** to athlete's side
1. **Mark athlete position:** Fixed floor position, unchanged clothing and footwear
1. **Record jumps:** One video per jump (1-3 jumps recommended)
1. **Maintain consistency:** Same angle, lighting, and distance throughout

**Important:**

- Capture one video per jump—do not record multiple jumps in a single file
- Keep camera at 45° oblique for all recordings
- Ensure ankle landmarks (heel, ankle, toes) are clearly visible and separated

______________________________________________________________________

### Why 45° Oblique? (Empirical Evidence)

**Validation Study Results (December 2025):**

- **45° oblique**: 140.67° average ankle angle ✅ (accurate)
- **90° lateral**: 112.00° average ankle angle ⚠️ (underestimated)
- **Root Cause**: At 90° lateral, one leg occludes the other → MediaPipe **confuses left/right feet**

**Key Insight:** MediaPipe cannot distinguish which foot is which at 90° lateral. At 45° oblique, both legs are clearly separated, enabling accurate left/right tracking.

______________________________________________________________________

## ✅ Critical Requirements

- ✅ **45° oblique camera angle** (optimal for MediaPipe)
- ✅ **Hands remain on hips** for the entire movement
- ✅ **Consistent lighting** (no shadows on ankle)
- ✅ **Separate video files** for each jump
- ✅ **Good form:** Deep countermovement, explosive extension, no arm swing
- ✅ **Ankle landmarks visible:** Heel, ankle, and toes clearly separated

❌ **Do not:**

- Use 90° pure lateral view (causes landmark occlusion)
- Include multiple jumps in a single video file
- Record with poor lighting (affects landmark detection)
- Position camera too close (\< 3m) or too far (> 5m)

______________________________________________________________________

## 📊 Frame Rate and Configuration

| Frame Rate | iPhone/Android Configuration                                     |
| ---------- | ---------------------------------------------------------------- |
| **60fps**  | Settings → Camera → Record Video: 1080p at 60fps                 |
| **120fps** | Settings → Camera → Record Video: 1080p at 120fps (if available) |

**Note:** 120fps requires better lighting than 60fps

______________________________________________________________________

## 📝 Pre-Recording Checklist

- [ ] Tripod is stable and level
- [ ] Athlete positioned with proper footwear
- [ ] Lighting is even throughout, no shadows on ankle
- [ ] Frame rate setting matches current group requirement
- [ ] Test 5-second recording completed successfully
- [ ] Full athlete body visible in frame (head to toes)
- [ ] Confirm hands positioned on hips before first jump

______________________________________________________________________

## 🎯 Acceptance Criteria

Each video must include:

- ✅ Clear side angle (45° or 90° view)
- ✅ Complete athlete body in frame
- ✅ Ankle well-illuminated and clearly visible
- ✅ Hands stay on hips throughout entire movement
- ✅ Deep countermovement followed by explosive push
- ✅ Visible plantarflexion (toe point) at liftoff
- ✅ Proper research technique throughout

______________________________________________________________________

## 📋 Quick Reference: Ankle Angles (at 45° view)

**Starting position (neutral):** ~80-90° (foot at right angle to shin)
**Liftoff (plantarflexion):** ~120-150° (foot pointing downward)
**Expected at takeoff:** ~140° average based on validation study
**Target progression:** At least 30° of ankle extension during jump

**Note:** These values are for 45° oblique view. 90° lateral view shows artificially low angles (~112° avg) due to landmark tracking issues.

______________________________________________________________________

## 📚 Technical References

See also:

- `docs/guides/camera-setup.md` - Camera positioning and equipment guidelines
- `docs/technical/framerate.md` - Frame rate considerations and temporal resolution
- Issue #10 - Ankle angle measurement validation study

**Version:** 2.0 | December 2025 (Updated with empirical validation findings)
