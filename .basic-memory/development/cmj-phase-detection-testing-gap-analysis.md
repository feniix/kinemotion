---
title: CMJ Phase Detection Testing Gap Analysis
type: note
permalink: development/cmj-phase-detection-testing-gap-analysis
tags:
  - testing
  - cmj
  - phase-detection
  - coverage-analysis
  - gap-analysis
---

# CMJ Phase Detection Testing Gap Analysis

## Executive Summary

**Current Coverage**: 88.24% for `src/kinemotion/cmj/analysis.py` (31 tests)

**Critical Gap**: Phase progression validation and regression testing for phase ordering and temporal constraints.

### CMJ Phase Architecture

```
1. STANDING → 2. ECCENTRIC (downward) → 3. TRANSITION (lowest point)
→ 4. CONCENTRIC (upward) → 5. FLIGHT → 6. LANDING
```

## Current Test Coverage (Detailed)

### Phase Detection Functions Tested (88.24% coverage):

- `detect_cmj_phases()` - Full CMJ phase detection (backward search from peak)
- `find_standing_phase()` - Initial standing detection
- `find_countermovement_start()` - Eccentric phase start
- `find_lowest_point()` - Transition point detection
- `find_cmj_takeoff_from_velocity_peak()` - Takeoff detection
- `find_cmj_landing_from_position_peak()` - Landing detection
- `refine_transition_with_curvature()` - Transition refinement
- `interpolate_threshold_crossing()` - Velocity threshold interpolation
- `compute_signed_velocity()` - Velocity calculation

### Untested Lines (Lines 95-98, 175, 348, 397-414, 430, 443, 451, 466, 472):

- Line 95-98: `find_standing_phase()` - Return None path (standing_count loop logic)
- Line 175: `find_lowest_point()` - Position fallback when search_end \<= start_frame
- Line 348: `find_cmj_landing_from_position_peak()` - Edge case handling
- Lines 397-414: `find_interpolated_takeoff_landing()` - Entire helper wrapper function (NOT CALLED IN TESTS)
- Lines 430, 443, 451, 466, 472: Helper functions (`_find_takeoff_frame`, `_find_lowest_frame`, `_find_landing_frame`, `_find_standing_end`) - FULLY UNTESTED

## Critical Gaps: Phase Progression Testing

### Gap 1: Phase Ordering Validation (NOT TESTED)

**What's missing**: Tests that verify phases occur in correct order:

- standing_end \< lowest_point \< takeoff \< peak_height \< landing
- Tests that phases maintain temporal sequence across different jump profiles

**Current state**: Individual phases tested in isolation. No tests verify:

- Phase sequence integrity
- Temporal constraints between phases
- Invalid phase orderings are caught

### Gap 2: Phase Transition Edge Cases (INCOMPLETE)

**What's missing**: Edge case tests for phase boundaries:

- What happens when phases overlap? (eccentric overlaps concentric)
- What if countermovement is too shallow? (lowest_point very close to standing)
- What if landing frame \< takeoff frame? (temporal inversion)
- Multiple peaks in vertical position? (bouncing)

### Gap 3: Regression Prevention Tests (MISSING)

**What's missing**: Tests for known biomechanically correct CMJ progressions:

- Deep squat CMJ (30-50cm height, 0.5-0.7s contact)
- Shallow squat CMJ (15-25cm height, 0.3-0.5s contact)
- Explosive CMJ (>60cm height, minimal contact time)
- Failed CMJ attempts (incomplete phases)

### Gap 4: Helper Function Coverage (0% - CRITICAL)

**Lines 397-414, 417-481**: Wrapper and helper functions have 0% coverage

- `find_interpolated_takeoff_landing()` - Wrapper function combining takeoff + landing
- `_find_takeoff_frame()` - Backward search peak detection
- `_find_lowest_frame()` - Velocity zero-crossing detection
- `_find_landing_frame()` - Impact detection after peak
- `_find_standing_end()` - Low-velocity detection before countermovement

These are used by the backward search algorithm in `detect_cmj_phases()` but only indirectly tested.

## Missing Test Cases (Specific Recommendations)

### 1. Phase Progression Validation Suite

```python
# Test: All phases must occur in correct temporal order
def test_phase_progression_ordering_valid_cmj():
    """Verify all phases occur in correct sequence for valid CMJ."""
    positions = create_valid_cmj_trajectory()
    result = detect_cmj_phases(positions, fps=30.0)

    standing, lowest, takeoff, landing = result

    # Phase ordering assertions
    if standing is not None:
        assert standing < lowest, "Standing must end before lowest point"
    assert lowest < takeoff, "Lowest point must be before takeoff"
    assert takeoff < landing, "Takeoff must be before landing"
    # Peak height is implicit in implementation, should be between takeoff and landing

def test_phase_progression_temporal_constraints():
    """Verify temporal constraints between phases."""
    # Eccentric-to-concentric transition should be <300ms
    # Flight duration should be <1000ms
    # Contact time should be >100ms
    ...

# Test: Invalid phase orderings trigger failures
def test_invalid_phase_progression_overlapping_eccentric_concentric():
    """Reject CMJ with overlapping eccentric/concentric phases."""
    # Create trajectory where lowest_point > takeoff_frame
    # Function should return None or normalize

def test_invalid_phase_progression_landing_before_takeoff():
    """Reject CMJ where landing occurs before takeoff."""
    # This is biomechanically impossible
    ...
```

### 2. Edge Cases in Phase Transitions

```python
def test_shallow_countermovement_lowest_point_close_to_standing():
    """Test detection when countermovement depth is minimal (elderly, weak)."""
    # Standing at frame 20, lowest at frame 25 (only 5 frames = 167ms at 30fps)
    # Should still detect correctly even with shallow squat

def test_multiple_position_peaks_chooses_global_maximum():
    """Test robustness to bouncing or multiple peaks."""
    # Create trajectory with small initial peak, then larger main peak
    # Function should use the global peak for backward search

def test_phase_detection_with_incomplete_jump():
    """Test handling of incomplete jumps (video cut off mid-flight)."""
    # Landing frame is beyond video length
    # Function should return None rather than crash

def test_very_fast_eccentric_concentric_transition():
    """Test ultra-quick athletes (minimal ground contact)."""
    # Eccentric: frames 50-100 (1.67s at 30fps)
    # Concentric: frames 100-110 (0.33s - very fast push)
    # Should detect all phases correctly
```

### 3. Regression Tests: Known Biomechanical Profiles

```python
def test_deep_squat_cmj_progression():
    """Regression test: Deep squat CMJ with validated metrics.

    Profile: Athlete performs ~40cm jump
    - Standing: 0-1s
    - Eccentric (squat): 1-1.5s (deep, >90° knee)
    - Transition: 1.5s
    - Concentric (push): 1.5-2.0s (explosive)
    - Flight: 2.0-2.5s
    - Landing: 2.5s
    """
    positions = generate_validated_deep_squat_cmj()
    standing, lowest, takeoff, landing = detect_cmj_phases(positions, fps=30.0)

    # Verify phase durations
    eccentric_duration = lowest - standing  # Should be 0.3-0.5s
    concentric_duration = takeoff - lowest  # Should be 0.2-0.4s
    flight_duration = landing - takeoff     # Should be 0.3-0.8s

    assert 9 <= eccentric_duration <= 15, f"Eccentric: {eccentric_duration} frames"
    assert 6 <= concentric_duration <= 12, f"Concentric: {concentric_duration} frames"
    assert 9 <= flight_duration <= 24, f"Flight: {flight_duration} frames"

def test_explosive_cmj_minimal_contact():
    """Regression test: Explosive athlete with minimal ground contact."""
    # Profile: >70cm jump, <300ms contact
    positions = generate_explosive_cmj()
    standing, lowest, takeoff, landing = detect_cmj_phases(positions, fps=30.0)

    contact_duration = takeoff - lowest
    assert contact_duration < 10, f"Explosive should have <300ms contact, got {contact_duration/30:.2f}s"

def test_failed_cmj_attempt():
    """Regression test: Handle failed/incomplete jump attempts."""
    # Athlete starts countermovement but doesn't complete it
    positions = generate_failed_cmj_trajectory()
    result = detect_cmj_phases(positions, fps=30.0)

    # Function should return None for invalid jump
    assert result is None, "Invalid jump should return None"
```

### 4. Helper Function Direct Tests (Lines 397-481)

```python
def test_find_interpolated_takeoff_landing_wrapper():
    """Test wrapper function find_interpolated_takeoff_landing."""
    positions = create_cmj_trajectory()
    velocities = compute_signed_velocity(positions)

    result = find_interpolated_takeoff_landing(positions, velocities, lowest_point_frame=50)

    assert result is not None
    takeoff, landing = result
    assert takeoff < landing, "Takeoff must be before landing"

def test_find_takeoff_frame_backward_search():
    """Test backward search for takeoff (peak velocity before peak height)."""
    # Create velocity profile with clear peak at frame 40
    velocities = np.concatenate([
        np.linspace(-0.01, -0.1, 20),  # Accelerating up
        np.array([-0.12, -0.11, -0.09]),  # Peak at frame 40-42
        np.linspace(-0.05, 0.01, 20),   # Decelerating
    ])

    takeoff = _find_takeoff_frame(velocities, peak_height_frame=60, fps=30.0)

    # Takeoff should be near the peak around frame 40-42
    assert 38 <= takeoff <= 45

def test_find_lowest_frame_velocity_zero_crossing():
    """Test finding lowest point via velocity zero-crossing (positive to negative)."""
    # Create trajectory where velocity crosses from positive (down) to negative (up)
    velocities = np.concatenate([
        np.ones(30) * 0.05,   # Downward motion
        np.linspace(0.05, -0.05, 10),  # Transition point around frame 35
        np.ones(30) * -0.05,   # Upward motion
    ])

    lowest = _find_lowest_frame(velocities, positions, takeoff_frame=60, fps=30.0)

    # Lowest should be near the zero-crossing at frame 35
    assert 33 <= lowest <= 37

def test_find_standing_end_low_velocity_detection():
    """Test finding end of standing phase via low velocity threshold."""
    # Standing (low velocity) before countermovement starts
    velocities = np.concatenate([
        np.ones(20) * 0.001,    # Standing - very low velocity
        np.ones(40) * 0.08,      # Countermovement starts
    ])

    standing_end = _find_standing_end(velocities, lowest_point=50)

    # Standing should end around frame 19-20
    if standing_end is not None:
        assert 15 <= standing_end <= 25
```

## Coverage Impact Assessment

### Estimated Improvements:

| Test Category                | New Tests       | Expected Coverage Gain | Priority     |
| ---------------------------- | --------------- | ---------------------- | ------------ |
| Phase progression validation | 4-5 tests       | +5-8%                  | CRITICAL     |
| Edge cases in transitions    | 3-4 tests       | +4-6%                  | HIGH         |
| Regression test suite        | 3-4 tests       | +3-5%                  | HIGH         |
| Helper function coverage     | 4-5 tests       | +6-8%                  | CRITICAL     |
| **TOTAL**                    | **14-18 tests** | **+18-27%**            | **CRITICAL** |

### Target: 88.24% → 96-99% (Phase detection module)

## Implementation Priority

1. **CRITICAL**: Helper function tests (Lines 397-481) - 0% coverage

   - Direct testing of backward search algorithm
   - Foundation for phase progression validation

1. **HIGH**: Phase progression validation

   - Tests that verify temporal constraints
   - Rejection of biomechanically impossible sequences

1. **HIGH**: Regression tests with validated CMJ profiles

   - Deep squat, explosive, minimal contact
   - Failed jump handling

1. **MEDIUM**: Edge case transitions

   - Overlapping phases, incomplete jumps, bouncing

## Alignment with Project Standards

- Follows AAA (Arrange, Act, Assert) pattern
- Uses synthetic test data with clear setup
- Tests one concept per function
- Includes edge cases and boundary conditions
- Deterministic (no random data)
- Tests both success and failure paths
- Includes docstrings explaining biomechanical context
