---
title: Validation Code Duplication Evidence
type: note
permalink: codebase/validation-code-duplication-evidence-1
---

# Validation Code Duplication Evidence

## Side-by-Side Comparison of Duplicated Code

### 1. ValidationSeverity Enum (100% Identical)

**CMJ Validator (lines 24-30):**
```python
class ValidationSeverity(Enum):
    """Severity level for validation issues."""
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"
```

**Drop Jump Validator (lines 20-26):**
```python
class ValidationSeverity(Enum):
    """Severity level for validation issues."""
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"
```

**Duplication:** 7 lines, 100% identical

---

### 2. ValidationIssue Dataclass (100% Identical)

**CMJ Validator (lines 32-41):**
```python
@dataclass
class ValidationIssue:
    """Single validation issue."""
    severity: ValidationSeverity
    metric: str
    message: str
    value: float | None = None
    bounds: tuple[float, float] | None = None
```

**Drop Jump Validator (lines 28-37):**
```python
@dataclass
class ValidationIssue:
    """Single validation issue."""
    severity: ValidationSeverity
    metric: str
    message: str
    value: float | None = None
    bounds: tuple[float, float] | None = None
```

**Duplication:** 10 lines, 100% identical

---

### 3. ValidationResult Methods (100% Identical)

**add_error() - CMJ (lines 56-72) vs Drop Jump (lines 50-66):**
```python
def add_error(
    self,
    metric: str,
    message: str,
    value: float | None = None,
    bounds: tuple[float, float] | None = None,
) -> None:
    """Add error-level issue."""
    self.issues.append(
        ValidationIssue(
            severity=ValidationSeverity.ERROR,
            metric=metric,
            message=message,
            value=value,
            bounds=bounds,
        )
    )
```

**Duplication:** 17 lines × 3 methods (add_error, add_warning, add_info) = 51 lines

---

**finalize_status() - CMJ (lines 108-122) vs Drop Jump (lines 102-116):**
```python
def finalize_status(self) -> None:
    """Determine final pass/fail status based on issues."""
    has_errors = any(
        issue.severity == ValidationSeverity.ERROR for issue in self.issues
    )
    has_warnings = any(
        issue.severity == ValidationSeverity.WARNING for issue in self.issues
    )

    if has_errors:
        self.status = "FAIL"
    elif has_warnings:
        self.status = "PASS_WITH_WARNINGS"
    else:
        self.status = "PASS"
```

**Duplication:** 15 lines, 100% identical

---

### 4. AthleteProfile Enum (100% Identical)

**CMJ Bounds (lines 22-30):**
```python
class AthleteProfile(Enum):
    """Athlete performance categories for metric bounds."""
    ELDERLY = "elderly"
    UNTRAINED = "untrained"
    RECREATIONAL = "recreational"
    TRAINED = "trained"
    ELITE = "elite"
```

**Drop Jump Bounds (lines 22-30):**
```python
class AthleteProfile(Enum):
    """Athlete performance categories for metric bounds."""
    ELDERLY = "elderly"
    UNTRAINED = "untrained"
    RECREATIONAL = "recreational"
    TRAINED = "trained"
    ELITE = "elite"
```

**Duplication:** 9 lines, 100% identical

---

### 5. MetricBounds Dataclass (100% Identical)

**CMJ Bounds (lines 32-76):**
```python
@dataclass
class MetricBounds:
    """Physiological bounds for a single metric."""
    absolute_min: float
    practical_min: float
    recreational_min: float
    recreational_max: float
    elite_min: float
    elite_max: float
    absolute_max: float
    unit: str

    def contains(self, value: float, profile: AthleteProfile) -> bool:
        """Check if value is within bounds for athlete profile."""
        if profile == AthleteProfile.ELDERLY:
            return self.practical_min <= value <= self.recreational_max
        elif profile == AthleteProfile.UNTRAINED:
            return self.practical_min <= value <= self.recreational_max
        elif profile == AthleteProfile.RECREATIONAL:
            return self.recreational_min <= value <= self.recreational_max
        elif profile == AthleteProfile.TRAINED:
            trained_min = (self.recreational_min + self.elite_min) / 2
            trained_max = (self.recreational_max + self.elite_max) / 2
            return trained_min <= value <= trained_max
        elif profile == AthleteProfile.ELITE:
            return self.elite_min <= value <= self.elite_max
        return False

    def is_physically_possible(self, value: float) -> bool:
        """Check if value is within absolute physiological limits."""
        return self.absolute_min <= value <= self.absolute_max
```

**Drop Jump Bounds (lines 32-76):**
```python
@dataclass
class MetricBounds:
    """Physiological bounds for a single metric."""
    absolute_min: float
    practical_min: float
    recreational_min: float
    recreational_max: float
    elite_min: float
    elite_max: float
    absolute_max: float
    unit: str

    def contains(self, value: float, profile: AthleteProfile) -> bool:
        """Check if value is within bounds for athlete profile."""
        if profile == AthleteProfile.ELDERLY:
            return self.practical_min <= value <= self.recreational_max
        elif profile == AthleteProfile.UNTRAINED:
            return self.practical_min <= value <= self.recreational_max
        elif profile == AthleteProfile.RECREATIONAL:
            return self.recreational_min <= value <= self.recreational_max
        elif profile == AthleteProfile.TRAINED:
            trained_min = (self.recreational_min + self.elite_min) / 2
            trained_max = (self.recreational_max + self.elite_max) / 2
            return trained_min <= value <= trained_max
        elif profile == AthleteProfile.ELITE:
            return self.elite_min <= value <= self.elite_max
        return False

    def is_physically_possible(self, value: float) -> bool:
        """Check if value is within absolute physiological limits."""
        return self.absolute_min <= value <= self.absolute_max
```

**Duplication:** 45 lines, 100% identical

---

## Duplication Summary

| Component | Lines | Duplication % | Status |
|-----------|-------|---------------|--------|
| ValidationSeverity | 7 | 100% | \u274c Duplicate |
| ValidationIssue | 10 | 100% | \u274c Duplicate |
| ValidationResult.add_error() | 17 | 100% | \u274c Duplicate |
| ValidationResult.add_warning() | 17 | 100% | \u274c Duplicate |
| ValidationResult.add_info() | 17 | 100% | \u274c Duplicate |
| ValidationResult.finalize_status() | 15 | 100% | \u274c Duplicate |
| AthleteProfile | 9 | 100% | \u274c Duplicate |
| MetricBounds (full class) | 45 | 100% | \u274c Duplicate |

**Total Duplication:** ~137 lines of identical code across 4 files

**File sizes:**
- cmj_metrics_validator.py: 831 lines
- cmj_validation_bounds.py: 395 lines
- dropjump_metrics_validator.py: 347 lines
- dropjump_validation_bounds.py: 197 lines
- **Combined:** 1,770 lines

**Duplication percentage:** 137 / 1770 = **7.7% duplication**

**Project standard:** < 3%
**Status:** \u26a0\ufe0f **Violates quality standard by 2.6x**

## Impact

1. **Maintenance burden:** Bug fixes must be applied twice
2. **Inconsistency risk:** Changes to one validator may not propagate to the other
3. **Extensibility:** Adding new jump types requires copying all base code again
4. **Code smell:** Indicates architectural debt that should be refactored

## Resolution Path

Extract shared abstractions to `core/validation.py` as base classes, then:
- CMJMetricsValidator extends base in `cmj/metrics_validator.py`
- DropJumpMetricsValidator extends base in `dropjump/metrics_validator.py`
- Estimated duplication after refactor: < 1% (only jump-specific validation logic remains)
