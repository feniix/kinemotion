# Camera Setup Guide

> **Versión en español disponible:** [camera-setup.md](../translations/es/camera-setup.md)

This guide provides best practices for recording drop jump and CMJ videos to ensure accurate analysis with kinemotion.

## Overview

Kinemotion now supports **45° angle camera positioning** as the standard setup, providing better landmark visibility and tracking accuracy compared to pure lateral views. This guide covers:

1. **Single iPhone at 45°** (recommended standard setup)
1. **Dual iPhone stereo setup** (advanced - for improved accuracy)

**Why 45° instead of lateral (90°)?**

Research shows that camera viewing angle significantly affects pose estimation accuracy. The 45° angle provides:

- **Better visibility**: 40-60% ankle/knee visibility vs 18-27% in lateral view
- **Reduced occlusion**: Both legs more visible (less self-occlusion)
- **Good sagittal plane capture**: Still measures jump height and vertical motion accurately
- **Practical compromise**: Between frontal (high visibility, poor depth) and lateral (pure sagittal, high occlusion)

______________________________________________________________________

## Setup 1: Single iPhone at 45° (Standard)

### Single Camera Positioning

**Recommended for:** Most users, training environments, individual athlete assessment

#### Top View Diagram (Single Camera)

```text
                    N (North - Athlete faces forward)
                    ↑

        [Drop Box]  |
            |       |
            ↓       |
           ⬤ Athlete (jumps straight up/down)
            ↘
             ↘ 45° angle
              ↘
            [iPhone on Tripod]

Side view visualization:

    Athlete           iPhone
       ⬤  - - - - - - [📱]
                      ↑
                   3-5m distance
                   Hip height (130-150cm)
```

**Key positioning:**

- **Angle:** 45° from athlete's sagittal plane (between side and front)
- **Distance:** 3-5 meters (optimal: 4 meters)
- **Height:** Hip level (130-150 cm from floor)
- **Orientation:** Landscape mode (horizontal)

### Detailed Setup Instructions

#### 1. Physical Placement

**Step-by-step:**

1. **Position athlete at drop box** - Have athlete stand at their jumping position
1. **Identify sagittal plane** - Imagine a line from front to back through athlete's center
1. **Mark 45° position** - From athlete's side, move 45° toward the front
   - If athlete faces North, camera should be Southeast or Southwest
   - Camera sees athlete's front-side (not pure profile)
1. **Set distance** - Measure 3-5m from athlete's jumping position
1. **Set height** - Camera lens at athlete's hip height (130-150 cm typical)
1. **Level tripod** - Ensure camera is level (not tilted up/down)

#### 2. Frame Composition

**At 1080p (1920x1080), frame athlete like this:**

```text
|--------------------------|
|    [10-15% margin top]   |
|                          |
|         👤 Athlete       | ← Full body visible
|          ↕               | ← Entire jump height
|         / \              | ← Both legs visible
|        /   \             |
|    [Landing Area]        | ← Floor visible
|   [10-15% margin bottom] |
|--------------------------|
```

**Checklist:**

- ✅ Entire body visible (head to feet)
- ✅ 10-15% margin above head (for jump height)
- ✅ Landing surface visible in frame
- ✅ Athlete stays centered throughout movement
- ✅ Both legs visible (key advantage of 45° angle)
- ❌ Don't crop body parts
- ❌ Don't pan or zoom during recording

#### 3. Camera Settings

| Setting           | Specification              | Reason                                            |
| ----------------- | -------------------------- | ------------------------------------------------- |
| **Resolution**    | 1080p (1920x1080)          | Minimum for accurate landmark detection           |
| **Frame Rate**    | 60 fps (30 fps minimum)    | 60 fps recommended for short ground contact times |
| **Orientation**   | Landscape (horizontal)     | Wider field of view                               |
| **Focus**         | Manual (locked on athlete) | Prevents autofocus hunting                        |
| **Exposure**      | Locked/manual              | Consistent brightness throughout video            |
| **Shutter Speed** | 1/120s or faster           | Reduces motion blur                               |
| **Stabilization** | Tripod (required)          | Eliminates camera shake                           |

**iPhone-specific settings:**

```text
Camera app → Settings:
- Format: Most Compatible (H.264)
- Record Video: 1080p at 60fps
- Lock Focus: Tap and hold on athlete
- Lock Exposure: Swipe up/down to adjust, then lock
```

#### 4. Lighting

**Best practices:**

- Even lighting across athlete's body
- Avoid backlighting (athlete as silhouette)
- Indoor: Overhead gym lights typically sufficient
- Outdoor: Overcast conditions ideal (soft, even light)

**Why it matters:** MediaPipe relies on visual contrast. Poor lighting reduces landmark visibility scores and analysis accuracy.

#### 5. Background

**Optimal:**

- Plain wall or solid color background
- High contrast with athlete's clothing
- Minimal movement in background

**Avoid:**

- Busy backgrounds (equipment, other people)
- Similar colors to athlete's clothing
- Reflective surfaces (mirrors, windows)

### Expected Performance

**Improvements over lateral (90°) view:**

| Metric                       | Lateral View (90°) | 45° Angle    | Improvement     |
| ---------------------------- | ------------------ | ------------ | --------------- |
| **Ankle/Knee Visibility**    | 18-27%             | 40-60%       | +100-150%       |
| **Joint Angle Accuracy**     | ~10-15° error      | ~8-12° error | ~20-30% better  |
| **Detection Reliability**    | Good               | Excellent    | More consistent |
| **Ground Contact Detection** | Challenging        | Easier       | More robust     |

**Limitations:**

- Still monocular (depth estimation noisy)
- No biomechanical constraints (vs Pose2Sim)
- Not research-grade (for that, use dual camera setup)

### Camera Setup Checklist

Before recording, verify:

- [ ] iPhone on stable tripod (no movement during recording)
- [ ] Camera at 45° angle from athlete's sagittal plane
- [ ] Distance: 3-5 meters from landing area
- [ ] Height: Camera lens at athlete's hip height (130-150cm)
- [ ] Framing: Full body visible (head to feet + 10-15% margins)
- [ ] Settings: 1080p, 60 fps, landscape orientation
- [ ] Focus: Locked on athlete (tap and hold)
- [ ] Exposure: Locked (consistent lighting)
- [ ] Lighting: Even, no harsh shadows or backlighting
- [ ] Background: Plain, minimal distractions
- [ ] Test recording: Athlete stays in frame throughout jump

______________________________________________________________________

## Setup 2: Dual iPhone Stereo (Advanced)

### When to Use Dual Camera Setup

**Recommended for:**

- Research applications requiring higher accuracy
- Elite athlete assessment
- When depth accuracy is critical
- Biomechanical analysis requiring joint angles

**Benefits over single camera:**

- **~50% error reduction** (30.1mm RMSE vs 56.3mm monocular)
- **Accurate 3D reconstruction** (eliminates depth ambiguity)
- **Better landmark visibility** (each camera sees different angles)
- **Research-grade accuracy** (with proper calibration and processing)

**Requirements:**

- 2 iPhones (same model recommended for matching settings)
- 2 tripods
- Calibration pattern (ChArUco board or checkerboard)
- More complex processing workflow

### Dual Camera Positioning

#### Optimal configuration: ±45° from sagittal plane, 90° separation

#### Top View Diagram (Dual Camera)

```text
                    N (Athlete faces forward)
                    ↑

    [iPhone 2]      |      [iPhone 1]
    (Left side)     |      (Right side)
         ↘          |          ↙
          ↘ 45°     |      45° ↙
           ↘        |        ↙
             ↘   [Box]    ↙
               ↘    |   ↙
                 ↘  ↓ ↙
                   ⬤ Athlete

    Total separation: 90° (optimal for triangulation)
```

**Why 90° separation?**

Research by Pagnon et al. (2022) and Dill et al. (2024) found 90° angle between cameras optimal for stereo 3D reconstruction. This balances:

- Triangulation accuracy (wider angles better)
- Overlapping field of view (cameras must see same landmarks)
- Practical setup constraints

### Detailed Dual Camera Setup

#### Step 1: Position Both Cameras

**iPhone 1 (Right camera):**

- Position 45° from athlete's right side
- If athlete faces North, camera is Southeast
- Distance: 3-5m from athlete
- Height: Hip level (130-150cm)

**iPhone 2 (Left camera):**

- Position 45° from athlete's left side
- If athlete faces North, camera is Southwest
- Distance: 3-5m from athlete (same as iPhone 1)
- Height: Hip level (match iPhone 1 exactly)

**Critical alignment:**

- Both cameras at **same height** (±2cm tolerance)
- Both cameras at **same distance** from athlete (±10cm tolerance)
- Both cameras **level** (not tilted)
- **90° separation** between cameras (±5° tolerance)

#### Step 2: Frame Composition (Both Cameras)

Both iPhones should frame the athlete identically:

```text
Each camera view:
|------------------------|
|   [margin]             |
|      👤 Full body      | ← Same framing
|       ↕ Jump height    | ← Both cameras
|      / \               |
|  [Landing area]        |
|   [margin]             |
|------------------------|
```

**Synchronize framing:**

- Athlete centered in both frames
- Same margins (10-15% top/bottom)
- Both see full jump sequence
- Landing area visible in both

#### Step 3: Camera Settings (Both iPhones)

##### CRITICAL: Both cameras must have identical settings

| Setting         | Both Cameras                         |
| --------------- | ------------------------------------ |
| **Resolution**  | 1080p (1920x1080) - exactly the same |
| **Frame Rate**  | 60 fps - exactly the same            |
| **Orientation** | Landscape - exactly the same         |
| **Focus**       | Manual, locked                       |
| **Exposure**    | Manual, locked (same brightness)     |
| **Format**      | H.264, Most Compatible               |

**Why identical settings matter:**

- Synchronization requires matching frame rates
- Triangulation assumes same resolution
- Different exposures affect landmark detection

#### Step 4: Synchronization

##### Option A: Manual start (simple)

1. Start recording on iPhone 1
1. Start recording on iPhone 2 within 1-2 seconds
1. **Synchronization cue:** Have athlete clap hands or jump once before actual test
1. Use this event to sync videos in post-processing

##### Option B: Audio sync (better)

1. Use external audio cue (clap, beep, voice command)
1. Both iPhones record audio
1. Align videos using audio waveform in post-processing
1. Software like Pose2Sim has built-in sync tools

##### Option C: Hardware sync (best, requires equipment)

1. Use external trigger device
1. Starts both cameras simultaneously
1. Most accurate synchronization
1. Requires additional hardware

**Recommendation:** Start with Option A (manual + clap sync), upgrade to Option B if needed.

#### Step 5: Calibration

**Required:** One-time calibration before first use or if camera positions change

**Calibration pattern options:**

1. **ChArUco board** (recommended - more robust)

   - Print large ChArUco pattern (A3 or larger)
   - Mount on rigid board
   - Grid size: 7x5 or similar

1. **Checkerboard** (alternative)

   - Print large checkerboard (A3 or larger)
   - 8x6 or 9x7 grid
   - Ensure perfectly flat

**Calibration procedure:**

```bash
# If using Pose2Sim
1. Record calibration pattern from both cameras
2. Move pattern through capture volume (10-15 different positions)
3. Ensure pattern visible in both cameras simultaneously
4. Run calibration:
   Pose2Sim.calibration()
```

**Calibration outputs:**

- Camera intrinsics (focal length, distortion)
- Camera extrinsics (relative positions, rotation)
- Saves to calibration file for reuse

**Re-calibrate when:**

- Camera positions change
- Different lenses used
- After several weeks (drift check)

### Processing Dual Camera Videos

**Current kinemotion support:** Single camera only

**To process stereo videos, you'll need:**

#### Option A: Use Pose2Sim (recommended)

```bash
# Install Pose2Sim
pip install pose2sim

# Process stereo videos
Pose2Sim.calibration()      # One-time
Pose2Sim.poseEstimation()   # Run MediaPipe on both videos
Pose2Sim.synchronization()  # Sync videos
Pose2Sim.triangulation()    # 3D reconstruction
Pose2Sim.filtering()        # Smooth trajectories
Pose2Sim.kinematics()       # OpenSim joint angles
```

#### Option B: Future kinemotion stereo support

Dual camera support may be added to kinemotion in future versions. Current roadmap:

- Stereo triangulation module
- Automatic synchronization
- Integrated calibration workflow

#### Option C: Manual triangulation

If you have programming experience, implement stereo triangulation using OpenCV and MediaPipe output from both cameras.

### Expected Performance (Dual Camera)

**Accuracy improvements over single camera:**

| Metric                  | Single Camera (45°) | Dual Camera (Stereo) | Improvement          |
| ----------------------- | ------------------- | -------------------- | -------------------- |
| **Position RMSE**       | ~56mm               | ~30mm                | 47% better           |
| **Joint Angle Error**   | ~8-12°              | ~5-7°                | ~30-40% better       |
| **Depth Accuracy**      | Poor (noisy)        | Good                 | Eliminates ambiguity |
| **Landmark Visibility** | 40-60%              | 70-90%               | Multi-angle coverage |

**Validated research:**

- Dill et al. (2024): Stereo MediaPipe achieved 30.1mm RMSE vs Qualisys gold standard
- Pagnon et al. (2022): 90° camera separation optimal for triangulation

### Dual Camera Checklist

Before recording, verify:

- [ ] **Both iPhones** on stable tripods
- [ ] **Camera 1** at +45° from athlete's right side
- [ ] **Camera 2** at -45° from athlete's left side
- [ ] **90° total separation** between cameras
- [ ] **Same distance** (3-5m) from athlete for both cameras
- [ ] **Same height** (hip level, 130-150cm) for both cameras
- [ ] **Both level** (not tilted up/down)
- [ ] **Identical settings** (1080p, 60fps, landscape)
- [ ] **Identical focus** and exposure locked
- [ ] **Sync method** planned (clap, audio cue, etc.)
- [ ] **Calibration** completed (one-time)
- [ ] **Test recording** from both cameras simultaneously

______________________________________________________________________

## Recording Settings (Both Setups)

### Video Specifications

| Setting         | Requirement    | Recommendation    | Reason                                            |
| --------------- | -------------- | ----------------- | ------------------------------------------------- |
| **Resolution**  | 1080p minimum  | 1080p (1920x1080) | Higher resolution improves MediaPipe accuracy     |
| **Frame Rate**  | 30 fps minimum | **60 fps**        | Better for short ground contact times (150-250ms) |
| **Orientation** | Landscape only | Landscape         | Wider field of view for jumping movement          |
| **Format**      | MP4, MOV, AVI  | MP4 (H.264)       | Universal compatibility                           |
| **Bitrate**     | Higher better  | Auto or 50+ Mbps  | Preserves detail during motion                    |

### Why 60 fps vs 30 fps?

**For drop jumps and CMJ:**

| Metric                      | 30 fps           | 60 fps           |
| --------------------------- | ---------------- | ---------------- |
| **Temporal resolution**     | 33.3ms per frame | 16.7ms per frame |
| **Ground contact sampling** | 5-8 frames       | 10-15 frames     |
| **Time measurement error**  | ±33ms            | ±16ms            |
| **Velocity accuracy**       | Good             | Better           |

**Ground contact times in drop jumps:** 150-250ms

- At 30 fps: Only 5-8 samples during contact
- At 60 fps: 10-15 samples during contact (2x better)

**Recommendation:** Use 60 fps if your iPhone supports it. The accuracy improvement justifies the larger file size.

### iPhone Camera Settings

**How to set up iPhone for optimal recording:**

1. **Open Camera app**
1. **Settings → Camera → Record Video**
   - Select: **1080p at 60 fps** (or 30 fps if 60 not available)
1. **Settings → Camera → Formats**
   - Select: **Most Compatible** (H.264, not HEVC)
1. **Before recording:**
   - **Lock focus:** Tap and hold on athlete until "AE/AF Lock" appears
   - **Lock exposure:** Swipe up/down to adjust brightness, then keep locked
1. **Frame composition:**
   - Position athlete in center
   - Ensure full body visible with margins
1. **Start recording** before athlete begins jump sequence

**ProTip:** Record a test video first and verify:

- Athlete stays in frame
- Focus remains sharp
- Lighting is adequate
- No motion blur

______________________________________________________________________

## Lighting Guidelines

### Indoor Recording

**Recommended:**

- Overhead gym lights (typical 400-800 lux sufficient)
- Even lighting across jumping area
- Avoid creating athlete shadow on background

**Check:**

- Athlete's face and joints clearly visible
- No harsh shadows on body
- No bright spots (windows, reflective surfaces)

### Outdoor Recording

**Best conditions:**

- Overcast day (soft, even lighting)
- Avoid midday sun (harsh shadows)
- Avoid late afternoon (low angle, long shadows)

**Positioning:**

- Sun behind or to side of cameras
- Athlete not backlit (silhouette)
- Consider time of day for consistent lighting

______________________________________________________________________

## Background Guidelines

**Optimal background:**

- Plain wall (neutral color)
- Contrasting with athlete's clothing
- No patterns or busy elements
- Static (no movement)

**Color contrast examples:**

- Athlete in dark clothing → light background (white/gray wall)
- Athlete in light clothing → dark background (blue/gray wall)
- Avoid: Athlete in white → white background (low contrast)

**Why it matters:** MediaPipe separates figure from background. High contrast improves landmark detection accuracy and reduces false positives.

______________________________________________________________________

## Common Mistakes to Avoid

### ❌ Camera Not at 45° Angle

```text
❌ INCORRECT: Pure lateral (90°)
         [Athlete]
             |
             |
    [Camera]←┘

❌ INCORRECT: Pure frontal (0°)
    [Camera]
       ↓
    [Athlete]

✅ CORRECT: 45° angle
         [Athlete]
             ↘
              ↘ 45°
            [Camera]
```

**Problem with lateral:** High occlusion, low ankle/knee visibility
**Problem with frontal:** Depth ambiguity, jump height measurement poor
**Solution:** Use 45° angle as specified

### ❌ Camera Too Close (\<3m)

**Problems:**

- Perspective distortion (wide-angle effect)
- Risk of athlete moving out of frame
- Lens distortion at edges (curved lines)

**Solution:** Maintain 3-5m distance

### ❌ Camera Too High or Too Low

```text
❌ Too high (looking down):
    [Camera]
       ↓ ↘
         [Athlete]

❌ Too low (looking up):
         [Athlete]
       ↗ ↑
    [Camera]

✅ Correct (hip level):
    [Camera] → [Athlete]
```

**Problem:** Parallax error, distorted proportions
**Solution:** Camera lens at hip height (130-150cm)

### ❌ Poor Framing

**Common mistakes:**

- Athlete too small in frame (camera too far)
- Athlete cut off during jump (camera too close or low)
- Not centered (athlete drifts out of frame)

**Solution:**

- Test recording first
- Adjust framing to include full jump with margins
- Mark jumping position to ensure consistency

### ❌ Inconsistent Settings Between Dual Cameras

**For stereo setup only:**

**Problems:**

- Different frame rates → sync impossible
- Different resolutions → triangulation fails
- Different exposure → landmark detection inconsistent

**Solution:** Configure both iPhones identically (see Dual Camera Checklist)

______________________________________________________________________

## Troubleshooting

### "Poor landmark visibility" Warning

**Symptoms:** Kinemotion reports low visibility scores

**Causes:**

- Insufficient lighting
- Low contrast with background
- Camera out of focus
- Motion blur (shutter speed too slow)

**Solutions:**

1. Add lighting sources
1. Change background or athlete clothing for contrast
1. Lock focus on athlete (tap and hold)
1. Increase shutter speed (reduce exposure if needed)
1. Ensure 1080p resolution

### Jump Height Seems Incorrect

**Possible causes:**

1. Camera angle not optimal (measurement error)
1. Athlete moving horizontally (drift during jump)
1. Camera not level (tilted)
1. Poor video quality affecting tracking

**Solutions:**

1. Verify camera angle with measuring app or protractor
1. Coach athlete to jump straight up (minimal drift)
1. Use tripod level indicator or phone level app
1. Use `--quality accurate` for best results with good videos

### "No Drop Jump Detected" Error

**Possible causes:**

1. Video doesn't include complete sequence
1. Athlete cut off in framing
1. Very poor tracking quality

**Solutions:**

1. Start recording before athlete steps on box
1. Adjust framing - test with practice jump
1. Improve video quality (lighting, focus, resolution)
1. Use manual `--drop-start-frame` flag if auto-detection fails

### Dual Camera: Videos Not Synchronized

**Symptoms:** Triangulation fails or produces unrealistic 3D poses

**Solutions:**

1. Verify both videos have identical frame rates
1. Use audio/visual cue to sync (clap, beep)
1. Use Pose2Sim synchronization module
1. Consider hardware trigger for future recordings

______________________________________________________________________

## Equipment Recommendations

### Single Camera Setup

**Budget Option ($100-300):**

- iPhone SE (2020 or later) or Android flagship
- Basic tripod with smartphone mount ($20-50)
- Total: ~$150-350

**Mid-Range ($500-800):**

- Recent iPhone (11 or later) with 4K/60fps
- Quality tripod with fluid head ($100-200)
- Total: ~$600-1000

**What you need:**

- iPhone capable of 1080p @ 60fps minimum
- Stable tripod (lightweight OK for indoor use)
- Level indicator (most tripods have bubble level)

### Dual Camera Setup

**Budget Stereo ($300-600):**

- 2x iPhone SE or similar
- 2x basic tripods
- Calibration board (print and mount, \<$20)
- Total: ~$350-650

**Mid-Range Stereo ($1000-1600):**

- 2x Recent iPhone (same model)
- 2x quality tripods
- Professional calibration board
- Optional: Hardware sync trigger
- Total: ~$1200-1800

**What you need:**

- 2 iPhones (same model strongly recommended)
- 2 stable tripods (identical height adjustment)
- Calibration pattern (ChArUco or checkerboard)
- Processing capability (laptop/desktop for Pose2Sim)

**Cost comparison to research-grade systems:**

- Marker-based MoCap (Vicon, Qualisys): $50,000-$500,000
- Commercial markerless (Theia3D): $5,000-$20,000
- Dual iPhone + Pose2Sim: $300-$1,800 (100x cheaper!)

______________________________________________________________________

## Validation and Quality Checks

### After Recording

**For every video, verify:**

1. **Playback check:**

   - Full jump sequence captured
   - Athlete stays in frame
   - Focus sharp throughout
   - No motion blur

1. **Quality metrics:**

   - File size appropriate (60fps 1080p ≈ 200MB/min)
   - No dropped frames (smooth playback)
   - Audio clear (if using for sync)

1. **Test analysis:**

   - Run kinemotion on video
   - Check debug overlay output
   - Verify landmark detection quality

### Quality Indicators

**Good quality video (ready for analysis):**

- ✅ MediaPipe visibility scores >0.5 average
- ✅ Smooth landmark tracking (minimal jitter)
- ✅ All jump phases detected automatically
- ✅ Debug overlay shows consistent tracking

**Poor quality video (re-record recommended):**

- ❌ Visibility scores \<0.3 average
- ❌ Jumpy landmark positions (tracking loss)
- ❌ Failed phase detection
- ❌ Debug overlay shows gaps or unrealistic poses

______________________________________________________________________

## Advanced Tips

### For Consistent Multi-Session Recording

**Create a standardized setup:**

1. **Mark camera positions** on floor with tape

   - Measure 45° angle precisely
   - Mark 4m distance circle
   - Label "Camera 1" and "Camera 2" positions

1. **Document your setup:**

   - Take photos of camera positions
   - Note tripod height settings
   - Save camera settings screenshot

1. **Use same equipment** across sessions

   - Same iPhone(s)
   - Same tripod height
   - Same room/location if possible

**Benefits:**

- Consistent measurements across time
- Easier to compare athlete progress
- Simplified setup for each session

### Optimizing for Different Jump Types

**Drop Jump specific:**

- Ensure drop box visible in frame (important for context)
- Capture pre-drop standing phase
- Need to see ground contact clearly

**CMJ specific:**

- Start with athlete already in frame (no drop box)
- Capture countermovement phase (downward motion)
- Need full range of motion (lowest point to peak)

**Both:**

- 60 fps beneficial for fast movements
- Hip-level camera height optimal
- 45° angle works for both jump types

______________________________________________________________________

## Research Background

### Why These Recommendations?

**Camera angle (45°):**

- Baldinger et al. (2025) showed camera viewing angle significantly affects joint angle validity
- 45° reduces occlusion while maintaining sagittal plane visibility
- Compromise between frontal (high visibility) and lateral (pure sagittal)

**Dual camera 90° separation:**

- Pagnon et al. (2022): Tested multiple angles, found 90° optimal for 3D triangulation
- Dill et al. (2024): Validated stereo MediaPipe at 30.1mm RMSE with 90° setup
- Balance between wide baseline (accuracy) and overlapping views (matching)

**1080p @ 60fps:**

- Higher resolution improves MediaPipe landmark detection
- 60 fps necessary for accurate temporal events (ground contact)
- Validated in multiple studies as sufficient for biomechanics

### Limitations of Single Camera

**What single camera (45°) CANNOT provide:**

- Research-grade accuracy (limited to ~8-12° joint angle errors)
- Accurate depth/3D coordinates (z-axis noisy)
- Biomechanical constraints (no skeletal model)
- Validation against gold-standard (needs multi-camera)

**What single camera (45°) CAN provide:**

- Training and assessment quality measurements
- Relative comparisons (same athlete over time)
- Drop jump key metrics (contact time, flight time, RSI)
- CMJ metrics (jump height, countermovement depth)

**For research-grade accuracy:** Use dual camera stereo setup with Pose2Sim or OpenCap.

______________________________________________________________________

## Summary

### Single iPhone at 45° (Standard Setup)

**Quick setup:**

1. Position camera 45° from athlete's sagittal plane
1. 4 meters distance, hip height (130-150cm)
1. 1080p @ 60 fps, landscape, locked focus/exposure
1. Frame full body with 10-15% margins
1. Even lighting, plain background
1. Record full jump sequence

**Expected accuracy:** Good for training/assessment (~8-12° joint angles)

### Dual iPhone Stereo (Advanced Setup)

**Quick setup:**

1. Position Camera 1 at +45° (right), Camera 2 at -45° (left)
1. Both 4m distance, both hip height, 90° separation
1. Identical settings: 1080p @ 60fps
1. Calibrate with ChArUco/checkerboard pattern
1. Sync with clap or audio cue
1. Process with Pose2Sim for 3D reconstruction

**Expected accuracy:** Research-grade (~5-7° joint angles, 30mm RMSE)

### Decision Guide

**Use single camera if:**

- Training/coaching applications
- Assessing relative improvements
- Budget/equipment constraints
- Simplicity prioritized

**Use dual camera if:**

- Research applications
- Elite athlete assessment
- Accurate 3D kinematics needed
- Publishing or validation required

______________________________________________________________________

## Related Documentation

- **[Versión en Español](../translations/es/camera-setup.md)** - Spanish version of this guide
- **[Sports Biomechanics Pose Estimation](../research/sports-biomechanics-pose-estimation.md)** - Comprehensive research on pose systems
- **[Pose Systems Quick Reference](../reference/pose-systems.md)** - System comparison guide
- [CLI Parameters Guide](../reference/parameters.md) - Analysis parameters
- [CMJ Guide](cmj-guide.md) - Counter-movement jump specifics
- [CLAUDE.md](https://github.com/feniix/kinemotion/blob/main/CLAUDE.md) - Complete project documentation (GitHub)

______________________________________________________________________

## References

**Camera angle research:**

- Baldinger, M., Reimer, L. M., & Senner, V. (2025). Influence of the Camera Viewing Angle on OpenPose Validity in Motion Analysis. *Sensors*, 25(3), 799. <https://doi.org/10.3390/s25030799>

**Stereo camera validation:**

- Dill, S., et al. (2024). Accuracy Evaluation of 3D Pose Reconstruction Algorithms Through Stereo Camera Information Fusion for Physical Exercises with MediaPipe Pose. *Sensors*, 24(23), 7772. <https://doi.org/10.3390/s24237772>

**Optimal camera separation:**

- Pagnon, D., Domalain, M., & Reveret, L. (2022). Pose2Sim: An End-to-End Workflow for 3D Markerless Sports Kinematics—Part 2: Accuracy. *Sensors*, 22(7), 2712. <https://doi.org/10.3390/s22072712>

For complete bibliography, see [sports-biomechanics-pose-estimation.md](../research/sports-biomechanics-pose-estimation.md).

______________________________________________________________________

**Last Updated:** November 6, 2025
