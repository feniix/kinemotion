---
title: Squat Jump Implementation Plan
type: note
permalink: biomechanics/squat-jump-implementation-plan
---

# Squat Jump Implementation Plan

## Overview
Adding Squat Jump (SJ) as the third assessment jump to kinemotion, completing the "3 assessment jumps" suite (SJ, CMJ, Drop Jump).

## What is Squat Jump?

**Biomechanical Definition:**
- Starts in static squat position (no countermovement)
- Pure concentric phase only (no stretch-shortening cycle)
- Athlete holds squat position briefly, then explodes upward
- Measures pure concentric power output

**Key Differences from CMJ:**
| Feature | CMJ | Squat Jump |
|---------|-----|------------|
| Start | Standing | Static squat |
| Countermovement | Yes | No |
| Eccentric phase | Yes | No |
| Power measured | Indirect | Direct calculation |

## Module Architecture

### File Structure
```
src/kinemotion/squat_jump/
├── __init__.py              # Exports: SJPhase, process_sj_video
├── cli.py                   # sj-analyze command
├── analysis.py              # SJ phase detection
├── kinematics.py            # Power, force, velocity calculations
├── metrics_validator.py     # SJ metrics validation
├── validation_bounds.py     # SJ-specific bounds
└── debug_overlay.py         # SJ visualization

tests/squat_jump/
├── __init__.py
├── test_analysis.py         # Phase detection tests
├── test_kinematics.py       # Power calculation tests
├── test_cli.py              # CLI tests
├── test_validation.py       # Bounds tests
└── fixtures.py              # SJ-specific fixtures
```

### SJ Phases
```python
class SJPhase(Enum):
    SQUAT_HOLD = "squat_hold"    # Static start position (NEW)
    CONCENTRIC = "concentric"    # Upward movement
    FLIGHT = "flight"            # In the air
    LANDING = "landing"          # Ground contact
    UNKNOWN = "unknown"
```

## Key Metrics

### SJ-Specific Metrics
| Metric | Description | Formula |
|--------|-------------|---------|
| Jump Height | From flight time | h = g × t² / 8 |
| Flight Time | Time airborne | t_flight |
| **Peak Power** | Max power output | P = (m × (a + g)) × v |
| **Mean Power** | Average power | P_mean = Work / t |
| **Peak Force** | Max ground reaction force | F = m × (a + g) |
| Peak Concentric Velocity | Max upward velocity | From pose data |

### Metrics NOT in SJ
- ❌ Countermovement depth (no countermovement)
- ❌ Eccentric duration (no eccentric phase)
- ❌ Peak eccentric velocity (no downward motion)

## Implementation Phases

### Phase 1: Foundation (Low Complexity)
**Agent:** Python Backend Developer

**Tasks:**
- Create `src/kinemotion/squat_jump/` directory
- Implement `__init__.py` with exports
- Implement `cli.py` with `sj-analyze` command
- Register command in `src/kinemotion/cli.py`

**CLI Command:**
```bash
kinemotion sj-analyze video.mp4 --mass 75.0  # Athlete mass in kg
```

### Phase 2: Core Detection (Medium Complexity)
**Agents:** Biomechanics Specialist + Computer Vision Engineer

**Tasks:**
- Implement `analysis.py` with SJ phase detection
  - `detect_squat_start()`: Static hold detection
  - `detect_takeoff()`: Similar to CMJ
  - `detect_landing()`: Reuse from CMJ
- Implement `kinematics.py` with power calculations

**Static Start Detection:**
```python
def detect_squat_start(landmarks: NDArray) -> int:
    """
    Detect start frame where athlete is holding squat position.

    Criteria:
    - Vertical velocity near zero (< 0.1 m/s for 0.3s)
    - Knee angle ~90° (70-110° acceptable)
    - Hip angle flexed
    - Position stable for minimum hold time
    """
```

### Phase 3: Validation (Medium Complexity)
**Agents:** Biomechanics Specialist + ML/Data Scientist

**Tasks:**
- Implement `validation_bounds.py` with SJBounds
  - Jump height: similar to CMJ
  - Flight time: similar to CMJ
  - Power metrics: need literature values
- Implement `metrics_validator.py` extending MetricsValidator
- Auto-tune parameters for SJ detection

### Phase 4: Visualization (Low Complexity)
**Agent:** Computer Vision Engineer

**Tasks:**
- Implement `debug_overlay.py` for SJ visualization
- Reuse existing overlay patterns
- Show squat hold, concentric, flight, landing phases

### Phase 5: Testing (Medium Complexity)
**Agent:** QA Engineer

**Tasks:**
- Create test fixtures
- Test phase detection edge cases
- Test power calculations with known values
- CLI integration tests
- Validation bounds tests

**Target:** 80%+ coverage (matching existing modules)

### Phase 6: Documentation (Low Complexity)
**Agent:** Technical Writer

**Tasks:**
- Add SJ guide to `docs/guides/`
- Update API reference
- Update CLAUDE.md with SJ support
- Add SJ to "Supported Analysis Types"

## Complexity & ROI Assessment

| Aspect | Rating | Notes |
|--------|--------|-------|
| **Overall Complexity** | Medium | Leverages existing core, static start detection is new |
| **Foundation** | Low | Follows existing pattern |
| **Detection** | Medium | Static start detection is new challenge |
| **Metrics** | Medium | Power calculations need athlete mass parameter |
| **Testing** | Medium | Needs test videos of proper SJ form |
| **Impact** | High | Completes "3 assessment jumps" suite |
| **Strategic Value** | High | Core athletic testing tool |

**ROI Score: 3.8**
- High impact (completes assessment jump suite)
- High strategic value (core athletic tool)
- Medium complexity

## Technical Decisions

### 1. Athlete Mass Parameter
**Decision:** Require athlete mass as CLI parameter
```bash
kinemotion sj-analyze video.mp4 --mass 75.0  # kg
```
**Rationale:** Power calculations require mass: P = (m × (a + g)) × v

### 2. Static Start Detection
**Decision:** Velocity threshold + joint angle stability
**Criteria:**
- Vertical velocity < 0.1 m/s for 0.3s
- Knee angle: 70-110°
- Hip angle: flexed
- Position stable

### 3. Power Calculation
**Formula:** P(t) = (mass × (acceleration + gravity)) × velocity(t)
- Peak power: max(P(t)) during concentric phase
- Mean power: ∫P(t)dt / t_concentric

### 4. Validation Bounds
**Source:** Literature search needed for:
- Peak power by athlete profile
- Mean power by athlete profile
- Peak force by athlete profile

**Starting Point:** SJ jump height similar to CMJ (slightly lower, ~5-10%)

## Agent Coordination

| Agent | Phase | Responsibilities |
|-------|-------|------------------|
| **Biomechanics Specialist** | 2, 3 | Validate SJ metrics, define bounds |
| **Python Backend Developer** | 1, 2 | Implement module structure |
| **Computer Vision Engineer** | 2, 4 | Adapt pose detection for static start |
| **ML/Data Scientist** | 3 | Auto-tune SJ parameters |
| **QA Engineer** | 5 | Test coverage |
| **Technical Writer** | 6 | Documentation |

## Next Steps

1. **Biomechanics validation**: Confirm SJ metrics and bounds
2. **Create module structure**: Follow existing patterns
3. **Implement detection algorithm**: Static start detection
4. **Add comprehensive tests**: 80%+ coverage
5. **Documentation updates**: Guides and API reference

## References

- Science for Sport: "Squat Jump" (2025)
- Kinvent: "The Basics of the 3 Assessment Jumps" (2024)
- Samozino et al. (2008): "A simple method for measuring force, velocity and power output during squat jump"
- MDPI Sports (2024): "Beyond Jump Height: A Comparison of Concentric Variables in the Squat Jump, Countermovement Jump and Drop Jump"
