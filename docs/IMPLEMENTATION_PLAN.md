# Kinemotion Issues - Implementation Plan & Fix Guide

**Created**: 2025-01-26
**Purpose**: Step-by-step plan to resolve all identified issues with LLM prompts for implementation

## Overview

This document provides a structured implementation plan to fix all issues identified in ERRORS_FINDINGS.md, organized by priority with specific checklist items and LLM prompts for each fix.

## Priority Levels

- **P0**: Critical - Fix immediately (affects credibility/core functionality)
- **P1**: High - Fix within 1 week (major features/usability)
- **P2**: Medium - Fix within 2 weeks (consistency/quality)
- **P3**: Low - Fix within 1 month (nice-to-have improvements)

## Phase Completion Summary

| Phase | Status | Priority | Completion Date | Notes |
|-------|--------|----------|-----------------|-------|
| Phase 1: Critical Fixes | ✅ COMPLETE | P0 | 2025-01-26 | Removed accuracy claims, added disclaimers |
| Phase 1.5: CLI Refactoring | ✅ COMPLETE | P1 | 2025-01-26 | Modular CLI architecture established |
| Phase 2: Feature Connection | ✅ RESOLVED | P1 | 2025-01-26 | Features intentionally NOT exposed (design decision) |
| Phase 3: Algorithm Consistency | ✅ COMPLETE | P1 | 2025-01-26 | Velocity calculation unified, correction factor parameterized |
| Phase 4: Documentation | ✅ COMPLETE | P2 | 2025-01-26 | Feature docs + validation roadmap complete |
| Phase 5: Testing Improvements | ⏳ PENDING | P2 | - | Integration & regression tests needed |
| Phase 6: Type Safety | ⏳ PENDING | P3 | - | Type annotation improvements |
| Phase 7: Validation Infrastructure | ⏳ PENDING | P3 | - | Validation framework design |

**Overall Progress:** 5 / 8 phases complete (63%)

---

## Phase 1: Critical Fixes (P0 - Day 1) ✅ COMPLETED

### 1.1 Remove/Caveat Accuracy Claims ✅

**Checklist:**

- [x] Remove all specific accuracy percentages from README.md
- [x] Remove empirical correction factor or add validation
- [x] Add disclaimer about unvalidated measurements
- [x] Update all documentation with accuracy caveats

**Completed:** 2025-01-26
**Notes:**

- Removed all specific percentages (71%, 88%) from README.md
- Added prominent "Validation Status" section in README.md with comprehensive disclaimer
- Replaced accuracy claims with "theoretical benefits" and "⚠️ unvalidated" warnings throughout
- Added 16-line comment block in kinematics.py explaining correction factor is experimental/unvalidated
- Updated docs/PARAMETERS.md to caveat all accuracy improvement claims

**LLM Prompt:**

```text
Review README.md and remove all specific accuracy claims (71%, 88%, etc.). Replace with:
1. A disclaimer stating "Accuracy has not been validated against gold standard measurements"
2. Change "~88% accuracy" to "theoretically improved accuracy when calibrated"
3. Add a section called "Validation Status" explaining what has and hasn't been validated
4. In kinematics.py, add a comment above the 1.35x correction factor explaining it's unvalidated

Keep the technical explanations but remove specific percentages. Maintain professional tone.
```text

**Files modified:**

- README.md (lines 17, 26-34, 207, 311, 361, 405)
- docs/PARAMETERS.md (multiple sections: polyorder, filtering, calibration, curvature)
- src/kinemotion/dropjump/kinematics.py (lines 318-336, 340)

### 1.2 Fix Documentation File Paths ✅

**Checklist:**

- [x] Update CLAUDE.md with correct file locations
- [x] Verify all file references are accurate
- [ ] Add file structure validation test (deferred to Phase 5)

**Completed:** 2025-01-26
**Notes:**

- Verified that CLAUDE.md file paths are correct (video_io.py is in dropjump/ as documented)
- No changes needed - documentation was already accurate

**LLM Prompt:**

```text
In CLAUDE.md, find all references to "dropjump/video_io.py" and correct them to "core/video_io.py".
Also update the module structure diagram to reflect actual file organization:
- video_io.py is in core/ (shared functionality)
- debug_overlay.py is in dropjump/ (drop jump specific)

Ensure the architectural explanation matches this structure.
```text

**Files verified:**

- CLAUDE.md (module structure section - all paths verified correct)

---

## Phase 1 Summary

**Status:** ✅ COMPLETED (2025-01-26)

**Changes Made:**

1. Removed all specific accuracy percentages from documentation
2. Added prominent validation disclaimer in README.md
3. Updated all "accuracy improvement" claims to "theoretical benefits" with warnings
4. Documented correction factor as experimental/unvalidated with comprehensive comments
5. Verified documentation file paths are correct

**Testing:**

- ✅ All 47 tests passing
- ✅ Ruff linting passes (100%)
- ✅ Mypy type checking passes (100%)
- ✅ No regressions introduced

**Impact:**

- Addresses critical credibility issue
- Maintains transparency about tool capabilities
- Professional tone while acknowledging limitations
- Clear path forward for validation work

---

## Phase 1.5: CLI Refactoring (Completed 2025-01-26) ✅

### CLI Modularization

**Checklist:**

- [x] Move dropjump-analyze command to src/kinemotion/dropjump/cli.py
- [x] Simplify main CLI to entry point only
- [x] Register command using cli.add_command()
- [x] Update all documentation to reflect new structure
- [x] Verify all tests pass after refactoring

**Completed:** 2025-01-26

**Notes:**

- Moved all dropjump-analyze command logic from src/kinemotion/cli.py to src/kinemotion/dropjump/cli.py
- Main CLI reduced from 358 lines to 20 lines (entry point only)
- Command registration uses Click's add_command() pattern
- All 47 tests passing after refactoring
- No functional changes - purely structural

**Changes Made:**

1. Created src/kinemotion/dropjump/cli.py with complete dropjump_analyze command
2. Simplified src/kinemotion/cli.py to just CLI group definition and command registration
3. Updated CLAUDE.md module structure to reflect new CLI architecture
4. Updated IMPLEMENTATION_PLAN.md to document refactoring

**Files Modified:**

- src/kinemotion/dropjump/cli.py (created - 358 lines)
- src/kinemotion/cli.py (simplified - 20 lines)
- docs/IMPLEMENTATION_PLAN.md (this file)
- CLAUDE.md (module structure updated)

**Benefits:**

- **Modularity**: Drop jump code self-contained in dropjump/ module
- **Scalability**: Easy to add new jump types (CMJ, squat) as sibling modules
- **Maintainability**: Clear separation - main CLI is just entry point
- **Future-ready**: Pattern established for adding new analysis types

**Testing:**

- ✅ All 47 tests passing
- ✅ Ruff linting passes (100%)
- ✅ Mypy type checking passes (100%)
- ✅ CLI functionality verified - all commands work as before

**Next Steps:**
This refactoring prepares the codebase for adding new jump type analysis commands:

- Future CMJ analysis: src/kinemotion/cmj/cli.py
- Future squat jump: src/kinemotion/squat/cli.py
- Each module follows same pattern for consistency

---

## Phase 2: Feature Connection (P1 - Days 2-3) ✅ RESOLVED - NOT APPLICABLE

### 2.1 CoM Tracking - NOT EXPOSED (Intentional Design Decision) ✅

**Status:** ✅ RESOLVED - Not applicable for drop jump analysis

**Decision:** CoM tracking is intentionally NOT exposed in the `dropjump-analyze` command.

**Rationale:**

- Drop jump videos are typically **~3 seconds long** (standing on box → drop → contact → jump)
- **No stationary baseline period** available for CoM calibration
- CoM tracking offers **no practical advantages** for drop jump analysis
- Foot tracking is more reliable for the specific biomechanics of drop jumps

**Implementation:**

- CoM tracking code exists in `core/pose.py` (fully functional and tested)
- Hardcoded `use_com=False` in dropjump CLI (line 335)
- Available for **future jump types** (CMJ, squat jump) that have longer videos with baseline periods

**Files Status:**

- ✅ src/kinemotion/core/pose.py - CoM calculation fully implemented
- ✅ src/kinemotion/dropjump/cli.py - Intentionally does NOT expose --use-com flag
- ✅ docs/CLAUDE.md - Documented reasoning (lines 424-437)

### 2.2 Adaptive Threshold - NOT EXPOSED (Intentional Design Decision) ✅

**Status:** ✅ RESOLVED - Not applicable for drop jump analysis

**Decision:** Adaptive threshold is intentionally NOT exposed in the `dropjump-analyze` command.

**Rationale:**

- Adaptive threshold requires **~5+ seconds** of video with **3 seconds of standing baseline**
- Drop jump videos start with immediate action (no standing period)
- **Insufficient baseline data** to calculate adaptive threshold reliably
- Fixed velocity threshold is appropriate for drop jump biomechanics

**Implementation:**

- Adaptive threshold code exists in `core/filtering.py` (fully functional and tested)
- Fixed `velocity_threshold` parameter used (default: 0.02, configurable via CLI)
- Available for **future jump types** (CMJ, squat jump) with adequate baseline periods

**Files Status:**

- ✅ src/kinemotion/core/filtering.py - Adaptive threshold fully implemented
- ✅ src/kinemotion/dropjump/cli.py - Intentionally does NOT expose --adaptive-threshold flag
- ✅ docs/CLAUDE.md - Documented reasoning (lines 424-437)

**Future Work:**
When adding CMJ (countermovement jump) or squat jump analysis:

- These jump types have longer videos (~5-10 seconds) with stationary baseline
- Expose `--use-com` and `--adaptive-threshold` in those commands
- Pattern: `src/kinemotion/cmj/cli.py` with full feature exposure
- Core modules ready to support these features

---

## Phase 3: Algorithm Consistency (P1 - Days 4-5) ✅ COMPLETED

### 3.1 Fix Velocity Calculation Consistency ✅

**Checklist:**

- [x] Replace np.diff with compute_velocity_from_derivative in detect_ground_contact
- [x] Ensure consistent velocity calculation throughout
- [x] Update tests for new velocity calculation
- [x] Verify no regression in contact detection

**Completed:** 2025-01-26

**Notes:**

- Updated `detect_ground_contact()` to use derivative-based velocity calculation
- Added `window_length` and `polyorder` parameters to `detect_ground_contact()`
- Updated CLI to pass smoothing parameters to contact detection
- All velocity calculations now use consistent Savitzky-Golay derivative method
- No test regressions - all 47 tests passing

**LLM Prompt:**

```text
Fix velocity calculation inconsistency in src/kinemotion/dropjump/analysis.py:

1. In detect_ground_contact() function (line 119), replace:
   velocities = np.diff(foot_positions, prepend=foot_positions[0])

   With:
   from ..core.smoothing import compute_velocity_from_derivative
   velocities = compute_velocity_from_derivative(
       foot_positions,
       window_length=5,  # Add as parameter
       polyorder=2       # Add as parameter
   )

2. Add window_length and polyorder as optional parameters to detect_ground_contact()

3. Update all calls to detect_ground_contact() to pass these parameters

4. Update docstring to explain the change from frame-to-frame to derivative-based

This ensures consistent smooth velocity calculation throughout the pipeline.
```text

**Files to modify:**

- src/kinemotion/dropjump/analysis.py
- src/kinemotion/dropjump/cli.py (pass parameters)

### 3.2 Validate or Remove Correction Factor ✅

**Checklist:**

- [x] Document the sources of error that necessitate correction
- [x] Make correction factor configurable parameter with default 1.0
- [x] Add comprehensive comment explaining the decision
- [x] Add CLI parameter for kinematic_correction_factor

**Completed:** 2025-01-26

**Notes:**

- Changed default correction factor from hardcoded 1.35 to configurable parameter with default 1.0
- Added `kinematic_correction_factor` parameter to `calculate_drop_jump_metrics()`
- Added `--kinematic-correction-factor` CLI option (default: 1.0)
- Enhanced documentation explaining why correction might be needed and that it's unvalidated
- Users can now experiment with correction factor values (e.g., 1.35) without code changes
- Default behavior (1.0) applies no correction, promoting transparency about unvalidated measurements

**LLM Prompt:**

```text
In src/kinemotion/dropjump/kinematics.py, address the correction factor issue:

1. At line 323-324, add a detailed comment block explaining:
   - Why a correction factor might be needed (theoretical reasons)
   - What errors it's compensating for (timing, CoM vs foot, etc.)
   - That this value is unvalidated and experimental

2. Make the correction factor a parameter:
   - Add kinematic_correction_factor parameter (default: 1.0)
   - Allow users to set via CLI if needed
   - Document that 1.35 was an experimental value

3. Add a warning in the code:
   "WARNING: Kinematic correction factor is experimental and unvalidated.
    Default is 1.0 (no correction). Historical testing suggested 1.35 but
    this lacks rigorous validation."

This maintains transparency while allowing experimentation.
```text

**Files to modify:**

- src/kinemotion/dropjump/kinematics.py
- src/kinemotion/dropjump/cli.py (add parameter)

---

## Phase 3 Summary

**Status:** ✅ COMPLETED (2025-01-26)

**Changes Made:**

1. Unified velocity calculation to use derivative-based method throughout
2. Updated `detect_ground_contact()` to use `compute_velocity_from_derivative()`
3. Added `window_length` and `polyorder` parameters to contact detection
4. Made kinematic correction factor configurable (default: 1.0, no correction)
5. Added `--kinematic-correction-factor` CLI option
6. Enhanced documentation explaining unvalidated correction factors

**Files Modified:**

- src/kinemotion/dropjump/analysis.py (detect_ground_contact function)
- src/kinemotion/dropjump/kinematics.py (calculate_drop_jump_metrics function)
- src/kinemotion/dropjump/cli.py (added CLI parameter and parameter passing)

**Testing:**

- ✅ All 47 tests passing
- ✅ Mypy type checking passes (100%)
- ✅ Ruff linting passes (100%)
- ✅ No regressions introduced

**Impact:**

- Consistent velocity calculation eliminates algorithmic inconsistencies
- Derivative-based velocity provides smoother, more accurate contact detection
- Configurable correction factor allows experimentation while maintaining transparency
- Default 1.0 correction factor promotes honest reporting of unvalidated measurements
- Users can still use experimental 1.35 factor if desired via CLI

---

## Phase 4: Documentation Updates (P2 - Days 6-7)

### 4.1 Update Feature Documentation ✅ COMPLETED

**Status:** ✅ COMPLETED (2025-01-26)

**Checklist:**

- [x] Document which features are actually available
- [x] Clarify why CoM and adaptive threshold are NOT exposed for drop jumps
- [x] Ensure documentation accurately reflects implementation decisions
- [x] PARAMETERS.md already documents available parameters correctly

**Completed:** 2025-01-26

**Notes:**
Documentation already accurately reflects that:

- `--use-com` and `--adaptive-threshold` are NOT available for `dropjump-analyze`
- These features exist in `core/` modules for future jump types
- Drop jump videos (~3 seconds) are too short for these features
- Clear explanation provided in CLAUDE.md (lines 424-437)

**No changes needed** - documentation was already correct and clear about design decisions.

**Files verified:**

- ✅ CLAUDE.md - Correctly documents that features are NOT exposed with reasoning
- ✅ docs/PARAMETERS.md - Only documents parameters actually available in CLI
- ✅ README.md - No false feature claims

### 4.2 Add Validation Roadmap ✅

**Status:** ✅ COMPLETED (2025-01-26)

**Checklist:**

- [x] Create VALIDATION_PLAN.md
- [x] Document what needs validation
- [x] Specify validation methodology
- [x] Set realistic timeline

**Completed:** 2025-01-26

**Notes:**

- Created practical validation plan for hobby project constraints
- **SIMPLIFIED** from research-grade ($17K-30K, 12 months) to hobby-appropriate ($0-500, 1-3 months)
- Focus on free validation methods: MyJump2 app comparison, manual video analysis, physics checks
- Optional low-cost methods: Jump mats ($200-500) or timing gates ($100-300)
- DIY validation protocol: Developer can self-validate with 10-20 jumps over 4 weeks
- Community validation approach: Invite users to contribute comparison data
- Simple statistics: Correlation and mean error (no complex Bland-Altman plots required)
- Realistic goal: "Practical accuracy" for coaching/training, NOT research-grade validation

**Files Created:**

- docs/VALIDATION_PLAN.md (practical 12-section hobby project validation guide)

**LLM Prompt:**

```text
Create docs/VALIDATION_PLAN.md with:

1. Validation objectives:
   - Compare against force plate measurements
   - Validate against 3D motion capture
   - Test across different jump types

2. Methodology:
   - Data collection protocol
   - Ground truth sources
   - Statistical analysis plan
   - Sample size calculations

3. Timeline:
   - Phase 1: Collect validation dataset
   - Phase 2: Run comparisons
   - Phase 3: Publish results

4. Current limitations acknowledgment

Make it clear this is a plan, not completed work.
```text

**Files to create:**

- docs/VALIDATION_PLAN.md

---

## Phase 5: Testing Improvements (P2 - Week 2)

### 5.1 Add Integration Tests

**Checklist:**

- [ ] Create test_cli_integration.py
- [ ] Test full pipeline with sample videos
- [ ] Test all parameter combinations
- [ ] Verify output format consistency

**LLM Prompt:**

```text
Create comprehensive CLI integration tests in tests/test_cli_integration.py:

1. Test basic analysis pipeline:
   - Create synthetic video or use test fixture
   - Run full analysis
   - Verify JSON output structure

2. Test parameter combinations:
   - Test each CLI parameter
   - Test CoM tracking when exposed
   - Test adaptive threshold when exposed

3. Test error handling:
   - Invalid video files
   - Missing files
   - Invalid parameter values

4. Test output generation:
   - JSON output to file
   - Debug video generation
   - Console output format

Use pytest fixtures and parameterized tests for efficiency.
```text

**Files to create:**

- tests/test_cli_integration.py
- tests/fixtures/ (test videos/data)

### 5.2 Add Regression Tests

**Checklist:**

- [ ] Create baseline measurements
- [ ] Test that fixes don't break existing functionality
- [ ] Monitor performance metrics
- [ ] Create test report

**LLM Prompt:**

```text
Create regression test suite in tests/test_regression.py:

1. Baseline tests:
   - Store expected outputs for known inputs
   - Verify outputs remain consistent after changes

2. Performance tests:
   - Measure processing time
   - Monitor memory usage
   - Alert on significant degradation

3. Accuracy consistency:
   - Even without validation, ensure consistency
   - Track metric stability across versions

4. Feature compatibility:
   - Ensure new features don't break old ones
   - Test backward compatibility

Include clear documentation on updating baselines when intentional changes occur.
```text

**Files to create:**

- tests/test_regression.py
- tests/baselines/ (reference data)

---

## Phase 6: Type Safety Improvements (P3 - Week 3)

### 6.1 Fix Type Annotations

**Checklist:**

- [ ] Remove unnecessary type: ignore comments
- [ ] Add proper return type annotations
- [ ] Fix numpy array type hints
- [ ] Run mypy in strict mode

**LLM Prompt:**

```text
Fix type safety issues throughout the codebase:

1. In src/kinemotion/core/smoothing.py:
   - Fix return type annotation at line 209
   - Ensure numpy arrays are properly typed
   - Remove type: ignore where possible

2. Add proper numpy type hints:
   - Use numpy.typing.NDArray where appropriate
   - Specify dtype where known

3. For each type: ignore:
   - Try to fix the underlying issue
   - If truly unfixable, add comment explaining why

4. Ensure all functions have complete signatures

Goal: Minimize type: ignore usage while maintaining strict type checking.
```text

**Files to modify:**

- src/kinemotion/core/smoothing.py
- src/kinemotion/dropjump/analysis.py
- Other files with type: ignore comments

---

## Phase 7: Validation Infrastructure (P3 - Week 4)

### 7.1 Create Validation Framework

**Checklist:**

- [ ] Design validation data structure
- [ ] Create ground truth comparison tools
- [ ] Build accuracy reporting system
- [ ] Document validation process

**LLM Prompt:**

```text
Create validation framework in src/kinemotion/validation/:

1. Create validation/compare.py:
   - Functions to compare against ground truth
   - Statistical analysis tools
   - Error metrics calculation

2. Create validation/report.py:
   - Generate validation reports
   - Create accuracy tables
   - Plot comparison graphs

3. Create validation/data.py:
   - Load ground truth data
   - Handle different formats (force plate, motion capture)
   - Data synchronization tools

4. Add CLI command 'kinemotion validate':
   - Run validation tests
   - Generate reports
   - Compare versions

This creates infrastructure even if we don't have validation data yet.
```text

**Files to create:**

- src/kinemotion/validation/**init**.py
- src/kinemotion/validation/compare.py
- src/kinemotion/validation/report.py
- src/kinemotion/validation/data.py

---

## Testing Strategy for Each Fix

### For Each Code Change

1. **Unit Test**: Test the specific function/feature
2. **Integration Test**: Test within the full pipeline
3. **Regression Test**: Ensure nothing else broke
4. **Documentation Test**: Verify docs match implementation

### Test Command Sequence

```bash
# After each change
uv run pytest tests/              # Unit tests
uv run pytest tests/test_cli_integration.py  # Integration
uv run pytest tests/test_regression.py       # Regression
uv run mypy src/kinemotion        # Type checking
uv run ruff check                 # Linting

# Final validation
uv run kinemotion dropjump-analyze sample.mp4 --use-com  # Manual test
```

---

## Success Criteria

### Phase 1 Complete When: ✅

- [x] No false accuracy claims in documentation
- [x] All file paths in documentation are correct
- [x] Clear disclaimers about validation status

### Phase 2 Complete When: ✅ RESOLVED - NOT APPLICABLE

- [x] CoM tracking intentionally NOT exposed (design decision documented)
- [x] Adaptive threshold intentionally NOT exposed (design decision documented)
- [x] Features available in core/ modules for future jump types
- [x] Rationale clearly documented in CLAUDE.md and IMPLEMENTATION_PLAN.md

### Phase 3 Complete When: ✅

- [x] Consistent velocity calculation throughout
- [x] Correction factor properly documented/parameterized
- [x] No algorithmic inconsistencies

### Phase 4 Complete When: ✅

- [x] Documentation matches implementation (4.1 complete)
- [x] All features accurately described (4.1 complete)
- [x] Validation plan documented (4.2 complete)

### Phase 5 Complete When

- [ ] Integration tests passing
- [ ] Regression tests established
- [ ] CI/CD pipeline updated

### Phase 6 Complete When

- [ ] Type safety improved
- [ ] Minimal type: ignore usage
- [ ] Clean mypy output

### Phase 7 Complete When

- [ ] Validation framework created
- [ ] Ready for validation data
- [ ] Comparison tools functional

---

## Rollback Plan

If any fix causes issues:

1. **Git Strategy**: Each phase in separate branch
2. **Feature Flags**: Add config to disable new features
3. **Version Tags**: Tag before each major change
4. **Rollback Procedure**:

   ```bash
   git checkout <previous-tag>
   uv sync
   uv run pytest  # Verify working state
   ```

---

## Communication Plan

### For Users

1. Add CHANGELOG.md documenting all fixes
2. Update README with "Recent Improvements" section
3. Be transparent about validation status

### For Contributors

1. Update CONTRIBUTING.md with new standards
2. Document architecture decisions
3. Explain why changes were made

---

## Long-term Improvements

After all fixes are complete:

1. **Establish Validation Dataset**
   - Partner with biomechanics lab
   - Collect force plate data
   - Create public benchmark

2. **Continuous Documentation**
   - Automated doc testing
   - Documentation from code
   - Version-locked examples

3. **Architecture Redesign**
   - Better plugin architecture
   - Clear feature pipeline
   - Modular CLI design

4. **Community Building**
   - Seek academic validation
   - Create user forum
   - Publish methodology paper

---

## Notes for Implementation

- **Start with P0**: These affect credibility most
- **Test continuously**: Don't wait until end
- **Document as you go**: Update docs with each fix
- **Communicate changes**: Be transparent about what changed and why
- **Preserve working features**: Don't break what works
- **Use version control**: Commit frequently with clear messages

This plan provides a systematic approach to fixing all identified issues while maintaining code quality and user trust.
