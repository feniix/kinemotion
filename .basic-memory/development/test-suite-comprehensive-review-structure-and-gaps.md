---
title: Test Suite Comprehensive Review - Structure and Gaps
type: note
permalink: development/test-suite-comprehensive-review-structure-and-gaps
---

# Test Suite Comprehensive Review - Structure and Gaps

## Current State (December 2, 2025)
- **438 tests passed**
- **Coverage: 77.57%** (improved from 74.27% cited in CLAUDE.md)
- **21 test files** at root level (tests/)
- **1 test file** in tests/core/ subdirectory (test_quality.py)
- **15 fixtures** defined inline across test files (no centralized conftest.py)
- **8,748 lines** of test code

## Test File Organization

### Current Structure (Flat with minimal nesting)
```
tests/
├── test_*.py (21 files at root)
├── core/
│   └── test_quality.py (1 file)
└── __pycache__/
```

### Test Files by Category

#### CMJ Tests (5 files)
- test_cmj_analysis.py - CMJ phase detection
- test_cmj_kinematics.py - CMJ metrics calculation
- test_cmj_joint_angles.py - Triple extension angles
- test_cmj_physiological_bounds.py - CMJ validation bounds
- test_cmj_api.py - CMJ API wrapper tests

#### Drop Jump Tests (5 files)
- test_dropjump_analysis.py - Drop jump phase detection
- test_kinematics.py - Drop jump metrics (NAMING INCONSISTENCY: should be test_dropjump_kinematics.py)
- test_dropjump_physiological_bounds.py - Drop jump validation bounds
- test_dropjump_validation_integration.py - Integration tests
- test_dropjump_api.py - Drop jump API wrapper tests

#### Core Module Tests (8 files)
- test_filtering.py - core/filtering.py
- test_formatting.py - core/formatting.py
- test_video_io.py - core/video_io.py
- test_quality.py - core/quality.py (nested in tests/core/)
- test_contact_detection.py - Part of core/dropjump analysis (naming unclear)
- test_com_estimation.py - Core COM estimation utilities
- test_adaptive_threshold.py - Core adaptive threshold utilities
- test_aspect_ratio.py - core/video_io.py related (naming unclear)

#### Utility Tests (3 files)
- test_polyorder.py - Polyorder parameter validation
- test_cli_imports.py - CLI module import validation
- test_cli_cmj.py - CMJ CLI command tests
- test_cli_dropjump.py - Drop Jump CLI command tests

## Naming Inconsistencies

### Critical Issues
1. **test_kinematics.py** - Drop jump kinematics, should be **test_dropjump_kinematics.py**
   - Creates ambiguity with test_cmj_kinematics.py
   - Violates naming convention established for CMJ

2. **Generic concept files without jump-type prefix:**
   - test_contact_detection.py - Should be test_dropjump_contact_detection.py or test_dropjump_analysis.py
   - test_com_estimation.py - Should be test_core_com_estimation.py
   - test_adaptive_threshold.py - Should be test_dropjump_adaptive_threshold.py or test_core_adaptive_threshold.py
   - test_aspect_ratio.py - Should be test_video_io_aspect_ratio.py or test_core_aspect_ratio.py
   - test_polyorder.py - Should be test_core_polyorder.py or test_smoothing_polyorder.py

### Pattern Inconsistencies
- CMJ: test_cmj_<aspect>.py ✓ (consistent)
- Drop Jump: test_dropjump_<aspect>.py + test_<aspect>.py ✗ (mixed)
- Core: test_<module>.py + test_<concept>.py ✗ (mixed)
- CLI: test_cli_<type>.py ✓ (consistent)

## Coverage Gaps by Severity

### Critical Gaps (< 85%)
1. **core/smoothing.py: 74.53%**
   - 21 lines uncovered, 12 branches untested
   - Essential shared module for both jump types
   - Needs focused edge case testing

2. **cmj/cli.py: 70.34%**
   - WORST CLI coverage
   - 40+ lines uncovered
   - Error handling paths need testing

3. **dropjump/cli.py: 87.17%**
   - 15 lines uncovered
   - Error handling and validation edge cases

4. **dropjump/analysis.py: 88.15%**
   - 20 lines uncovered, 17 branches untested
   - Complex phase detection algorithm
   - Edge cases not fully tested

### Moderate Gaps (85-95%)
5. **dropjump/kinematics.py: 86.59%** - 12 lines uncovered, 12 branches
6. **core/pose.py: 88.46%** - 7 lines uncovered, 3 branches
7. **core/video_io.py: 91.26%** - 5 lines uncovered

### Acceptable Gaps (< 50%, by design)
- **dropjump/debug_overlay.py: 36.36%** - Visualization code (acceptable)
- **cmj/debug_overlay.py: 38.09%** - Visualization code (acceptable)

### Excellent Coverage (95%+)
- core/formatting.py: 100%
- dropjump/validation_bounds.py: 100%
- cmj/validation_bounds.py: 100%
- core/metadata.py: 96.05%
- core/validation.py: 95.45%
- core/quality.py: 95.92%
- dropjump/metrics_validator.py: 93.91%
- cmj/metrics_validator.py: 98.88%

## Fixture Organization Issues

### Current State
- 15 fixtures defined inline across test files
- **No centralized conftest.py** in tests/ directory
- **No shared fixture organization** across test modules
- Potential for duplication (e.g., sample_video_path defined in 2 files)

### Example Duplications
- `sample_video_path()` fixture defined in:
  - tests/test_cmj_api.py
  - tests/test_dropjump_api.py
- Should be centralized in conftest.py

## Test Organization Recommendations

### Directory Structure (Proposed)
```
tests/
├── conftest.py (shared fixtures)
├── core/
│   ├── conftest.py (core-specific fixtures)
│   ├── test_filtering.py
│   ├── test_video_io.py
│   ├── test_quality.py
│   ├── test_formatting.py
│   └── test_*.py (other core tests)
├── dropjump/
│   ├── conftest.py (drop jump fixtures)
│   ├── test_analysis.py
│   ├── test_kinematics.py (renamed from test_kinematics.py)
│   ├── test_physiological_bounds.py
│   └── test_api.py
├── cmj/
│   ├── conftest.py (CMJ fixtures)
│   ├── test_analysis.py
│   ├── test_kinematics.py
│   ├── test_joint_angles.py
│   ├── test_physiological_bounds.py
│   └── test_api.py
└── cli/
    ├── test_cmj.py
    ├── test_dropjump.py
    └── test_imports.py
```

## Test Naming Patterns

### Current Patterns
1. **Function naming**: test_<what>_<condition>_<expected>
   - Example: test_contact_detection_simple_pattern ✓
   - Example: test_find_standing_phase ✓

2. **Class naming**: Test<Feature>
   - Example: class TestDropStartDetection ✓
   - Example: class TestCMJCLIHelp ✓

### Issues
- Some tests use inconsistent function vs class organization
- Some functions test multiple behaviors (not atomic)
- File-level organization doesn't match source module structure

## Recent Refactoring Impact

### Changes from Recent Commits
- Validation base classes extracted to core/validation.py
- Validators moved to jump-specific modules:
  - cmj/metrics_validator.py
  - cmj/validation_bounds.py
  - dropjump/metrics_validator.py
  - dropjump/validation_bounds.py
- Reduced code duplication from 7.7% to < 1%
- Tests updated to reference new module paths

### Test File Updates Needed
- test_api.py was split into test_cmj_api.py and test_dropjump_api.py ✓
- test_joint_angles.py relates to cmj/joint_angles.py (test_cmj_joint_angles.py) ✓
- Import paths updated in test files to reflect new validator locations ✓

## Integration vs Unit Testing Strategy

### Current Approach
- Tests are organized by **feature/concept**, not strictly by module
- Integration testing focus:
  - test_cmj_physiological_bounds.py tests both validation_bounds.py and metrics_validator.py
  - test_dropjump_validation_integration.py tests full pipeline
  - Phase detection tests verify multiple functions working together

### Implications
- Strong testing of algorithm correctness ✓
- Good coverage of happy paths ✓
- Edge case coverage less consistent
- Error handling in CLI/API less tested

## Key Quality Indicators

### Strengths
1. Comprehensive metric validation (95%+ coverage)
2. Excellent test coverage of core algorithms
3. Good integration test coverage for jump analysis
4. Metrics validators thoroughly tested

### Weaknesses
1. CLI error handling under-tested (70-87%)
2. Visualization code deliberately low coverage (acceptable but could improve)
3. Signal processing (smoothing) has lowest critical coverage (74%)
4. Test file organization doesn't match source code structure
5. No centralized fixture management
6. Fixture duplication (sample_video_path)
7. Naming inconsistencies cause confusion

## Recommendations Summary

### Priority 1: Improve Core Coverage
1. Focus on core/smoothing.py (74.53%) - add edge cases
2. Improve CMJ CLI tests (70.34%) - error handling
3. Test CMJ analysis edge cases (85%+ but algorithm complex)

### Priority 2: Fix Naming Inconsistencies
1. Rename test_kinematics.py to test_dropjump_kinematics.py
2. Rename generic concept tests to include module prefix
3. Establish clear naming convention: test_<module>_<aspect>.py

### Priority 3: Improve Organization
1. Create tests/conftest.py for shared fixtures
2. Move tests into subdirectories (core/, dropjump/, cmj/, cli/)
3. Move test_quality.py from tests/core/ to tests/core/
4. Consolidate and de-duplicate fixtures

### Priority 4: Enhance Edge Case Testing
1. Add edge case tests for smoothing algorithms
2. Test CLI error conditions more thoroughly
3. Add regression tests for known bugs

## Test Count Details
- 438 tests collected by pytest (including parametrized variations)
- ~246 test functions/methods (unique tests)
- 8,748 lines of test code
