---
title: CMJ Validation Implementation Complete
type: note
permalink: biomechanics/cmj-validation-implementation-complete
tags:
  - cmj
  - validation
  - implementation
  - bounds
  - testing
---

# CMJ Validation Implementation - Complete Delivery

## Summary

Successfully defined and implemented comprehensive physiological bounds for CMJ metrics validation, including:

- **2 new Python modules** for validation framework
- **60 unit tests** covering all bounds and edge cases
- **3 athlete profile examples** with expected metric ranges
- **Detailed biomechanical documentation** in basic-memory

## Deliverables

### 1. Core Validation Modules

#### File: `src/kinemotion/core/cmj_validation_bounds.py` (137 lines)

Defines physiological bounds using `MetricBounds` dataclass:

```python
class CMJBounds:
    FLIGHT_TIME = MetricBounds(0.08, 0.15, 0.25, 0.70, 0.65, 1.10, 1.30, "s")
    JUMP_HEIGHT = MetricBounds(0.02, 0.05, 0.15, 0.60, 0.65, 1.00, 1.30, "m")
    COUNTERMOVEMENT_DEPTH = MetricBounds(0.05, 0.08, 0.20, 0.55, 0.40, 0.75, 1.10, "m")
    CONCENTRIC_DURATION = MetricBounds(0.08, 0.10, 0.40, 0.90, 0.25, 0.50, 1.80, "s")
    # ... plus eccentric, total movement, peak velocities, RSI, triple extension
```

**Features**:

- Profile-aware bounds checking
- Athlete classification based on jump height
- RSI validation with profile ranges
- Triple extension angle validation
- Pre-defined athlete profile fixtures

#### File: `src/kinemotion/core/cmj_metrics_validator.py` (696 lines)

Comprehensive validation engine with `CMJMetricsValidator` class:

```python
class CMJMetricsValidator:
    def validate(metrics: dict) -> ValidationResult
```

**Features**:

- **11 validation checks** organized by category
- **3 severity levels**: ERROR, WARNING, INFO
- **Cross-validation** of metric consistency
- **Edge case detection** with profile-specific rules
- **Detailed issue reporting** with bounds information

**Validation checks**:

1. Flight time bounds
1. Jump height bounds
1. Countermovement depth bounds
1. Concentric duration (contact time) bounds
1. Eccentric duration bounds
1. Peak velocity validation
1. Flight time ↔ jump height consistency
1. Peak velocity ↔ jump height consistency
1. RSI validity and profile appropriateness
1. Depth-to-height ratio check
1. Contact-depth ratio check
1. Triple extension angles

### 2. Test Suite

File: `tests/test_cmj_physiological_bounds.py` (500+ lines)

**60 unit tests** organized into 14 test classes:

- `TestAthleteProfileEstimation` (5 tests)
- `TestFlightTimeBounds` (6 tests)
- `TestJumpHeightBounds` (4 tests)
- `TestCountermovementDepthBounds` (6 tests)
- `TestContactTimeBounds` (5 tests)
- `TestPeakVelocityBounds` (6 tests)
- `TestRSIBounds` (6 tests)
- `TestTripleExtensionBounds` (6 tests)
- `TestMetricsConsistency` (4 tests)
- `TestRecreationalAthleteProfile` (2 tests)
- `TestEliteAthleteProfile` (4 tests)
- `TestEdgeCases` (4 tests)
- `TestValidationSeverityLevels` (3 tests)

**Test Coverage**:

- All 60 tests PASS
- 74.50% coverage for validator module
- 83.42% coverage for bounds module

______________________________________________________________________

## Key Physiological Bounds Defined

### Flight Time (seconds)

| Profile          | Range        |
| ---------------- | ------------ |
| Absolute Min/Max | 0.08 - 1.30s |
| Elderly          | 0.15 - 0.70s |
| Recreational     | 0.25 - 0.70s |
| Elite            | 0.65 - 1.10s |

### Jump Height (meters)

| Profile          | Range        |
| ---------------- | ------------ |
| Absolute Min/Max | 0.02 - 1.30m |
| Elderly          | 0.05 - 0.60m |
| Recreational     | 0.15 - 0.60m |
| Elite            | 0.65 - 1.00m |

### Countermovement Depth (meters)

| Profile          | Range        |
| ---------------- | ------------ |
| Absolute Min/Max | 0.05 - 1.10m |
| Elderly          | 0.08 - 0.55m |
| Recreational     | 0.20 - 0.55m |
| Elite            | 0.40 - 0.75m |

### Contact Time (Concentric Duration)

| Profile          | Range        |
| ---------------- | ------------ |
| Absolute Min/Max | 0.08 - 1.80s |
| Elderly          | 0.10 - 0.90s |
| Recreational     | 0.40 - 0.90s |
| Elite            | 0.25 - 0.50s |

### Peak Velocities

**Eccentric (downward)**:

- Elderly: 0.20-1.00 m/s
- Recreational: 0.80-2.00 m/s
- Elite: 2.00-3.50 m/s

**Concentric (upward)**:

- Elderly: 0.50-1.50 m/s
- Recreational: 1.80-2.80 m/s
- Elite: 3.00-4.20 m/s

### Reactive Strength Index (RSI)

| Profile         | Range       |
| --------------- | ----------- |
| Physical Limits | 0.30 - 4.00 |
| Elderly         | 0.15 - 0.30 |
| Untrained       | 0.30 - 0.80 |
| Recreational    | 0.80 - 1.50 |
| Trained         | 1.50 - 2.40 |
| Elite           | 2.20 - 3.50 |

### Triple Extension Angles at Takeoff

**Hip Angle** (degrees from vertical):

- Elderly: 150-165°
- Recreational: 160-180°
- Elite: 170-185°

**Knee Angle**:

- Elderly: 155-170°
- Recreational: 165-182°
- Elite: 173-190°

**Ankle Angle** (plantarflexion):

- Elderly: 100-125°
- Recreational: 110-140°
- Elite: 125-155°

______________________________________________________________________

## Athlete Profiles

### Profile 1: Elderly/Deconditioned (10-15cm jump)

- **Jump Height**: 0.10-0.18m
- **Flight Time**: 0.14-0.19s
- **Countermovement Depth**: 0.12-0.20m (shallow squat)
- **Contact Time**: 0.80-1.20s (slow propulsion)
- **RSI**: 0.15-0.25 (very poor)

### Profile 2: Recreational Athlete (35-55cm jump)

- **Jump Height**: 0.35-0.55m
- **Flight Time**: 0.53-0.67s
- **Countermovement Depth**: 0.28-0.45m (moderate squat)
- **Contact Time**: 0.45-0.65s
- **RSI**: 0.85-1.25 (moderate)

### Profile 3: Elite Male Athlete (65-90cm jump)

- **Jump Height**: 0.68-0.88m
- **Flight Time**: 0.74-0.84s
- **Countermovement Depth**: 0.42-0.62m (deep squat)
- **Contact Time**: 0.28-0.42s (fast, powerful)
- **RSI**: 2.20-2.80 (excellent)

______________________________________________________________________

## Edge Cases Handled

1. **Minimal Countermovement**: Valid if internally consistent (RSI, velocity)
1. **Deep Squat**: Valid for tall athletes with excellent mobility
1. **Double-Bounce Pattern**: Detected and flagged for review
1. **Incomplete Eccentric Phase**: Marked in metadata, metrics still valid
1. **High RSI with Low Jump Height**: Flagged as detection error
1. **Shallow Depth/High Jump**: Indicates standing position detection failure
1. **Contact Time Too Short**: Suggests lowest point detection error

______________________________________________________________________

## Validation Severity Levels

### ERROR

- Metrics physically impossible
- Likely video processing failure
- Examples: jump height >1.3m, flight time \<0.08s, RSI >4.0

### WARNING

- Metrics physically possible but unusual
- Outside typical range for profile
- Examples: RSI 0.5 for recreational, shallow squat with high jump

### INFO

- Normal variation, informational
- Metrics within expected range
- Consistent cross-validation checks

______________________________________________________________________

## Cross-Validation Features

**Automatic Consistency Checks**:

1. **Flight Time ↔ Jump Height**

   - Formula: h = g·t²/8
   - Tolerance: 10% error

1. **Peak Velocity ↔ Jump Height**

   - Formula: h = v²/(2g)
   - Tolerance: 15% error

1. **Depth-to-Height Ratio**

   - Normal range: 0.3-1.5
   - Validates standing position detection

1. **Contact-Depth Ratio**

   - Range: 0.5-2.5 s/m
   - Validates propulsion efficiency

______________________________________________________________________

## Integration Points

### Using the Validator

```python
from kinemotion.core.cmj_metrics_validator import CMJMetricsValidator
from kinemotion.core.cmj_validation_bounds import AthleteProfile

# Auto-detect profile from metrics
validator = CMJMetricsValidator()
result = validator.validate(metrics_dict)

# Or specify profile
validator = CMJMetricsValidator(assumed_profile=AthleteProfile.ELITE)
result = validator.validate(metrics_dict)

# Check results
if result.status == "PASS":
    print("✓ Valid metrics")
elif result.status == "PASS_WITH_WARNINGS":
    print("⚠ Check warnings")
    for issue in result.issues:
        print(f"  {issue.severity.value}: {issue.message}")
else:
    print("✗ Errors detected")
```

### Bounds Usage

```python
from kinemotion.core.cmj_validation_bounds import CMJBounds, AthleteProfile

# Check if value is physically possible
if CMJBounds.JUMP_HEIGHT.is_physically_possible(0.5):
    print("✓ Possible")

# Check if in range for profile
if CMJBounds.JUMP_HEIGHT.contains(0.5, AthleteProfile.RECREATIONAL):
    print("✓ Within recreational range")
```

______________________________________________________________________

## Testing

All tests pass with comprehensive coverage:

```bash
uv run pytest tests/test_cmj_physiological_bounds.py -v
# Result: 60 passed in 3.53s
```

**Coverage**:

- cmj_metrics_validator.py: 74.50%
- cmj_validation_bounds.py: 83.42%

______________________________________________________________________

## Documentation Reference

Full documentation stored in basic-memory:

- **biomechanics/CMJ Physiological Bounds for Validation**: Complete reference with:
  - 12 sections covering all metrics
  - Biomechanical rationale for each bound
  - Research references
  - Pseudo-code validation logic
  - Edge case handling guidelines

______________________________________________________________________

## Next Steps for Integration

1. **Import modules** in existing CMJ analysis pipeline
1. **Call validator** after metric calculation
1. **Store validation results** in quality assessment metadata
1. **Add validation output** to debug overlays
1. **Use bounds** for CLI error reporting

Example integration point in `src/kinemotion/cmj/analysis.py`:

```python
from kinemotion.core.cmj_metrics_validator import CMJMetricsValidator

# After calculating metrics
validator = CMJMetricsValidator()
validation = validator.validate({
    'jump_height': metrics.jump_height,
    'flight_time': metrics.flight_time,
    # ... other fields
})

# Store in quality assessment
metrics.result_metadata.validation_result = validation
```

______________________________________________________________________

## Files Created

1. `/src/kinemotion/core/cmj_validation_bounds.py` - Bounds definitions
1. `/src/kinemotion/core/cmj_metrics_validator.py` - Validation engine
1. `/tests/test_cmj_physiological_bounds.py` - 60 unit tests
1. Memory note: `biomechanics/CMJ Physiological Bounds for Validation` - Full reference

**Total lines of code**: ~1,300 lines (bounds + validator + tests)
