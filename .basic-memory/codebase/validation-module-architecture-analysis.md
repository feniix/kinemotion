---
title: Validation Module Architecture Analysis
type: note
permalink: codebase/validation-module-architecture-analysis-1
---

# Validation Module Architecture Analysis

## Current State: Validators in core/

The validation modules are currently located in `core/` but with jump-type prefixes:
- `core/cmj_metrics_validator.py` + `core/cmj_validation_bounds.py`
- `core/dropjump_metrics_validator.py` + `core/dropjump_validation_bounds.py`

This is **architecturally inconsistent** with other `core/` modules which are truly shared without type prefixes (pose.py, video_io.py, smoothing.py, filtering.py).

## Why They're in core/ (Historical Context)

1. **Recognized shared patterns** - Someone identified that CMJ and drop jump validation have identical structures
2. **Incomplete refactoring** - Placed in core/ as first step, but never extracted base classes
3. **Not documented** - CLAUDE.md line 88 lists core/ contents as "pose, smoothing, filtering, auto_tuning, video_io" - validators NOT mentioned
4. **Naming inconsistency** - Jump-type prefixes (cmj_*, dropjump_*) signal these are NOT shared abstractions

## Shared Components (Common to Both)

### 100% Identical Code (~110+ lines):

1. **ValidationSeverity enum** (7 lines)
   - ERROR, WARNING, INFO severity levels

2. **ValidationIssue dataclass** (7 lines)
   - severity, metric, message, value, bounds fields

3. **ValidationResult methods** (~45 lines)
   - `add_error()` - identical implementation
   - `add_warning()` - identical implementation
   - `add_info()` - identical implementation
   - `finalize_status()` - identical logic (ERROR → FAIL, WARNING → PASS_WITH_WARNINGS, none → PASS)
   - `to_dict()` - similar structure with jump-specific fields

4. **AthleteProfile enum** (8 lines)
   - ELDERLY, UNTRAINED, RECREATIONAL, TRAINED, ELITE

5. **MetricBounds dataclass** (22 lines)
   - Structure: absolute_min, practical_min, recreational_min/max, elite_min/max, absolute_max, unit
   - `contains(value, profile)` method - identical logic
   - `is_physically_possible(value)` method - identical logic

### Shared Patterns (~85% similar):

6. **Validator initialization**
   - Both take optional `assumed_profile: AthleteProfile | None`
   - Both store profile or estimate from metrics

7. **Validation flow structure**
   - Estimate athlete profile if not provided
   - Check individual metric bounds
   - Perform cross-validation checks
   - Finalize status

8. **Profile estimation**
   - Both have `estimate_athlete_profile(metrics)` functions
   - Logic structure similar (jump height primary classifier)
   - Implementation differs slightly based on available metrics

## Code Duplication Impact

**Estimated duplication:** ~100-120 lines across 4 files
**Project standard:** < 3% duplication
**Status:** ⚠️ Violates duplication target

## Correct Architecture (Proposed)

### Step 1: Extract Base Classes to `core/validation.py`

```python
# core/validation.py - Shared validation infrastructure

from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod


class ValidationSeverity(Enum):
    """Severity level for validation issues."""
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


class AthleteProfile(Enum):
    """Athlete performance categories."""
    ELDERLY = "elderly"
    UNTRAINED = "untrained"
    RECREATIONAL = "recreational"
    TRAINED = "trained"
    ELITE = "elite"


@dataclass
class ValidationIssue:
    """Single validation issue."""
    severity: ValidationSeverity
    metric: str
    message: str
    value: float | None = None
    bounds: tuple[float, float] | None = None


@dataclass
class MetricBounds:
    """Physiological bounds for a metric."""
    absolute_min: float
    practical_min: float
    recreational_min: float
    recreational_max: float
    elite_min: float
    elite_max: float
    absolute_max: float
    unit: str

    def contains(self, value: float, profile: AthleteProfile) -> bool:
        """Check if value within bounds for profile."""
        # ... (existing logic)

    def is_physically_possible(self, value: float) -> bool:
        """Check if value within absolute limits."""
        return self.absolute_min <= value <= self.absolute_max


@dataclass
class ValidationResult:
    """Base validation result."""
    issues: list[ValidationIssue] = field(default_factory=list)
    status: str = "PASS"
    athlete_profile: AthleteProfile | None = None

    def add_error(self, metric: str, message: str,
                  value: float | None = None,
                  bounds: tuple[float, float] | None = None) -> None:
        """Add error-level issue."""
        # ... (existing implementation)

    def add_warning(self, ...) -> None:
        """Add warning-level issue."""
        # ... (existing implementation)

    def add_info(self, ...) -> None:
        """Add info-level issue."""
        # ... (existing implementation)

    def finalize_status(self) -> None:
        """Determine final status."""
        # ... (existing logic)

    @abstractmethod
    def to_dict(self) -> dict:
        """Convert to JSON-serializable dict."""
        pass


class MetricsValidator(ABC):
    """Base validator for jump metrics."""

    def __init__(self, assumed_profile: AthleteProfile | None = None):
        self.assumed_profile = assumed_profile

    @abstractmethod
    def validate(self, metrics: dict) -> ValidationResult:
        """Validate metrics comprehensively."""
        pass
```

### Step 2: Move Jump-Specific Implementations

**Move to:**
- `cmj/metrics_validator.py` - CMJMetricsValidator extends MetricsValidator
- `cmj/validation_bounds.py` - CMJBounds, TripleExtensionBounds, RSIBounds
- `dropjump/metrics_validator.py` - DropJumpMetricsValidator extends MetricsValidator
- `dropjump/validation_bounds.py` - DropJumpBounds

**Benefits:**
- ✅ Achieve < 3% duplication target
- ✅ Clear separation: core/ = shared, jump folders = specific
- ✅ Consistent naming (no jump-type prefixes in core/)
- ✅ Easier to add new jump types (extend base classes)
- ✅ Single source of truth for validation patterns

## References

- CLAUDE.md line 88: core/ documented as "pose, smoothing, filtering, auto_tuning, video_io"
- Code duplication standard: < 3% (docs/development/testing.md)
- Current usage: api.py imports from core/, tests import from core/
