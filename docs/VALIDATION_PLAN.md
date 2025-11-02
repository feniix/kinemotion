# Kinemotion Validation Plan

**Status**: 📋 HOBBY PROJECT - Practical Validation Approach
**Created**: 2025-01-26
**Last Updated**: 2025-11-01 (Auto-tuning system added)
**Purpose**: Realistic, low-cost validation roadmap for a hobby project

______________________________________________________________________

## ⚠️ Current Status

**IMPORTANT**: Kinemotion measurements are currently **unvalidated**. This document outlines a practical, affordable validation approach suitable for a hobby project. The goal is to establish "reasonable accuracy" rather than research-grade validation.

**NEW (November 2025)**: Kinemotion now features intelligent auto-tuning that eliminates manual parameter adjustment. The tool automatically:

- Detects video FPS and adjusts velocity thresholds accordingly (30/60/120fps)
- Analyzes tracking quality and adapts smoothing
- Auto-detects drop start frame (no manual specification needed)
- Handles iPhone rotation metadata automatically

This makes validation testing easier - no need to guess optimal parameters!

______________________________________________________________________

## 1. Validation Philosophy for Hobby Projects

### What "Validation" Means Here

For a hobby project, validation means:

- ✅ **Reasonable accuracy**: Measurements are "in the ballpark" for practical use
- ✅ **Consistency**: Repeated measurements give similar results
- ✅ **Sanity checks**: Results make physical sense (jump height from flight time checks out)
- ✅ **Comparative accuracy**: Similar to other free/affordable tools (My Jump Lab, jump mats)
- ❌ **NOT research-grade**: Not validated against force plates or motion capture systems

### Realistic Goals

- Establish that Kinemotion provides **useful estimates** for athletes and coaches
- Identify conditions where it works well (and where it doesn't)
- Compare against other accessible tools
- Build confidence through community validation
- **No academic publication required** - just honest assessment

______________________________________________________________________

## 2. Frame Rate Recommendations

**IMPORTANT**: Frame rate significantly impacts timing accuracy for drop jump analysis.

### Frame Rate vs. Timing Accuracy

| Frame Rate | Time per Frame | Event Detection Error | Contact Time Error\* | Recommendation    |
| ---------- | -------------- | --------------------- | -------------------- | ----------------- |
| 30fps      | 33.3ms         | ±17-33ms              | ±10-20%              | ⚠️ Minimum viable |
| 60fps      | 16.7ms         | ±8-17ms               | ±5-10%               | ✅ Recommended    |
| 120fps     | 8.3ms          | ±4-8ms                | ±2-5%                | 🎯 Ideal          |
| 240fps     | 4.2ms          | ±2-4ms                | ±1-3%                | 🏆 Excellent      |

\*For typical drop jump contact times of 150-300ms

### Our Recommendation

**For validation and general use**:

- 🎯 **Target**: 60fps or higher (most modern phones support this)
- ✅ **Minimum**: 30fps (works but with reduced timing accuracy)
- 🏆 **Ideal**: 120fps slow-motion if available (best precision)

**Why 60fps minimum**:

- Ground contact times are often 150-300ms
- At 30fps: ±30ms timing error = 10-20% uncertainty
- At 60fps: ±15ms timing error = 5-10% uncertainty
- Modern smartphones easily support 60fps recording

**Note**: All validation in this document assumes **60fps as the baseline** unless otherwise specified. Adjust acceptance criteria if using 30fps (double the timing error tolerances).

______________________________________________________________________

## 3. Free Validation Methods (Budget: $0)

These methods cost nothing and can be done immediately by any user.

### 3.1 Compare Against My Jump Lab App

**What it is**: My Jump Lab (also known as My Jump 3) is a popular iPhone/Android app that calculates jump height from slow-motion video. It's been validated in multiple research studies (ICC > 0.95 vs. force plates).

**Download**: [iOS App Store](https://apps.apple.com/us/app/my-jump-lab-my-jump-3/id1554077178) | [Google Play](https://play.google.com/store/apps/details?id=com.my.jump.lab&hl=en)

**How to do it**:

1. Download My Jump Lab app from the links above
1. Record 10-20 jumps (countermovement or drop jumps)
1. Process same video with both My Jump Lab and Kinemotion
1. Compare jump heights, contact times, flight times
1. Calculate: mean difference, correlation, percentage error

**What to expect**:

- If correlation r > 0.85: Good agreement
- If mean difference \< 5cm for jump height: Acceptable
- If contact/flight times within ±30ms: Reasonable for 30fps video

**Time required**: 2-3 hours

**Validation value**: ⭐⭐⭐⭐⭐ (High - My Jump Lab is well-validated)

### 3.2 Tracker Video Analysis Tool

**What it is**: Tracker (<https://physlets.org/tracker/>) is a free, open-source video analysis tool widely used in physics education. It allows frame-by-frame position tracking with sub-pixel accuracy.

**Why it's excellent for validation**:

- ✅ Free and open-source
- ✅ Used in academic settings (established credibility)
- ✅ Tracks full trajectories (not just flight time)
- ✅ Export position data for detailed comparison
- ✅ Calibration tools (use known reference length)
- ✅ Sub-pixel tracking accuracy

**How to do it**:

1. Download Tracker from <https://physlets.org/tracker/>
1. Open your drop jump video in Tracker
1. Set coordinate system (origin at ground level)
1. Calibrate scale using known reference (e.g., drop box height)
1. Track ankle/heel position frame-by-frame (autotrack feature available)
1. Export position data (time vs. vertical position)
1. Identify takeoff/landing from position data
1. Calculate jump height from trajectory
1. Compare with Kinemotion results

**What to compare**:

- **Jump height**: Direct position measurement vs. Kinemotion
- **Event timing**: Landing/takeoff frames from trajectory analysis
- **Trajectory shape**: Compare full position curves
- **Contact/flight times**: Derived from position tracking

**What to expect**:

- Tracker accuracy: ±0.5-1cm (with proper calibration)
- Should agree within ±3-5cm with Kinemotion
- Validates both position tracking AND event detection
- Can identify systematic biases (e.g., Kinemotion consistently 2cm higher)

**Time required**: 2-3 hours (1 hour learning Tracker + 1-2 hours analysis)

**Validation value**: ⭐⭐⭐⭐⭐ (Excellent - rigorous position-based validation, free)

**Advantages over My Jump Lab**:

- Tracks full trajectory (not just flight time)
- Open-source and free (My Jump Lab costs $10-15)
- More detailed analysis capabilities
- Established in academic settings

### 3.3 Manual Slow-Motion Video Analysis

**What it is**: Frame-by-frame inspection of video to manually identify landing/takeoff frames.

**How to do it**:

1. Record 5-10 jumps at 60fps or 120fps (slow-motion on phone)
1. Use free video player (VLC, QuickTime) to step through frame-by-frame
1. Manually mark takeoff frame and landing frame
1. Calculate flight time: (frames_between / frame_rate)
1. Calculate jump height: h = g × t² / 8 (where t = flight time, g = 9.81 m/s²)
1. Compare with Kinemotion results

**What to expect**:

- Manual analysis accuracy: ±1-2 frames (±16-33ms at 60fps)
- Should agree within ±2 frames of Kinemotion's detected events
- Validates event detection accuracy

**Time required**: 3-4 hours

**Validation value**: ⭐⭐⭐⭐ (Good - validates event detection directly)

### 3.4 Physics Sanity Checks

**What it is**: Verify measurements make physical sense.

**Checks to perform**:

1. **Jump height from flight time**:

   - Calculate: h = g × t² / 8
   - Compare with position-based height
   - Should agree within 10-15%

1. **Velocity at takeoff**:

   - Calculate: v = g × t / 2 (where t = flight time)
   - Check: Is takeoff velocity reasonable? (1.5-2.5 m/s for typical jumps)

1. **Drop height calibration**:

   - If you know drop box height (e.g., 40cm)
   - Does calibrated measurement match reality?
   - Test with known reference heights

1. **Repeatability**:

   - Do 3 identical jumps
   - Results should be within 5-10% of each other
   - High variation suggests measurement issues

**Time required**: 1-2 hours

**Validation value**: ⭐⭐⭐ (Moderate - catches obvious errors)

### 3.5 Test-Retest Reliability

**What it is**: Measure same jumps twice to check consistency.

**How to do it**:

1. Record 5 jumps
1. Process with Kinemotion
1. Process same videos again (fresh analysis)
1. Compare results - should be identical (deterministic algorithm)
1. If using different videos of same jumps:
   - Calculate ICC (intraclass correlation)
   - Target: ICC > 0.90 (excellent reliability)

**Time required**: 1 hour

**Validation value**: ⭐⭐⭐⭐ (Good - validates algorithm consistency)

______________________________________________________________________

## 4. Low-Cost Validation Methods (Budget: $100-500)

Optional methods if you have budget for equipment.

### 4.1 Jump Mat Comparison (~$200-500)

**What it is**: Affordable switch mats that measure contact time and flight time.

**Options**:

- **DIY jump mat**: Build your own with pressure sensors and Arduino (~$50-100)
- **Commercial jump mats**:
  - Basic models: $200-400
  - Plyomat: ~$900 (validated against force plates)
  - Just Jump mat: ~$300-400

**How to do it**:

1. Purchase or build jump mat
1. Record 20-30 jumps with simultaneous video + jump mat
1. Compare contact times and flight times
1. Calculate correlation and agreement statistics

**What to expect**:

- Jump mats accurate to ±10-20ms typically
- Good target for video-based validation
- If agreement within ±30ms: Acceptable for 30fps video

**Time required**: 4-6 hours (after equipment acquisition)

**Validation value**: ⭐⭐⭐⭐⭐ (Excellent - independent reference system)

### 4.2 Optical Timing Gates (~$100-300)

**What it is**: Infrared sensors that detect when you break a light beam.

**How to use**:

- Set up 2 timing gates at ankle height
- Jump through gates (break beam on takeoff and landing)
- Measures flight time directly
- Compare with video-based flight time

**Time required**: 3-4 hours

**Validation value**: ⭐⭐⭐⭐ (Good - direct flight time measurement)

______________________________________________________________________

## 5. Simple Statistical Analysis

**No need for complex statistics!** Basic comparisons are sufficient:

### 5.1 Correlation

- Calculate Pearson correlation (r) between Kinemotion and reference
- Interpretation:
  - r > 0.90: Excellent
  - r = 0.80-0.90: Good
  - r = 0.70-0.80: Acceptable
  - r \< 0.70: Needs improvement

**Tool**: Any spreadsheet (Excel, Google Sheets) or Python pandas

### 5.2 Mean Difference

- Calculate: mean(Kinemotion - Reference)
- Shows systematic bias
- Example: If mean difference = +3cm, Kinemotion overestimates by 3cm on average

### 5.3 Mean Absolute Error (MAE)

- Calculate: mean(abs(Kinemotion - Reference))
- Shows typical error magnitude
- Target: MAE \< 5cm for jump height, \< 30ms for timing at 30fps

### 5.4 Percentage Error

- Calculate: mean(abs((Kinemotion - Reference) / Reference) × 100)
- Shows relative error
- Target: \< 10% for practical use

**Example Python Code**:

```python
import numpy as np
from scipy.stats import pearsonr

kinemotion = [28.5, 32.1, 30.4, 29.8, 31.2]  # cm
reference = [27.9, 31.5, 29.8, 29.2, 30.5]   # cm

r, p = pearsonr(kinemotion, reference)
mean_diff = np.mean(np.array(kinemotion) - np.array(reference))
mae = np.mean(np.abs(np.array(kinemotion) - np.array(reference)))

print(f"Correlation: r = {r:.3f}, p = {p:.3f}")
print(f"Mean difference: {mean_diff:.2f} cm")
print(f"Mean absolute error: {mae:.2f} cm")
```

______________________________________________________________________

## 6. DIY Validation Protocol (For Developer)

**Goal**: Quick self-validation with minimal resources

### Phase 1: Initial Testing (Week 1)

#### Day 1-2: Setup

- [ ] Download Tracker (<https://physlets.org/tracker/>) - free and open-source
- [ ] Alternative: Install My Jump Lab app if iOS device available
- [ ] Set up recording environment (good lighting, clear background)
- [ ] Test camera angles and distances

#### Day 3-5: Data Collection

- [ ] Record 10 countermovement jumps or drop jumps
- [ ] Include known reference in video (ruler, measuring tape, or known drop box height)
- [ ] Ensure good video quality (no motion blur, clear foot position)
- [ ] **Use 60fps or higher** (recommended for accurate timing measurements)
- [ ] 30fps acceptable as minimum, but expect ±30ms timing error vs ±15ms at 60fps

#### Day 6-7: Analysis

- [ ] Process all videos with Kinemotion
- [ ] Analyze same videos with Tracker (track ankle/heel position)
- [ ] Alternative: Use My Jump Lab if available
- [ ] Export Tracker position data and calculate jump height
- [ ] Calculate correlation, mean difference, MAE
- [ ] Document results in validation notes

#### Phase 1 Success Criteria

- Correlation r > 0.85 with Tracker/My Jump Lab
- Mean difference \< 5cm for jump height
- Contact/flight times within ±30ms
- Event detection within ±2-3 frames

### Phase 2: Manual Verification (Week 2-3)

#### Week 2: Frame-by-Frame Analysis

- [ ] Select 5 best quality videos
- [ ] Manually identify takeoff/landing frames
- [ ] Compare with Kinemotion's detected events
- [ ] Document frame differences

#### Week 3: Physics Checks

- [ ] Calculate jump height from flight time (h = g×t²/8)
- [ ] Compare with position-based estimates
- [ ] Verify velocity calculations make sense
- [ ] Test repeatability (process same video 3 times)

#### Phase 2 Success Criteria

- Event detection within ±2 frames of manual analysis
- Physics calculations internally consistent (\<10% difference)
- Perfect repeatability (deterministic algorithm)

### Phase 3: Documentation (Week 4)

- [ ] Write up results in docs/VALIDATION_RESULTS.md
- [ ] Update README.md with honest accuracy claims
- [ ] Document conditions where tool works well
- [ ] Document limitations and error sources
- [ ] Add disclaimer with validation status

______________________________________________________________________

## 7. Community Validation

### Leverage user contributions to expand validation data

### 7.1 Invite User Comparisons

Create a validation issue on GitHub:

**Title**: "Community Validation: Share Your Comparison Data"

**Template**:

```markdown
Help validate Kinemotion by comparing it with other tools!

**What to do**:
1. Record jump videos (with phone/camera at 60fps+)
2. Analyze videos with Kinemotion
3. Compare with My Jump Lab, jump mat, or manual analysis
4. Share your results here

**Data to share**:
- Number of jumps analyzed
- Reference tool used (My Jump Lab, jump mat, manual)
- Correlation (if calculated)
- Mean difference
- Your assessment (good agreement? systematic bias?)

**Example**:
- 15 jumps compared with My Jump Lab
- Correlation: r = 0.91
- Mean difference: -2.3cm (Kinemotion slightly lower)
- Assessment: Good agreement for practical use
```

### 7.2 Aggregate Community Data

- Collect user reports in validation spreadsheet
- Calculate overall statistics across all users
- Identify patterns (works better at 60fps vs 30fps, etc.)
- Build confidence through multiple independent validations

______________________________________________________________________

## 8. Acceptance Criteria for Hobby Project

**"Good Enough" Thresholds**:

### Jump Height

- ✅ **Acceptable**: MAE \< 5cm, r > 0.85
- ⭐ **Good**: MAE \< 3cm, r > 0.90
- 🏆 **Excellent**: MAE \< 2cm, r > 0.95

### Contact Time / Flight Time

- ✅ **Acceptable**: MAE \< 30ms (at 30fps), r > 0.80
- ⭐ **Good**: MAE \< 20ms (at 30fps), r > 0.85
- 🏆 **Excellent**: MAE \< 10ms (at 60fps), r > 0.90

### Event Detection

- ✅ **Acceptable**: Within ±3 frames of manual analysis
- ⭐ **Good**: Within ±2 frames of manual analysis
- 🏆 **Excellent**: Within ±1 frame of manual analysis

**If these criteria are met**: Can claim "validated for practical use" with appropriate caveats about video quality, frame rate, and conditions.

______________________________________________________________________

## 9. Timeline & Resource Summary

### Realistic Timeline (Solo Developer)

**Week 1**: My Jump Lab comparison (2-3 hours total)
**Week 2**: Manual video analysis (3-4 hours total)
**Week 3**: Physics checks and repeatability (2-3 hours total)
**Week 4**: Documentation and results write-up (2-3 hours total)

**Total time investment**: 10-15 hours over 1 month

**Optional**: Purchase jump mat if budget allows (adds 4-6 hours for testing)

### Budget Summary

**Minimum (Free)**:

- My Jump Lab app (or use free trial): $0-15
- Time: 10-15 hours
- **Total: $0-15**

**Recommended (Low-Cost)**:

- My Jump Lab app: $10-15
- Basic jump mat: $200-400 (optional)
- Time: 15-20 hours
- **Total: $10-415**

**Aspirational (Research-Grade)**:

- All of the above: $10-415
- Plyomat validated jump mat: $900
- Lab access for force plate comparison: $0-5000 (if opportunity arises)
- **Total: $910-6315**

**For hobby project**: Stick to minimum or recommended budget!

______________________________________________________________________

## 10. Opportunistic Validation

### If Lab Access Becomes Available

Sometimes opportunities arise unexpectedly:

- Friend/colleague has access to biomechanics lab
- Local university offers community access
- Contact with sports science researcher

**If this happens**:

1. Explain your tool and validation goal
1. Ask if you can run 10-20 test jumps for comparison
1. Offer to share results (may help their research too)
1. Be flexible with timing (work around their schedule)

**Cost**: Usually free if someone gives you access, just your time

______________________________________________________________________

## 11. Documenting Results

### What to Document (Honest Assessment)

**If validation successful** (meets acceptance criteria):

- ✅ State which reference tools were used
- ✅ Report correlation and error statistics
- ✅ Specify video conditions tested (frame rate, lighting, etc.)
- ✅ Note limitations and caveats
- ✅ Update README.md with accuracy claims

**Example README update**:

```markdown
## Validation Status

Kinemotion has been validated through comparison with My Jump Lab app and manual video analysis:

- **Jump height**: Correlation r = 0.88, MAE = 4.2cm (n=25 jumps, 30fps video)
- **Flight time**: Correlation r = 0.91, MAE = 24ms (n=25 jumps, 30fps video)
- **Event detection**: Within ±2 frames of manual analysis

**Tested conditions**: Indoor lighting, 1080p video at 30fps, front camera view

**Limitations**:
- Not validated against force plates or motion capture
- Accuracy decreases with poor lighting or motion blur
- Lower accuracy at 30fps vs 60fps (±30ms vs ±15ms timing)

See docs/VALIDATION_RESULTS.md for full details.
```

**If validation shows issues**:

- ❗ Be transparent about problems found
- ❗ Document conditions where tool doesn't work well
- ❗ Keep prominent ⚠️ warnings in documentation
- ❗ Explain what needs improvement

### Create docs/VALIDATION_RESULTS.md

Template:

```markdown
# Validation Results

**Date**: [YYYY-MM-DD]
**Validated by**: [Your name/GitHub handle]
**Version tested**: [Kinemotion version]

## Summary

[Brief overview of validation approach and key findings]

## Methods

### Reference Tools
- [List tools used: My Jump Lab, manual analysis, etc.]

### Testing Protocol
- [Number of jumps, video settings, conditions]

## Results

### Jump Height
- Correlation: r = [value]
- Mean difference: [value] cm
- Mean absolute error: [value] cm
- Interpretation: [good/acceptable/needs work]

### Contact Time
- [Same format]

### Flight Time
- [Same format]

### Event Detection
- [Frame accuracy comparison]

## Visualizations

[Include scatter plots, Bland-Altman if desired, or just tables]

## Conclusions

### What Works Well
- [List conditions/scenarios with good accuracy]

### Limitations Found
- [List conditions where accuracy suffers]

### Recommendations
- [Advice for users to get best results]

## Raw Data

[Optional: Include CSV or table of all measurements for transparency]
```

______________________________________________________________________

## 12. Alternative: "Trust but Verify" Approach

**Philosophy**: Start using the tool, verify it makes sense through practical use.

### Practical Verification

1. **Does it pass the smell test?**

   - Do jump heights seem reasonable? (20-40cm for recreational, 40-70cm for trained athletes)
   - Are contact times sensible? (150-300ms typical for drop jumps)
   - Does flight time correlate with perceived jump height?

1. **Internal consistency**

   - Do better jumps (feel higher) measure higher?
   - Do repeated similar jumps give similar results?
   - Do trends over time make sense (improving with training)?

1. **Comparative validation**

   - Does athlete A (known to jump higher) measure higher than athlete B?
   - Do measurements track with performance (vertical jump improvement = better game performance)?

**When this is sufficient**:

- Using tool for personal training feedback
- Tracking relative improvements over time
- Not making high-stakes decisions based on measurements
- Comfortable with "good enough" accuracy

______________________________________________________________________

## 13. Conclusion

### Validation is Iterative

You don't need perfect validation on day one. Start simple:

1. **Phase 1**: Compare with My Jump Lab (1 week, free)
1. **Phase 2**: Manual verification (1 week, free)
1. **Phase 3**: Document results (1 week)
1. **Phase 4**: Community validation (ongoing)
1. **Phase 5**: Opportunistic upgrades (if lab access becomes available)

### Honest Limitations

A hobby project validation will never match research-grade validation, and **that's okay**:

- ✅ Can establish "practical accuracy"
- ✅ Can identify obvious problems
- ✅ Can build user confidence
- ❌ Cannot claim research-grade validation
- ❌ Cannot recommend for scientific studies (without further validation)

### The Goal

Provide users with **honest, evidence-based information** about tool accuracy so they can make informed decisions about whether it meets their needs.

______________________________________________________________________

## Appendix: Quick Comparison - Hobby vs Research Validation

| Aspect           | Hobby Approach              | Research Approach            |
| ---------------- | --------------------------- | ---------------------------- |
| **Budget**       | $0-500                      | $15,000-30,000               |
| **Time**         | 1-3 months                  | 6-12 months                  |
| **Reference**    | My Jump Lab, jump mat       | Force plates, motion capture |
| **Participants** | Self + volunteers           | 30-50 recruited participants |
| **Statistics**   | Correlation, MAE            | ICC, Bland-Altman, LOA       |
| **Ethics**       | None required               | IRB approval needed          |
| **Publication**  | GitHub documentation        | Peer-reviewed journal        |
| **Outcome**      | "Practical accuracy"        | "Research-grade validated"   |
| **Use cases**    | Personal training, coaching | Scientific studies, research |

**For a hobby project**: Left column is perfectly appropriate!

______________________________________________________________________

**Document Version**: 2.1 (Frame Rate Guidance Added)
**Last Updated**: 2025-01-26
**Status**: 📋 Practical Validation Approach
**Key Updates**:

- Added Section 2: Frame Rate Recommendations (60fps recommended, not 30fps)
- Added Section 3.2: Tracker video analysis tool (free, open-source, rigorous)
- Clarified that validation assumes 60fps baseline for accuracy targets

**Next Steps**: Start with Phase 1 (Tracker or My Jump Lab comparison at 60fps+)
