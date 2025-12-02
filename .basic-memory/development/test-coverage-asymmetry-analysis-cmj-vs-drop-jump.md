---
title: 'Test Coverage Asymmetry Analysis: CMJ vs Drop Jump'
type: note
permalink: development/test-coverage-asymmetry-analysis-cmj-vs-drop-jump-1
tags:
- testing
- coverage
- cmj
- dropjump
- gap-analysis
---

# Test Coverage Asymmetry Analysis: CMJ vs Drop Jump

## Summary
The test coverage between CMJ and Drop Jump is **NOT equivalent**. There are significant gaps in both directions, some justified by algorithmic differences, others representing missing test coverage.

## Test File Inventory

### CMJ-Specific Tests (4 files, ~3,345 lines)
1. `test_cmj_analysis.py` (1,550 lines) - Phase detection, helper functions, validation
2. `test_cmj_joint_angles.py` (1,031 lines) - Triple extension, athlete profiles
3. `test_cmj_kinematics.py` (189 lines) - Metrics calculation
4. `test_cmj_physiological_bounds.py` (559 lines) - Comprehensive bounds validation
5. `test_joint_angles.py` (616 lines) - **DUPLICATE** of CMJ joint angles (older version)

### Drop Jump-Specific Tests (4 files, ~722 lines)
1. `test_adaptive_threshold.py` (202 lines) - Adaptive velocity threshold
2. `test_contact_detection.py` (223 lines) - Ground contact detection
3. `test_dropjump_validation_integration.py` (211 lines) - Basic validation
4. `test_kinematics.py` (86 lines) - Metrics calculation

### Shared/Core Tests (11 files)
- `test_api.py` (436 lines) - **Drop Jump API only**
- `test_cli_cmj.py` (395 lines)
- `test_cli_dropjump.py` (397 lines)
- `test_aspect_ratio.py`, `test_cli_imports.py`, `test_com_estimation.py`, `test_filtering.py`, `test_formatting.py`, `test_polyorder.py`, `test_video_io.py`

## Critical Gaps

### Drop Jump Missing (High Priority)
1. **API Testing** - No test_dropjump_api.py equivalent to test_api.py
2. **Comprehensive Physiological Bounds** - Only 211 lines vs CMJ's 559 lines
3. **Comprehensive Analysis Testing** - No equivalent to test_cmj_analysis.py (1,550 lines)

### CMJ Missing (High Priority)
1. **API Testing** - test_api.py only tests Drop Jump, CMJ API untested

### Algorithm-Specific (Justified Asymmetry)
- **CMJ has, Drop Jump doesn't need**: Joint angle testing (CMJ-specific feature)
- **Drop Jump has, CMJ doesn't need**: Adaptive threshold, contact detection (Drop Jump-specific algorithms)

## Detailed Gap Analysis

### 1. API Testing Gap
**Current**: test_api.py (436 lines) only tests Drop Jump
- ✅ Drop Jump: process_dropjump_video, bulk processing, quality presets, expert overrides
- ❌ CMJ: No tests for process_cmj_video, process_cmj_videos_bulk

**Impact**: CMJ API is untested at integration level

### 2. Physiological Bounds Gap
**CMJ**: test_cmj_physiological_bounds.py (559 lines)
- Comprehensive athlete profile testing (elderly, untrained, recreational, trained, elite)
- RSI bounds per profile
- Triple extension bounds
- Metric consistency validation
- Edge cases and boundary conditions

**Drop Jump**: test_dropjump_validation_integration.py (211 lines)
- Basic validation integration
- RSI calculation
- Dual height validation
- **Missing**: Comprehensive bounds per athlete profile

**Impact**: Drop Jump validation is less robust than CMJ

### 3. Analysis Testing Gap
**CMJ**: test_cmj_analysis.py (1,550 lines)
- Phase detection (standing, eccentric, concentric, takeoff, landing)
- Helper function tests (find_takeoff_frame, find_lowest_frame, etc.)
- Phase progression validation
- Biomechanical profiles (recreational, elite, failed jump)
- Edge cases (double bounce, boundary conditions)

**Drop Jump**: Fragmented across multiple files
- test_contact_detection.py (223 lines) - Contact detection only
- test_adaptive_threshold.py (202 lines) - Threshold calculation only
- **Missing**: Comprehensive phase detection and analysis testing

**Impact**: Drop Jump phase detection is less thoroughly tested

### 4. Joint Angle Testing (Justified Asymmetry)
**CMJ**: test_cmj_joint_angles.py (1,031 lines) + test_joint_angles.py (616 lines duplicate)
- Triple extension analysis is CMJ-specific feature
- Not applicable to Drop Jump

**Drop Jump**: None needed (algorithm doesn't use joint angles)

### 5. Algorithm-Specific Tests (Justified Asymmetry)
**Drop Jump specific**:
- test_adaptive_threshold.py (202 lines) - Drop Jump uses adaptive thresholds
- test_contact_detection.py (223 lines) - Drop Jump uses contact detection

**CMJ specific**:
- Uses phase progression and velocity zero-crossings instead

## Recommendations

### Priority 1: Critical Gaps
1. **Create test_cmj_api.py** - Mirror test_api.py for CMJ
   - Test process_cmj_video with all quality presets
   - Test process_cmj_videos_bulk
   - Test expert parameter overrides
   - Test JSON/video output
   - Test error handling

2. **Create test_dropjump_physiological_bounds.py** - Comprehensive bounds testing
   - Contact time bounds per athlete profile
   - Flight time bounds per athlete profile
   - RSI bounds per profile
   - Jump height bounds per profile
   - Metric consistency validation

3. **Create test_dropjump_analysis.py** - Comprehensive phase detection
   - Drop start detection
   - Contact phase detection
   - Flight phase detection
   - Landing detection
   - Phase ordering validation
   - Edge cases and boundary conditions

### Priority 2: Cleanup
4. **Remove test_joint_angles.py** - Duplicate of test_cmj_joint_angles.py
5. **Expand test_dropjump_validation_integration.py** - Add more validation scenarios

## Test Coverage Summary

| Category | CMJ Lines | Drop Jump Lines | Gap |
|----------|-----------|-----------------|-----|
| Analysis | 1,550 | 425 (fragmented) | CMJ +1,125 |
| Joint Angles | 1,647 (incl. dup) | 0 (N/A) | Justified |
| Physiological Bounds | 559 | 211 | CMJ +348 |
| API | 0 | 436 | DJ +436 |
| Kinematics | 189 | 86 | CMJ +103 |
| Algorithm-Specific | 0 | 425 | DJ +425 (justified) |

**Total CMJ-specific**: ~3,345 lines
**Total Drop Jump-specific**: ~722 lines
**Ratio**: CMJ has 4.6x more test coverage than Drop Jump

## Conclusion
The test asymmetry is **partially justified** by algorithmic differences (joint angles, contact detection) but reveals **significant gaps** in:
1. CMJ API testing (completely missing)
2. Drop Jump physiological bounds (incomplete)
3. Drop Jump comprehensive analysis testing (fragmented)

These gaps should be addressed to ensure equivalent test quality and confidence across both jump types.
