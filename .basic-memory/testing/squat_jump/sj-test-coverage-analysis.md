---
title: SJ Test Coverage Analysis
type: note
permalink: testing/squat-jump/sj-test-coverage-analysis
---

## Squat Jump Test Suite Coverage Report

**Overall Status:** 32.79% coverage (37 failed, 38 passed)

### Test Results by Category:

#### 1. Kinematics Tests (test_kinematics.py)
- **Status:** ✅ 10/12 tests passing
- **Coverage:** 60.38% (kinematics.py)
- **Key Findings:**
  - Basic metrics calculation works correctly when mass is None
  - Power/force calculations raise NotImplementedError (expected - Biomechanics Specialist pending)
  - Frame index type conversions fixed (float to int)

#### 2. Analysis Tests (test_analysis.py)
- **Status:** ❌ 0/13 tests passing (setup failures)
- **Coverage:** 17.65% (analysis.py)
- **Issues:** Missing fixtures causing setup failures
- **Fix Applied:** Created conftest.py to expose fixtures from fixtures.py

#### 3. Validation Tests (test_validation.py)
- **Status:** ❌ 11/11 tests failing
- **Coverage:** 85.56% (metrics_validator.py) - but tests failing
- **Issues:** Tests calling undefined functions like estimate_squat_jump_athlete_profile instead of estimate_athlete_profile

#### 4. CLI Tests (test_cli.py)
- **Status:** ❌ 16/22 tests passing (some failures)
- **Coverage:** 71.43% (cli.py)
- **Key Findings:**
  - Batch processing works (multiple files)
  - Expert parameters validation works
  - Help output works
  - Many tests failing due to NotImplementedError in SJ functionality

### Module Coverage Breakdown:

| Module | Coverage | Status |
|--------|----------|---------|
| validation_bounds.py | 100.00% | ✅ Perfect |
| metrics_validator.py | 85.56% | ✅ High (but tests failing) |
| cli.py | 71.43% | ✅ Good |
| kinematics.py | 60.38% | ✅ Moderate |
| api.py | 46.25% | ⚠️ Needs work |
| analysis.py | 17.65% | ❌ Low (fixture issues) |
| debug_overlay.py | 16.22% | ❌ Low |

### Priority Fixes Needed:

1. **High Priority:**
   - Fix validation test function name (estimate_athlete_profile vs estimate_squat_jump_athlete_profile)
   - Resolve analysis test fixture issues
   - Implement power/force calculations in kinematics.py

2. **Medium Priority:**
   - Improve api.py coverage (currently 46.25%)
   - Fix CLI test failures related to NotImplementedError handling

3. **Low Priority:**
   - Improve debug_overlay.py coverage (optional feature)

### Next Steps:

1. Route to biomechanics-specialist for power/force implementation
2. Fix validation test function names
3. Implement proper error handling in CLI for NotImplementedError cases
4. Update coverage expectations to reflect partially implemented state
