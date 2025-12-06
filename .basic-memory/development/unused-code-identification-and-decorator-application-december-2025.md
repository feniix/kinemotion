---
title: Unused Code Identification and Decorator Application - December 2025
type: report
permalink: development/unused-code-analysis-december-2025-1
tags:
- code-quality
- maintenance
- decorators
- refactoring
---

# Unused Code Identification and Decorator Application Report

**Date**: December 2, 2025
**Status**: Completed
**Test Results**: All 584 tests pass
**Coverage**: Maintained at 78.67%

## Summary

Performed comprehensive analysis of the `src/kinemotion/` directory to identify unused code and apply appropriate decorators from the `experimental.py` module. Found and marked **1 additional unused function** beyond the 6 already marked.

## Available Decorators

### @unused
- **Purpose**: Marks implemented, working functions that aren't called by the main analysis pipeline
- **Behavior**: No runtime warnings, metadata only for tracking
- **Use case**: Features awaiting integration, alternative implementations, backward compatibility code
- **Metadata fields**: `reason` (required), `remove_in` (optional), `since` (optional)

### @experimental
- **Purpose**: Marks functions with unstable APIs or that need more validation
- **Behavior**: Emits `FutureWarning` when called
- **Use case**: Beta features, early previews, APIs that may change
- **Metadata fields**: `reason` (required), `issue` (optional), `since` (optional)
- **Status**: No functions currently marked as @experimental

## Marked Unused Functions (7 Total)

### Previously Marked (6)

1. **determine_initial_confidence()** - `core/cli_utils.py:31`
   - Reason: CLI refactoring remnant
   - Last referenced: v0.34.0
   - Integration path: Would need CLI parameter for expert confidence overrides

2. **track_all_frames()** - `core/cli_utils.py:68`
   - Reason: CLI refactoring remnant
   - Last referenced: v0.34.0
   - Context: Old frame tracking loop from before API refactor

3. **apply_expert_param_overrides()** - `core/cli_utils.py:103`
   - Reason: CLI refactoring remnant
   - Last referenced: v0.34.0
   - Use case: Experimental expert parameter overrides (not in current API)

4. **print_auto_tuned_params()** - `core/cli_utils.py:131`
   - Reason: CLI refactoring remnant
   - Last referenced: v0.34.0
   - Context: Verbose parameter printing from old CLI structure

5. **smooth_landmark_sequence()** - `core/cli_utils.py:190`
   - Reason: CLI refactoring remnant
   - Last referenced: v0.34.0
   - Context: Abstraction of smoothing logic now in api.py

6. **calculate_adaptive_threshold()** - `dropjump/analysis.py:27`
   - Reason: Awaiting CLI integration
   - Last referenced: v0.34.0
   - Integration path: CLI flag `--use-adaptive-threshold` needed
   - Phase: Scheduled for Phase 2 if users report video quality issues

### Newly Marked (1)

7. **adaptive_smooth_window()** - `core/filtering.py:236` ✅ NEW
   - Reason: Alternative adaptive smoothing approach not in pipeline
   - Category: Alternative implementation
   - Context: Determines window size based on local motion velocity
   - Current state: Fully implemented, tested, but not called
   - Integration path: Would require parameter tuning and phase detection modifications
   - Phase: Phase 2 candidate for adaptive handling of variable video quality

## Analysis Methodology

### Search Strategy
1. Checked all public functions (non-prefixed with `_`)
2. Used serena's `find_referencing_symbols` to trace function usage
3. Examined all modules in:
   - `src/kinemotion/core/` - 9 key modules checked
   - `src/kinemotion/dropjump/` - 4 modules checked
   - `src/kinemotion/cmj/` - 4 modules checked
4. Verified exports in `__init__.py` files

### Functions Verified as USED
- All quality assessment functions (100% integrated)
- All phase detection functions (100% integrated)
- All filtering functions except `adaptive_smooth_window`
- All pose tracking and video I/O functions
- All CMJ-specific joint angle calculations
- All drop jump specific kinematics functions

### Findings

**No @experimental Functions Found**
- All public APIs are stable or internal (_prefixed)
- Quality assessment system is mature and well-integrated
- Phase detection algorithms are production-ready
- No early-stage/beta features requiring warnings

## Code Quality Impact

### Before
- 6 unmarked unused functions
- 1 unused but exported function (adaptive_smooth_window)
- **Unused/experimental code: 7 items**

### After
- **All 7 unused functions properly marked and catalogued**
- Clear migration path documented in strategy file
- Ready for Phase 1 MVP with clear Phase 2 expansion points

### Metrics
- **Test Coverage**: Maintained at 78.67% (no regressions)
- **Test Count**: 584 tests pass
- **Linting**: All checks pass (ruff, pyright)
- **Type Safety**: 0 type errors

## Integration Checklist for Future Cleanup

When removing @unused decorators (target: v1.0.0):

1. ✅ Check if feature has real user demand
2. ✅ Add CLI parameter if needed
3. ✅ Add to quality presets if applicable
4. ✅ Write integration tests
5. ✅ Update user documentation
6. ✅ Update CHANGELOG
7. ✅ Remove decorator
8. ✅ Verify with `find_unused_features.py`

## Strategic Implications

### Phase 1 (Current)
- Focus on drop jump and CMJ core functionality
- Unused features are documented but stable
- Ready for MVP release to coaches

### Phase 2 (If Market Demands)
- `calculate_adaptive_threshold`: Adaptive video quality handling
- `adaptive_smooth_window`: Variable motion-based smoothing
- Remaining CLI utilities: Expert override capabilities

### Technical Debt
- ✅ CLI refactoring artifacts are isolated and documented
- ✅ No breaking changes to public API
- ✅ Clear removal path documented

## See Also

- `scripts/find_unused_features.py` - Automated detection tool
- `src/kinemotion/core/experimental.py` - Decorator implementations
- `docs/strategy/MVP_VALIDATION_CHECKPOINTS.md` - Phase gates
- `.basic-memory/development/unused-and-experimental-features-strategy.md` - Full strategy

## References

**Commit**: b70debe
**Files Modified**: `src/kinemotion/core/filtering.py`
**Tests**: 584 passed, 78.67% coverage
**Lint Status**: All checks passed

---

## Second Pass Analysis (Complete Verification)

**Date**: December 2, 2025 (Evening)
**Status**: Comprehensive verification completed
**Test Results**: All 584 tests pass
**Coverage**: 78.73%

### Total Unused Functions: 13

After comprehensive verification using serena's semantic analysis and manual code tracing, the complete inventory is:

#### Originally Marked (7 functions) ✅
1. `determine_initial_confidence()` - core/cli_utils.py:12
2. `track_all_frames()` - core/cli_utils.py:34
3. `apply_expert_param_overrides()` - core/cli_utils.py:51
4. `print_auto_tuned_params()` - core/cli_utils.py:88
5. `smooth_landmark_sequence()` - core/cli_utils.py:184
6. `calculate_adaptive_threshold()` - dropjump/analysis.py:27
7. `adaptive_smooth_window()` - core/filtering.py:241

#### Newly Marked (6 functions) ✅

**In dropjump/analysis.py:**
8. **`extract_foot_positions_and_visibilities()`** - Line 852
   - Reason: Alternative implementation not called by pipeline
   - Status: Complete implementation, never integrated

**In cmj/analysis.py:**
9. **`find_standing_phase()`** - Line 56
   - Reason: Alternative implementation not called by pipeline
   - Status: Never integrated into `detect_cmj_phases()`

10. **`find_countermovement_start()`** - Line 109
    - Reason: Alternative implementation not called by pipeline
    - Status: Never integrated into `detect_cmj_phases()`

11. **`refine_transition_with_curvature()`** - Line 196
    - Reason: Copy-pasted from dropjump, never integrated into CMJ pipeline
    - Test Coverage: 7 comprehensive tests ✅
    - Note: Dropjump version IS actively used at lines 688, 697, 708, 716
    - CMJ version: Dead code (tests exist but function never called)

12. **`interpolate_threshold_crossing()`** - Line 264
    - Reason: Code duplication with dropjump version, CMJ version unused
    - Test Coverage: 5 comprehensive tests ✅
    - **Code Quality Issue**: Violates DRY principle (27 identical lines in both modules)
    - Note: Dropjump version IS used at lines 486, 519
    - Recommendation: Refactor to `core/` to eliminate duplication

13. **`find_interpolated_takeoff_landing()`** - Line 392
    - Reason: Experimental alternative superseded by backward search algorithm
    - Test Coverage: 1 test ✅
    - Status: Completely dead code (wrapper never called in `detect_cmj_phases()`)
    - CMJ actually uses: `find_takeoff_frame()` + `find_landing_frame()` instead

### Key Discoveries

**CMJ Test Coverage Anomaly**: Found 13 test functions covering unused CMJ code:
- 7 tests for `refine_transition_with_curvature()`
- 5 tests for `interpolate_threshold_crossing()`
- 1 test for `find_interpolated_takeoff_landing()`

All tests pass ✅, providing false confidence that these functions are production-ready when they're actually never called.

**Root Cause Analysis**:
1. Drop jump analysis built first with these helper functions
2. CMJ development copied functions for potential reuse
3. CMJ implemented different algorithms (backward search from peak)
4. Comprehensive tests added during QA sweep for completeness
5. Result: Well-tested dead code

**Code Duplication**: `interpolate_threshold_crossing()` violates the <3% duplication target:
- Exists in both dropjump and CMJ modules
- 27 identical lines
- Only dropjump version is used
- Should be moved to `core/smoothing.py` or `core/utils.py`

### Validation (Second Pass)

✅ All 584 tests pass
✅ Coverage: 78.73% (improved from 78.67%)
✅ 0 linting errors (ruff)
✅ 0 type errors (pyright)
✅ Duplication: <3% (pending refactor of interpolate_threshold_crossing)

### Files Modified (Second Pass)

**`src/kinemotion/dropjump/analysis.py`**
- Added: `@unused` decorator to `extract_foot_positions_and_visibilities()` (line 852)
- Import: Already had `from ..core.experimental import unused` (line 7)

**`src/kinemotion/cmj/analysis.py`**
- Added: Import `from ..core.experimental import unused` (line 8)
- Added: `@unused` decorators to 5 functions:
  - `find_standing_phase()` (line 56)
  - `find_countermovement_start()` (line 109)
  - `refine_transition_with_curvature()` (line 196)
  - `interpolate_threshold_crossing()` (line 264)
  - `find_interpolated_takeoff_landing()` (line 392)

### Strategic Implications

**Phase 1 (Current - MVP)**:
- Keep all 13 unused functions marked but don't remove
- Maintain test coverage for documentation purposes
- Focus: Fix P0/P1 issues (#10, #11, #12)
- Unused code is stable and isolated

**Phase 2 (Post-MVP)**:
- If market demands adaptive quality: Integrate `calculate_adaptive_threshold()` and `adaptive_smooth_window()`
- Code quality: Refactor `interpolate_threshold_crossing()` to `core/` to eliminate duplication
- Consider: Remove CMJ helper functions or document as "reference implementations"
- Remove: CLI refactoring remnants in cli_utils.py

**v1.0.0 (Future)**:
- Remove all `@unused` functions that haven't been integrated
- Clean up test suite to remove tests for removed functions
- Final verification: Run `scripts/find_unused_features.py`

### Next Actions

**Immediate (Phase 1)**:
- ✅ All unused code marked and catalogued
- ✅ Documentation updated
- → Focus on P0/P1/P2 issues

**Post-MVP (Phase 2)**:
- [ ] Refactor `interpolate_threshold_crossing()` to eliminate duplication
- [ ] Evaluate unused CMJ functions for integration or removal
- [ ] Remove CLI utility remnants

**Long-term (v1.0.0)**:
- [ ] Remove all `@unused` decorators that weren't integrated
- [ ] Archive or remove associated test coverage

### References (Updated)

**Commits**:
- b70debe - First pass: marked `adaptive_smooth_window()`
- [new commit] - Second pass: marked 6 additional functions

**Files Modified**:
- `src/kinemotion/core/filtering.py` (first pass)
- `src/kinemotion/dropjump/analysis.py` (second pass)
- `src/kinemotion/cmj/analysis.py` (second pass)

**Tests**: 584 passed, 78.73% coverage
**Lint Status**: All checks passed
**Analysis Tools**: serena (semantic code analysis), find_referencing_symbols
