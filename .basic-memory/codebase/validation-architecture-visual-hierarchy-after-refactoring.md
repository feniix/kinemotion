---
title: Validation Architecture - Visual Hierarchy After Refactoring
type: note
permalink: codebase/validation-architecture-visual-hierarchy-after-refactoring-1
---

# Validation Architecture - After Refactoring

## Class Hierarchy

```
┌─────────────────────────────────────────────────────────────┐
│           core/validation.py (SHARED BASE CLASSES)          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─ ValidationSeverity (enum)                              │
│  │    └─ ERROR, WARNING, INFO                              │
│  │                                                          │
│  ├─ ValidationIssue (dataclass)                            │
│  │    └─ severity, metric, message, value, bounds          │
│  │                                                          │
│  ├─ AthleteProfile (enum)                                 │
│  │    └─ ELDERLY, UNTRAINED, RECREATIONAL, TRAINED, ELITE │
│  │                                                          │
│  ├─ MetricBounds (dataclass)                              │
│  │    ├─ absolute/practical/recreational/elite ranges     │
│  │    ├─ contains(value, profile) → bool                  │
│  │    └─ is_physically_possible(value) → bool             │
│  │                                                          │
│  ├─ ValidationResult (dataclass + ABC)                    │
│  │    ├─ issues, status, athlete_profile                 │
│  │    ├─ add_error(metric, message, value, bounds)        │
│  │    ├─ add_warning(metric, message, value, bounds)      │
│  │    ├─ add_info(metric, message, value)                 │
│  │    ├─ finalize_status() → determines PASS/WARNING/FAIL │
│  │    └─ to_dict() → abstract (subclass implements)       │
│  │                                                          │
│  └─ MetricsValidator (ABC)                               │
│       ├─ __init__(assumed_profile)                        │
│       └─ validate(metrics) → abstract                     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
              ▲                              ▲
              │                              │
    ┌─────────┴────────┐            ┌───────┴────────┐
    │                  │            │                │

┌────────────────────────┐    ┌──────────────────────────┐
│   cmj/ (CMJ-specific)  │    │  dropjump/ (DJ-specific) │
├────────────────────────┤    ├──────────────────────────┤
│                        │    │                          │
│ metrics_validator.py:  │    │ metrics_validator.py:    │
│ ┌────────────────────┐ │    │ ┌──────────────────────┐ │
│ │ CMJMetricsValidator│ │    │ │DropJumpMetricsVali- │ │
│ │ (extends Metrics-  │ │    │ │ dator (extends       │ │
│ │  Validator)        │ │    │ │ MetricsValidator)    │ │
│ │                    │ │    │ │                      │ │
│ │ CMJValidationResult│ │    │ │ DropJumpValidation-  │ │
│ │ (extends Validation│ │    │ │ Result (extends      │ │
│ │  Result)           │ │    │ │ ValidationResult)    │ │
│ └────────────────────┘ │    │ └──────────────────────┘ │
│                        │    │                          │
│ validation_bounds.py:  │    │ validation_bounds.py:   │
│ ┌────────────────────┐ │    │ ┌──────────────────────┐ │
│ │ CMJBounds          │ │    │ │ DropJumpBounds       │ │
│ │  └─ FLIGHT_TIME    │ │    │ │  └─ CONTACT_TIME     │ │
│ │  └─ JUMP_HEIGHT    │ │    │ │  └─ FLIGHT_TIME      │ │
│ │  └─ ...            │ │    │ │  └─ JUMP_HEIGHT      │ │
│ │                    │ │    │ │  └─ RSI              │ │
│ │ TripleExtension-   │ │    │ │                      │ │
│ │ Bounds (hip/knee/  │ │    │ │ estimate_athlete_    │ │
│ │  ankle angles)     │ │    │ │ profile()            │ │
│ │                    │ │    │ │                      │ │
│ │ RSIBounds (CMJ-    │ │    │ └──────────────────────┘ │
│ │ specific RSI ranges)│ │    │                          │
│ │                    │ │    │                          │
│ │ MetricConsistency  │ │    │                          │
│ │ (cross-validation  │ │    │                          │
│ │  tolerances)       │ │    │                          │
│ │                    │ │    │                          │
│ │ estimate_athlete_  │ │    │                          │
│ │ profile()          │ │    │                          │
│ └────────────────────┘ │    │                          │
│                        │    │                          │
└────────────────────────┘    └──────────────────────────┘
```

## Data Flow Example

### CMJ Validation Flow
```
metrics_dict (CMJ data)
    │
    ▼
api.py or test imports CMJMetricsValidator()
    │
    ▼
validator.validate(metrics_dict)
    │
    ├─ Estimate profile from jump_height
    │
    ├─ Check individual bounds (flight_time, jump_height, etc.)
    │   └─ Each uses MetricBounds.contains(value, profile)
    │
    ├─ Cross-validation checks
    │   └─ Uses MetricConsistency tolerances
    │
    └─ Finalize status
        └─ Calls ValidationResult.finalize_status()
    │
    ▼
CMJValidationResult
    ├─ status: "PASS" / "PASS_WITH_WARNINGS" / "FAIL"
    ├─ issues: list[ValidationIssue]
    ├─ athlete_profile: AthleteProfile
    ├─ rsi: float
    ├─ height_flight_time_consistency: float
    └─ [CMJ-specific fields]
    │
    ▼
result.to_dict() → JSON-serializable dictionary
```

## Import Structure After Refactoring

### Old (Duplicated)
```python
# api.py
from .core.cmj_metrics_validator import CMJMetricsValidator
from .core.dropjump_metrics_validator import DropJumpMetricsValidator

# tests/test_cmj_physiological_bounds.py
from kinemotion.core.cmj_metrics_validator import CMJMetricsValidator
from kinemotion.core.cmj_validation_bounds import CMJBounds, AthleteProfile
```

### New (Refactored)
```python
# api.py
from .cmj.metrics_validator import CMJMetricsValidator
from .dropjump.metrics_validator import DropJumpMetricsValidator

# tests/test_cmj_physiological_bounds.py
from kinemotion.cmj.metrics_validator import CMJMetricsValidator
from kinemotion.cmj.validation_bounds import CMJBounds
from kinemotion.core.validation import AthleteProfile, ValidationSeverity
```

## Key Improvements

| Aspect | Before | After |
|--------|--------|-------|
| Shared code location | core/ with jump prefixes | core/validation.py (no prefixes) |
| CMJ validator location | core/cmj_metrics_validator.py | cmj/metrics_validator.py |
| Drop jump validator location | core/dropjump_metrics_validator.py | dropjump/metrics_validator.py |
| Code duplication | 137 lines (7.7%) | ~10 lines (< 1%) |
| Base class definition | None (duplicated) | core/validation.py (single source) |
| AthleteProfile enum copies | 2 (CMJ + drop jump) | 1 (shared in core/validation.py) |
| MetricBounds class copies | 2 (CMJ + drop jump) | 1 (shared in core/validation.py) |
| Validator coupling | Tight (no inheritance) | Loose (via inheritance) |
| Extensibility | Requires copying all code | Extend base classes |
| Maintenance effort | 2x (update both files) | 1x (fix base class) |

## Co-location Benefits

All validation code now co-located with its jump type:
```
cmj/
  ├── analysis.py              ← CMJ analysis algorithms
  ├── kinematics.py            ← CMJ metrics calculation
  ├── metrics_validator.py     ← ✨ NEW: CMJ validation
  ├── validation_bounds.py     ← ✨ NEW: CMJ bounds
  └── joint_angles.py          ← CMJ-specific angles

dropjump/
  ├── analysis.py              ← Drop jump algorithms
  ├── kinematics.py            ← Drop jump metrics
  ├── metrics_validator.py     ← ✨ NEW: Drop jump validation
  └── validation_bounds.py     ← ✨ NEW: Drop jump bounds
```

This makes it easier to:
1. **Understand the jump type** - All related code in one folder
2. **Add new jump types** - Copy the pattern from an existing type
3. **Modify jump-specific logic** - Find everything you need in one place
4. **Maintain shared infrastructure** - core/validation.py is the single source

## Next Jump Type Example

To add a new jump type (e.g., Standing Jump):
```
1. Create standingjump/ folder
2. Copy structure from cmj/ or dropjump/
3. Create standingjump/metrics_validator.py
   └─ Extend MetricsValidator from core/validation.py
4. Create standingjump/validation_bounds.py
   └─ Define StandingJumpBounds, estimate_athlete_profile()
5. Update api.py imports
6. All base classes already available in core/validation.py ✅
```

No more code duplication needed!
