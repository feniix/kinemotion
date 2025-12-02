# Test Suite Review - December 2025

**Status**: ✅ 78.67% coverage | ⚠️ Organizational issues found | 🔄 Action required

## Quick Summary

**Current State**: 174 test functions across 23 test files. Strong test quality with excellent edge case coverage and documentation, but suffers from:

1. ❌ Naming inconsistencies (module vs function focus)
1. ❌ Misplaced test files (wrong directory)
1. ❌ 8 modules without dedicated tests (including critical validation.py and pose.py)

**Overall Grade**: B+ (Production-ready for MVP, needs cleanup before Phase 2)

______________________________________________________________________

## Critical Issues Requiring Immediate Action

### 🔴 P0 - Week 1 (Critical Path)

#### 1. Misplaced Test File

**File**: `tests/core/test_adaptive_threshold.py`

- **Problem**: Tests `dropjump/analysis.py` but located in `tests/core/`
- **Action**: Move to `tests/dropjump/test_adaptive_threshold.py`
- **Estimated Time**: 15 minutes
- **Command**:
  ```bash
  git mv tests/core/test_adaptive_threshold.py tests/dropjump/test_adaptive_threshold.py
  # Update imports if needed
  uv run pytest tests/dropjump/test_adaptive_threshold.py
  ```

#### 2. Missing Critical Tests: core/validation.py

**Module**: `src/kinemotion/core/validation.py`

- **Problem**: Base validation classes (ValidationResult, MetricsValidator, AthleteProfile) have no dedicated tests
- **Impact**: Validation framework bugs could affect all metrics validation
- **Action**: Create `tests/core/test_validation.py`
- **Estimated Time**: 2 hours
- **Priority Tests**:
  - ValidationResult initialization and to_dict()
  - MetricsValidator abstract methods
  - AthleteProfile value objects
  - Edge cases: missing data, invalid severity levels

#### 3. Missing Critical Tests: core/pose.py

**Module**: `src/kinemotion/core/pose.py`

- **Problem**: Only `compute_center_of_mass()` tested (via test_com_estimation.py)
- **Gap**: Pose extraction, landmark confidence handling, tracking failures
- **Action**: Rename `test_com_estimation.py` → `test_pose.py` and expand
- **Estimated Time**: 2 hours
- **Priority Tests**:
  - Pose detection with MediaPipe
  - Low confidence landmark handling
  - Tracking failure recovery
  - Empty frame handling

#### 4. Documentation Fix

**File**: `CLAUDE.md`

- **Problem**: Claims "519 tests" but actual count is 174 test functions
- **Action**: Update test count and add test organization section
- **Estimated Time**: 10 minutes

______________________________________________________________________

## 🟡 P1 - Weeks 2-3 (High Priority)

### Consolidate Fragmented Tests

#### 5. Video I/O Tests Consolidation

**Files**: `test_video_io.py` + `test_aspect_ratio.py`

- **Problem**: Video I/O functionality split across two files
- **Option A**: Merge test_aspect_ratio.py into test_video_io.py
- **Option B**: Rename to `test_video_io_rotation.py` for clarity
- **Estimated Time**: 30 minutes

#### 6. Smoothing Tests Consolidation

**Files**: `test_smoothing.py` + `test_polyorder.py`

- **Problem**: Polynomial order tests separate from main smoothing tests
- **Option A**: Merge test_polyorder.py into test_smoothing.py
- **Option B**: Rename to `test_smoothing_polyorder.py`
- **Estimated Time**: 30 minutes

### Add Missing High-Priority Tests

#### 7. core/auto_tuning.py Tests

**Currently**: Only tested indirectly via API tests

- **Create**: `tests/core/test_auto_tuning.py`
- **Test Coverage**:
  - Quality preset calculations (fast, balanced, accurate)
  - AnalysisParameters validation
  - Parameter boundary checks
  - Preset overrides
- **Estimated Time**: 1.5 hours

#### 8. core/metadata.py Tests

**Currently**: No tests found

- **Create**: `tests/core/test_metadata.py`
- **Test Coverage**:
  - Video metadata extraction
  - Frame rate detection
  - Duration calculation
  - Edge cases (corrupted metadata, missing fields)
- **Estimated Time**: 1 hour

______________________________________________________________________

## 🟢 P2 - Month 2 (Medium Priority)

### 9. Add Test Type Markers

**Goal**: Categorize tests by type (unit/integration/e2e)

**Implementation**:

```python
# In conftest.py or pytest.ini
import pytest

# Register markers
pytest.mark.unit     # Fast, isolated
pytest.mark.integration  # Multiple components
pytest.mark.e2e      # Full pipeline

# Usage
@pytest.mark.unit
def test_velocity_calculation():
    ...

@pytest.mark.integration
def test_cmj_full_pipeline():
    ...
```

**Benefits**:

- Run fast unit tests during development: `pytest -m unit`
- Run comprehensive suite before commit: `pytest`
- Skip slow e2e tests in CI: `pytest -m "not e2e"`

**Estimated Time**: 2 hours (add markers to existing tests)

### 10-12. Add Debug Overlay Tests

**Missing Coverage**:

- `tests/core/test_debug_overlay_utils.py` (0% coverage)
- `tests/cmj/test_debug_overlay.py` (0% coverage)
- `tests/dropjump/test_debug_overlay.py` (minimal coverage)

**Rationale**: Debug overlays are lower priority (acceptable 10-36% coverage per qa-test-engineer.md), but should have basic smoke tests.

**Estimated Time**: 1 hour each (3 hours total)

### 13. Create Testing Standards Document

**File**: `docs/development/testing-standards.md`

**Contents**:

1. Test file naming conventions (mirror source structure)
1. When to use class-based vs function-based organization
1. Test type categorization (unit/integration/e2e)
1. Edge case testing checklist
1. Parameterized test guidelines

**Estimated Time**: 2 hours

______________________________________________________________________

## Test File Organization Map

### Current Structure vs Ideal Structure

| **Current**                             | **Issue**                 | **Ideal**                                                    |
| --------------------------------------- | ------------------------- | ------------------------------------------------------------ |
| `tests/core/test_adaptive_threshold.py` | ❌ Wrong location         | `tests/dropjump/test_adaptive_threshold.py`                  |
| `tests/core/test_com_estimation.py`     | ⚠️ Function-focused name  | `tests/core/test_pose.py` (with CoM tests)                   |
| `tests/core/test_polyorder.py`          | ⚠️ Parameter-focused name | Part of `test_smoothing.py` or `test_smoothing_polyorder.py` |
| `tests/core/test_aspect_ratio.py`       | ⚠️ Feature-focused name   | Part of `test_video_io.py` or `test_video_io_rotation.py`    |

### Missing Test Files (8 modules)

| **Module**                  | **Priority** | **Current Coverage** | **Action**                           |
| --------------------------- | ------------ | -------------------- | ------------------------------------ |
| core/validation.py          | P0 🔴        | Indirect only        | Create `test_validation.py`          |
| core/pose.py                | P0 🔴        | Partial (CoM only)   | Expand to full `test_pose.py`        |
| core/auto_tuning.py         | P1 🟡        | Indirect (API tests) | Create `test_auto_tuning.py`         |
| core/metadata.py            | P1 🟡        | None                 | Create `test_metadata.py`            |
| core/cli_utils.py           | P2 🟢        | None                 | Create `test_cli_utils.py`           |
| core/debug_overlay_utils.py | P2 🟢        | None                 | Create `test_debug_overlay_utils.py` |
| cmj/debug_overlay.py        | P2 🟢        | None                 | Create `test_debug_overlay.py`       |
| dropjump/debug_overlay.py   | P2 🟢        | Minimal              | Expand `test_debug_overlay.py`       |

______________________________________________________________________

## What's Working Well ✅

### 1. Excellent Test Documentation

CMJ analysis tests include biomechanical context in docstrings:

```python
def test_phase_progression_temporal_constraints() -> None:
    """Test temporal constraints between CMJ phases are physically plausible.

    Biomechanical context: CMJ phases must satisfy time constraints:
    - Eccentric (squat down): typically 0.3-0.8s (9-24 frames at 30fps)
    - Concentric (push up): typically 0.2-0.5s (6-15 frames at 30fps)
    ...
    """
```

**Impact**: Helps domain experts (coaches, biomechanics researchers) understand test intent.

### 2. Comprehensive Edge Case Coverage

- Empty arrays, single-frame videos
- Boundary conditions (zero velocity, perfect stillness)
- Numerical stability (division by zero, very small time steps)
- Examples: 81 edge case tests added in recent CMJ expansion

### 3. Maintainable CLI Test Patterns

- **Tier 1** (stable): Exit codes, file creation
- **Tier 2** (semi-stable): Loose text matching
- **Tier 3** (fragile): Avoided hardcoded output strings
- Well-documented rationale in test file headers

### 4. Zero Fixture Duplication

- Centralized in `conftest.py`: `cli_runner`, `minimal_video`, `sample_video_path`
- No fixture redefinition found across 23 test files ✅

### 5. Consistent AAA Pattern

- Arrange-Act-Assert pattern used throughout
- Clear separation with comments in complex tests

______________________________________________________________________

## Testing Standards Checklist

Use this checklist when creating new tests or reviewing existing ones:

### Test File Organization

- [ ] Test file mirrors source module structure (`test_pose.py` for `pose.py`)
- [ ] Test file in correct directory (tests/core/ for src/kinemotion/core/)
- [ ] Imports use absolute paths (`from kinemotion.core.pose import ...`)

### Test Naming

- [ ] Test function starts with `test_`
- [ ] Name describes what is being tested (not how)
- [ ] Edge cases explicitly marked in name (e.g., `test_velocity_with_empty_array`)

### Test Structure

- [ ] Follows AAA pattern (Arrange-Act-Assert)
- [ ] Has descriptive docstring (especially for complex tests)
- [ ] Tests one thing (single responsibility)
- [ ] Uses appropriate assertions (`np.testing.assert_allclose` for floats)

### Test Coverage

- [ ] Happy path tested
- [ ] Edge cases tested (empty, single element, boundary values)
- [ ] Error cases tested (invalid input, exceptions)
- [ ] Numerical stability tested (very small/large values)

### Test Quality

- [ ] Fast (\<1s for unit tests, \<10s for integration)
- [ ] Deterministic (no random timing, network calls)
- [ ] Isolated (doesn't depend on test order)
- [ ] Cleans up resources (uses tmp_path, closes files)

______________________________________________________________________

## Action Plan Summary

### Week 1 (6 hours)

1. [ ] Move test_adaptive_threshold.py to dropjump/ (15 min)
1. [ ] Create tests/core/test_validation.py (2 hours)
1. [ ] Rename/expand tests/core/test_pose.py (2 hours)
1. [ ] Update CLAUDE.md test count (10 min)
1. [ ] Run full test suite and verify coverage maintained

### Weeks 2-3 (5 hours)

6. [ ] Consolidate test_aspect_ratio.py into test_video_io.py (30 min)
1. [ ] Consolidate test_polyorder.py into test_smoothing.py (30 min)
1. [ ] Create tests/core/test_auto_tuning.py (1.5 hours)
1. [ ] Create tests/core/test_metadata.py (1 hour)
1. [ ] Document testing standards (1.5 hours)

### Month 2 (Optional - 6 hours)

11. [ ] Add pytest markers (unit/integration/e2e) (2 hours)
01. [ ] Add debug overlay tests (3 hours)
01. [ ] Create test matrix visualization (1 hour)

______________________________________________________________________

## Validation

After completing action items, verify:

```bash
# 1. All tests pass
uv run pytest

# 2. Coverage maintained/improved
uv run pytest --cov-report=html
# Check htmlcov/index.html - should be >= 78.67%

# 3. No linter errors
uv run ruff check --fix
uv run pyright

# 4. Test organization correct
# Verify test file locations match source structure
ls -la tests/core/ tests/cmj/ tests/dropjump/ tests/cli/
```

______________________________________________________________________

## Questions or Issues?

- **Not sure which priority to tackle first?** Start with P0 items (week 1)
- **Need help writing tests for a specific module?** Refer to existing test patterns in similar modules
- **Coverage dropped after refactoring?** Run `pytest --cov --cov-branch` to identify missing branches
- **Tests failing in CI but passing locally?** Check for MediaPipe/multiprocessing issues (see `skip_in_ci` marker usage)

______________________________________________________________________

**Document Status**: ✅ Active
**Last Updated**: December 2, 2025
**Next Review**: After P0 actions completed
