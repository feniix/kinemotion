# Validation Status

**Document Version:** 1.0
**Last Updated:** 2025-01-13
**Status:** Pre-validation

______________________________________________________________________

## Executive Summary

Kinemotion is a **pre-validation** tool that has not been validated against gold standard measurement systems (force plates, 3D motion capture). While the implementation is technically sophisticated and biomechanically sound, it **lacks empirical validation** required for research or clinical use.

**Bottom Line:** Use kinemotion for training monitoring and exploratory analysis. Do not use for research publications, clinical decisions, or any context requiring validated accuracy.

______________________________________________________________________

## Current Validation Status

### What Has Been Done ✅

- ✅ **Algorithmic implementation** - Biomechanically sound algorithms based on validated theory
- ✅ **Code quality** - 74.27% test coverage (261 tests), type-checked, linted
- ✅ **Theoretical foundation** - Based on validated principles:
  - Flight-time method (Bosco et al., 1983)
  - Force-velocity profiling theory (Samozino et al., 2014)
  - Dempster body segment parameters (1955)
- ✅ **Open source** - Transparent algorithms, reproducible results

### What Has NOT Been Done ❌

- ❌ **Force plate comparison** - No validation against gold standard
- ❌ **Reliability studies** - No test-retest, inter-device, or inter-rater data
- ❌ **Accuracy metrics** - No ICC, bias, limits of agreement calculated
- ❌ **Correction factors** - No systematic bias corrections (cf. Bishop et al., 2022 required correction factors)
- ❌ **Peer review** - No published validation study
- ❌ **Clinical validation** - No testing in clinical populations
- ❌ **Multi-site validation** - No testing across different laboratories/conditions

______________________________________________________________________

## Comparison to Validated Tools

| Aspect                      | MyJump (Validated)     | Kinemotion (Unvalidated)    |
| --------------------------- | ---------------------- | --------------------------- |
| **Force plate validation**  | Yes (ICC=0.997)        | No                          |
| **Peer-reviewed study**     | Published 2015         | None                        |
| **Sampling rate**           | 120Hz (iPhone 5s)      | 30-60fps (video dependent)  |
| **Method**                  | Manual frame selection | Automated landmark tracking |
| **Accuracy vs force plate** | Bias: 1.1±0.5cm        | Unknown                     |
| **Cost**                    | ~$12 app               | Free (open source)          |
| **Expertise required**      | Low (frame selection)  | None (fully automated)      |
| **Use in research**         | Yes (widely cited)     | No (not validated)          |

**Key Difference:** MyJump has been validated against force plates and published in peer-reviewed journals. Kinemotion has not.

______________________________________________________________________

## Current Validation Efforts (AthletePose3D)

We are currently in **Phase 1** of a multi-stage validation study using the **AthletePose3D (AP3D)** dataset, which contains high-speed athletic movements captured by research-grade multi-camera systems.

### 🧪 Methodology Highlights

To transition from 2D pixel-based analysis to research-grade 3D kinematics, we are implementing:

1. **Coordinate Normalization:** Using Procrustes Analysis (Kabsch Algorithm) to align MediaPipe detections with physical world coordinates (mm).
1. **3D Joint Angles:** Reconstructing anatomical angles (Hip, Knee, Ankle) in 3D space to correct for camera perspective and foreshortening.

For detailed technical analysis of why these steps matter for monocular video and how they are implemented, see the [AthletePose3D Methodology Guide](validation/athletepose3d-methodology.md).

______________________________________________________________________

## What Kinemotion CAN Claim

### Technical Implementation ✅

- "Implements biomechanically sound algorithms"
- "Uses validated theoretical frameworks (Samozino, Bosco)"
- "Provides consistent, repeatable measurements" (deterministic)
- "Advanced signal processing (RANSAC, bilateral filtering)"
- "Open source with comprehensive test coverage"

### Practical Use ✅

- "Suitable for training monitoring (relative changes)"
- "Useful for educational purposes"
- "Can track progress within individual athletes"
- "Provides exploratory analysis capabilities"

______________________________________________________________________

## What Kinemotion CANNOT Claim

### Validation Claims ❌

- ~~"Validated against force plates"~~
- ~~"Research-grade accuracy"~~
- ~~"Clinically validated"~~
- ~~"Equivalent to MyJump/validated apps"~~
- ~~"Suitable for research publications"~~

### Accuracy Claims ❌

- ~~"Accuracy within X cm of force plates"~~
- ~~"ICC > 0.90 reliability"~~
- ~~"Gold standard measurement"~~
- ~~"Laboratory-grade precision"~~

______________________________________________________________________

## Known Limitations

### 1. No Gold Standard Validation

**Issue:** Never compared against force plates or optical motion capture
**Impact:** Unknown accuracy, cannot make quantitative accuracy claims
**Mitigation:** Validation study planned (see roadmap)

### 2. MediaPipe Pose Estimation Constraints

**Issue:** MediaPipe validated for clinical joint angles (Armstrong et al., 2025) but NOT for jump performance metrics
**Limitations documented in research:**

- Affected by lighting conditions
- Reduced accuracy with loose clothing
- Jitter from self-occlusion
- Not optimized for high-speed ballistic movements

**Impact:** Tracking quality varies with recording conditions
**Mitigation:** Quality indicators and confidence scores (planned)

### 3. Lower Sampling Rate

**Issue:** Typical video (30-60fps) vs validated apps (120-240Hz)
**Impact:** Lower temporal resolution may reduce accuracy for rapid movements
**Comparison:**

- MyJump validated: 120Hz
- MyJumpLab validated: 240Hz
- Kinemotion typical: 30-60fps (2-4× lower)

**Mitigation:** Sub-frame interpolation, recommend 60fps minimum

### 4. Indirect Measurement Method

**Issue:** Landmarks → CoM estimation → velocity → phase detection
**Impact:** Error propagation through processing pipeline
**Comparison:**

- MyJump: Direct feet tracking → flight time
- Kinemotion: Landmarks → CoM → kinematic calculation (more steps = more error)

**Mitigation:** Robust filtering, outlier detection, physics checks

### 5. No Systematic Bias Correction

**Issue:** Bishop et al. (2022) showed correction factors needed for time-to-take-off when comparing manual vs automated detection
**Impact:** May have uncorrected systematic bias
**Example from Bishop 2022:**

- Raw TTTO had bias vs force plate
- Correction equation: `y = 0.8947x + 0.1507` eliminated bias

**Mitigation:** Correction factors will be derived after validation study

______________________________________________________________________

## Use Cases & Recommendations

### ✅ Appropriate Use Cases

#### 1. Training Monitoring

- Track jump performance trends over time
- Compare athlete's current vs baseline performance
- Monitor fatigue, training response, recovery
- **Why appropriate:** Relative changes don't require absolute accuracy

#### 2. Educational Purposes

- Learn biomechanics of jumping
- Understand video analysis methods
- Teach pose estimation technology
- **Why appropriate:** Educational value independent of validation

#### 3. Exploratory Research

- Pilot studies before formal testing
- Proof-of-concept investigations
- Methods development
- **Why appropriate:** Preliminary work, not final conclusions

#### 4. Self-Monitoring Athletes

- Personal training feedback
- Technique analysis
- Progress tracking
- **Why appropriate:** Self-directed, low-stakes context

### ❌ Inappropriate Use Cases

#### 1. Research Publications

- Cannot cite as validated measurement tool
- Reviewers will reject unvalidated instruments
- **Alternative:** Use validated equipment or conduct validation first

#### 2. Clinical Decision-Making

- Injury assessment
- Return-to-play clearance
- Treatment effectiveness
- **Why inappropriate:** Patient safety requires validated tools
- **Alternative:** Use clinical-grade force plates or validated apps

#### 3. Talent Identification

- Draft combines
- Team selection
- Athletic scholarships
- **Why inappropriate:** High-stakes decisions require validated accuracy
- **Alternative:** Use force plates or validated commercial systems

#### 4. Legal/Insurance Context

- Disability assessment
- Injury compensation
- Litigation evidence
- **Why inappropriate:** Legal scrutiny requires validated measurements
- **Alternative:** Only use validated, certified equipment

#### 5. Absolute Performance Comparisons

- Comparing athletes against normative data
- Setting performance standards
- Ranking athletes
- **Why inappropriate:** Unknown accuracy affects absolute values
- **Alternative:** Within-athlete comparisons only, or use validated equipment

______________________________________________________________________

## Validation Roadmap

### Planned Validation Activities (3 Months)

#### Phase 1: Internal Consistency (Month 1)

- Test-retest reliability (determinism test)
- Parameter sensitivity analysis
- Known height validation (dropped objects)
- Confidence scoring implementation

#### Phase 2: Comparative Validation (Month 2)

- Manual frame selection comparison (vs MyJump method)
- Inter-device reliability study
- Frame rate sensitivity analysis
- Validation utilities module

#### Phase 3: Documentation & Publication (Month 3)

- Physics-based sanity checks
- Environmental condition testing
- Technical validation report
- Preprint publication (OSF/SportRxiv)

#### Expected Outcomes

- Test-retest ICC calculated
- Correlation with manual method (target: r>0.95)
- Known limitations documented
- Optimal recording conditions established

**What This Will NOT Provide:**

- Force plate validation (requires lab access)
- Peer-reviewed publication (requires longer timeline)
- Clinical validation (requires patient populations)

### Future Validation (When Lab Access Available)

**Gold Standard Validation:**

1. Force plate comparison study (n≥20 subjects)
1. Calculate ICC, bias, limits of agreement
1. Derive correction factors if needed
1. Publish in peer-reviewed journal

**Target Metrics:**

- ICC > 0.90 (excellent reliability)
- Bias \< 2cm (per Balsalobre-Fernández et al., 2015)
- 95% of differences within ±5cm

For detailed roadmap, see [`docs/development/validation-roadmap.md`](development/validation-roadmap.md).

______________________________________________________________________

## Recommended Recording Setup

### To Maximize Accuracy (Based on MediaPipe Literature)

**Camera Setup:**

- **Frame rate:** 60fps minimum (higher is better)
- **Resolution:** 1920×1080 or higher
- **Distance:** 2-3 meters from athlete
- **Angle:** Lateral view (sagittal plane), perpendicular to movement
- **Height:** Tripod-mounted at mid-torso height
- **Stability:** Fixed position (no handheld)

**Environment:**

- **Lighting:** Bright, even lighting (avoid shadows)
- **Background:** Plain, uncluttered background
- **Surface:** Indoor gym preferred (consistent conditions)

**Athlete:**

- **Clothing:** Fitted clothing (compression gear ideal)
- **Visibility:** Ensure full body visible throughout jump
- **Framing:** Capture from head to feet with margin

**Avoid:**

- Dim lighting or backlighting
- Loose, baggy clothing
- Cluttered backgrounds
- Handheld/moving camera
- Partial occlusion of body
- Very low frame rates (\<30fps)

______________________________________________________________________

## Frequently Asked Questions

### Q: Can I use kinemotion for my research study?

**A:** Not as a validated measurement instrument. You can:

- Use it for pilot/exploratory work
- Compare it against validated equipment
- Conduct your own validation study
- Cite it as experimental software

**Do not:**

- Claim validated accuracy
- Use as primary outcome measure
- Compare against normative data

______________________________________________________________________

### Q: How does kinemotion compare to MyJump?

**A:**

- **MyJump:** Validated (ICC=0.997 vs force plate), published, widely used in research
- **Kinemotion:** Unvalidated, experimental, not suitable for research

**If you need validated measurements, use MyJump or similar validated apps.**

______________________________________________________________________

### Q: Why should I use kinemotion instead of MyJump?

**A:** You probably shouldn't if you need validated accuracy. Use kinemotion if:

- You want free, open-source software
- You need fully automated analysis (no manual frame selection)
- You're doing exploratory work
- You want to understand/modify the algorithms
- You're tracking relative changes (not absolute accuracy)

______________________________________________________________________

### Q: Can I track my own training progress with kinemotion?

**A:** Yes! For personal use tracking relative changes over time, kinemotion is appropriate. Just understand:

- Absolute jump height values may have unknown error
- Relative changes (trends) more reliable than absolute values
- Use consistent recording setup for comparability
- Consider validation if making training decisions

______________________________________________________________________

### Q: When will kinemotion be validated?

**A:**

- **Short-term (3 months):** Internal validation, manual comparison, technical report
- **Long-term (when lab access available):** Force plate validation, peer-review publication
- **No timeline:** Depends on resources and collaborations

______________________________________________________________________

### Q: Can I cite kinemotion in my paper?

**A:** You can cite the software repository, but:

- **Cannot claim:** "Validated measurement tool"
- **Can say:** "Experimental video analysis software"
- **Must note:** "Not validated against gold standard equipment"
- **Recommend:** Validate yourself or use alongside validated instruments

**Proper citation:**

```text
Kinemotion (version X.X.X) [Software]. (2025). Retrieved from https://github.com/feniix/kinemotion

Note: Kinemotion is experimental software not validated against force plates.
Measurements should be interpreted with caution.
```

______________________________________________________________________

## Contact & Contributions

### Report Issues

If you discover accuracy issues or unexpected behavior:

- Open an issue: <https://github.com/feniix/kinemotion/issues>
- Include video specifications, detection results, expected vs actual

### Contribute to Validation

If you have access to validation equipment (force plates, motion capture):

- Contact maintainers about collaboration
- Share validation data (with appropriate permissions)
- Contribute to validation roadmap

### Stay Updated

- Watch the repository for validation study updates
- Check `docs/validation/` for new validation reports
- See `CHANGELOG.md` for validation-related improvements

______________________________________________________________________

## References

### Validation Literature

- **Balsalobre-Fernández et al. (2015)** - MyJump validation against force plates (ICC=0.997)
- **Bishop et al. (2022)** - MyJumpLab validation with correction factors
- **Armstrong et al. (2025)** - MediaPipe Pose validation for clinical kinematics
- **Bland & Altman (1986)** - Methods for assessing agreement between measurements

### Biomechanics Theory

- **Bosco et al. (1983)** - Flight-time method for jump height calculation
- **Samozino et al. (2014)** - Force-velocity imbalance and jump performance
- **Dempster (1955)** - Body segment parameters for biomechanical modeling

### Methodological Standards

- **McGraw & Wong (1996)** - Intraclass correlation coefficient calculation
- **Hopkins (2000)** - Measures of reliability in sports medicine

______________________________________________________________________

## Document Changelog

**Version 1.0 (2025-01-13):**

- Initial validation status documentation
- Comprehensive limitations disclosure
- Use case recommendations
- Validation roadmap overview
