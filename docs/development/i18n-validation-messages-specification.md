# i18n Validation Messages - Technical Specification

## Overview

This document defines the implementation of internationalization (i18n) support for validation messages in the Kinemotion backend. We use **Option B: Structured Data + Frontend Translation** to keep the backend simple and maintainable.

## Architecture Decision

### Option A vs Option B

| Criterion                  | Option A: Backend Translation                             | Option B: Structured Data              |
| -------------------------- | --------------------------------------------------------- | -------------------------------------- |
| **Backend Responsibility** | Translation logic, message formatting, language detection | Validation logic only, structured data |
| **API Contract**           | Changes per language                                      | Language-independent                   |
| **Translation Updates**    | Requires backend redeploy                                 | Frontend-only updates                  |
| **Scalability**            | Backend becomes bottleneck                                | Scales independently                   |
| **Team Workflow**          | Backend team owns translations                            | Localization team owns i18n files      |
| **Testing Complexity**     | Higher (test each language)                               | Lower (test structure only)            |
| **REST Philosophy**        | ❌ Violates separation of concerns                        | ✅ Data layer + Presentation layer     |

**Selected: Option B** - Simplicity, scalability, and adherence to REST best practices.

## Data Model Changes

### Current ValidationIssue

```python
@dataclass
class ValidationIssue:
    severity: ValidationSeverity
    metric: str
    message: str                                    # Formatted message
    value: float | None = None
    bounds: tuple[float, float] | None = None
```

### New ValidationIssue (with i18n support)

```python
@dataclass
class ValidationIssue:
    severity: ValidationSeverity
    metric: str
    message: str                                    # KEPT: backward compatibility
    message_key: str | None = None                 # NEW: i18n translation key
    context: dict[str, Any] | None = None          # NEW: context for template variables
    value: float | None = None
    bounds: tuple[float, float] | None = None
```

### Message Key Format

**Pattern**: `validation.[domain].[metric].[condition]`

**Levels**:

1. `[domain]` - Always `validation` (for future expansion: e.g., `analysis`, `tracking`)
1. `[metric]` - Metric name: `flight_time`, `jump_height`, `rsi`, `triple_extension`, etc.
1. `[condition]` - Severity/reason: `within_range`, `outside_range`, `below_minimum`, `above_maximum`, `invalid_calculation`

### Examples

#### Flight Time Messages

```
validation.flight_time.within_range
validation.flight_time.outside_range
validation.flight_time.below_minimum
validation.flight_time.above_maximum
```

#### Jump Height Messages

```
validation.jump_height.within_range
validation.jump_height.outside_range
validation.jump_height.no_jump
validation.jump_height.above_maximum
```

#### RSI Messages

```
validation.rsi.valid
validation.rsi.invalid_calculation
validation.rsi.outlier
```

#### Triple Extension Messages

```
validation.triple_extension.normal
validation.triple_extension.insufficient
validation.triple_extension.compensatory_pattern
```

## Backend Implementation

### Step 1: Update ValidationResult Methods

**File**: `src/kinemotion/core/validation.py`

```python
def add_error(
    self,
    metric: str,
    message: str,
    value: float | None = None,
    bounds: tuple[float, float] | None = None,
    message_key: str | None = None,           # NEW
    context: dict[str, Any] | None = None,    # NEW
) -> None:
    """Add error-level issue with optional i18n support.

    Args:
        metric: Metric name (e.g., 'flight_time')
        message: Human-readable message (kept for backward compatibility)
        value: Measured value
        bounds: (min, max) tuple for absolute bounds
        message_key: i18n translation key (e.g., 'validation.flight_time.below_minimum')
        context: Dict with context for template variables (e.g., {'unit': 's', 'profile': 'elite'})
    """
    self.issues.append(
        ValidationIssue(
            severity=ValidationSeverity.ERROR,
            metric=metric,
            message=message,
            message_key=message_key,
            context=context,
            value=value,
            bounds=bounds,
        )
    )

def add_warning(
    self,
    metric: str,
    message: str,
    value: float | None = None,
    bounds: tuple[float, float] | None = None,
    message_key: str | None = None,
    context: dict[str, Any] | None = None,
) -> None:
    """Add warning-level issue with optional i18n support."""
    self.issues.append(
        ValidationIssue(
            severity=ValidationSeverity.WARNING,
            metric=metric,
            message=message,
            message_key=message_key,
            context=context,
            value=value,
            bounds=bounds,
        )
    )

def add_info(
    self,
    metric: str,
    message: str,
    value: float | None = None,
    message_key: str | None = None,           # NEW
    context: dict[str, Any] | None = None,    # NEW
) -> None:
    """Add info-level issue with optional i18n support."""
    self.issues.append(
        ValidationIssue(
            severity=ValidationSeverity.INFO,
            metric=metric,
            message=message,
            message_key=message_key,
            context=context,
            value=value,
        )
    )
```

### Step 2: Update CMJ Validator

**File**: `src/kinemotion/cmj/metrics_validator.py`

#### Example: Flight Time Validation

```python
def _check_flight_time(
    self, metrics: dict, result: CMJValidationResult, profile: AthleteProfile
) -> None:
    """Validate flight time."""
    flight_time_raw = self._get_metric_value(
        metrics, "flight_time_ms", "flight_time"
    )
    if flight_time_raw is None:
        return

    # Convert to seconds if needed
    if flight_time_raw < 10:
        flight_time = flight_time_raw
    else:
        flight_time = flight_time_raw / 1000.0

    bounds = CMJBounds.FLIGHT_TIME

    if not bounds.is_physically_possible(flight_time):
        if flight_time < bounds.absolute_min:
            result.add_error(
                "flight_time",
                f"Flight time {flight_time:.3f}s below frame rate resolution limit",
                value=flight_time,
                bounds=(bounds.absolute_min, bounds.absolute_max),
                message_key="validation.flight_time.below_minimum",  # NEW
                context={"unit": bounds.unit},                        # NEW
            )
        else:
            result.add_error(
                "flight_time",
                f"Flight time {flight_time:.3f}s exceeds elite human capability",
                value=flight_time,
                bounds=(bounds.absolute_min, bounds.absolute_max),
                message_key="validation.flight_time.above_maximum",   # NEW
                context={"unit": bounds.unit},                        # NEW
            )
    elif bounds.contains(flight_time, profile):
        result.add_info(
            "flight_time",
            f"Flight time {flight_time:.3f}s within expected range for {profile.value}",
            value=flight_time,
            message_key="validation.flight_time.within_range",        # NEW
            context={
                "profile": profile.value,
                "unit": bounds.unit,
            },                                                         # NEW
        )
    else:
        # Outside expected range but physically possible
        expected_min, expected_max = self._get_profile_range(profile, bounds)
        result.add_warning(
            "flight_time",
            f"Flight time {flight_time:.3f}s outside typical range "
            f"[{expected_min:.3f}-{expected_max:.3f}]s for {profile.value}",
            value=flight_time,
            bounds=(expected_min, expected_max),
            message_key="validation.flight_time.outside_range",       # NEW
            context={
                "profile": profile.value,
                "unit": bounds.unit,
                "min": expected_min,
                "max": expected_max,
            },                                                         # NEW
        )
```

#### Example: Jump Height Validation

```python
def _check_jump_height(
    self, metrics: dict, result: CMJValidationResult, profile: AthleteProfile
) -> None:
    """Validate jump height."""
    jump_height = self._get_metric_value(metrics, "jump_height_m", "jump_height")
    if jump_height is None:
        return

    bounds = CMJBounds.JUMP_HEIGHT

    if not bounds.is_physically_possible(jump_height):
        if jump_height < bounds.absolute_min:
            result.add_error(
                "jump_height",
                f"Jump height {jump_height:.3f}m essentially no jump (noise)",
                value=jump_height,
                bounds=(bounds.absolute_min, bounds.absolute_max),
                message_key="validation.jump_height.no_jump",         # NEW
                context={"unit": bounds.unit},                        # NEW
            )
        else:
            result.add_error(
                "jump_height",
                f"Jump height {jump_height:.3f}m exceeds human capability",
                value=jump_height,
                bounds=(bounds.absolute_min, bounds.absolute_max),
                message_key="validation.jump_height.above_maximum",   # NEW
                context={"unit": bounds.unit},                        # NEW
            )
    elif bounds.contains(jump_height, profile):
        result.add_info(
            "jump_height",
            f"Jump height {jump_height:.3f}m within expected range for {profile.value}",
            value=jump_height,
            message_key="validation.jump_height.within_range",        # NEW
            context={
                "profile": profile.value,
                "unit": bounds.unit,
            },                                                         # NEW
        )
    else:
        expected_min, expected_max = self._get_profile_range(profile, bounds)
        result.add_warning(
            "jump_height",
            f"Jump height {jump_height:.3f}m outside typical range "
            f"[{expected_min:.3f}-{expected_max:.3f}]m for {profile.value}",
            value=jump_height,
            bounds=(expected_min, expected_max),
            message_key="validation.jump_height.outside_range",       # NEW
            context={
                "profile": profile.value,
                "unit": bounds.unit,
                "min": expected_min,
                "max": expected_max,
            },                                                         # NEW
        )
```

### Step 3: Update Serialization

**File**: `src/kinemotion/cmj/metrics_validator.py` (and similar for drop jump)

```python
class CMJValidationResult(ValidationResult):
    """CMJ-specific validation result."""

    rsi: float | None = None
    height_flight_time_consistency: float | None = None
    velocity_height_consistency: float | None = None
    depth_height_ratio: float | None = None
    contact_depth_ratio: float | None = None

    def to_dict(self) -> dict:
        """Convert validation result to JSON-serializable dictionary."""
        return {
            "status": self.status,
            "issues": [
                {
                    "severity": issue.severity.value,
                    "metric": issue.metric,
                    "message": issue.message,
                    "message_key": issue.message_key,                  # NEW
                    "context": issue.context,                          # NEW
                    "value": issue.value,
                    "bounds": issue.bounds,
                }
                for issue in self.issues
            ],
            "athlete_profile": (
                self.athlete_profile.value if self.athlete_profile else None
            ),
            "rsi": self.rsi,
            "height_flight_time_consistency_percent": (
                self.height_flight_time_consistency
            ),
            "velocity_height_consistency_percent": self.velocity_height_consistency,
            "depth_height_ratio": self.depth_height_ratio,
            "contact_depth_ratio": self.contact_depth_ratio,
        }
```

## Frontend Implementation

### Step 1: Translation Files

**Directory Structure**:

```
frontend/public/locales/
├── en.json
├── es.json
├── fr.json
├── de.json
└── ja.json
```

**File**: `frontend/public/locales/en.json`

```json
{
  "validation": {
    "flight_time": {
      "within_range": "Flight time {{value}}{{unit}} within expected range for {{profile}}",
      "outside_range": "Flight time {{value}}{{unit}} outside typical range [{{min}}-{{max}}]{{unit}} for {{profile}}",
      "below_minimum": "Flight time {{value}}{{unit}} below frame rate resolution limit",
      "above_maximum": "Flight time {{value}}{{unit}} exceeds elite human capability"
    },
    "jump_height": {
      "within_range": "Jump height {{value}}{{unit}} within expected range for {{profile}}",
      "outside_range": "Jump height {{value}}{{unit}} outside typical range [{{min}}-{{max}}]{{unit}} for {{profile}}",
      "no_jump": "Jump height {{value}}{{unit}} essentially no jump (noise)",
      "above_maximum": "Jump height {{value}}{{unit}} exceeds human capability"
    },
    "countermovement_depth": {
      "within_range": "Countermovement depth {{value}}{{unit}} within expected range for {{profile}}",
      "outside_range": "Countermovement depth {{value}}{{unit}} outside typical range for {{profile}}",
      "insufficient": "Countermovement depth {{value}}{{unit}} insufficient for {{profile}}"
    },
    "rsi": {
      "valid": "Reactive Strength Index {{value}} typical for {{profile}}",
      "outlier": "RSI {{value}} significantly higher than typical for {{profile}}",
      "invalid_calculation": "RSI calculation invalid: missing contact or flight time"
    },
    "triple_extension": {
      "normal": "Triple extension pattern normal for {{profile}}",
      "insufficient": "Triple extension pattern insufficient - limited ankle contribution",
      "compensatory": "Compensatory pattern detected - excessive knee extension"
    },
    "consistency": {
      "height_flight_time": "Height-flight time relationship within {{tolerance}}% error",
      "height_velocity": "Height-velocity relationship within {{tolerance}}% error",
      "contact_depth": "Contact time-depth ratio typical for {{profile}}"
    },
    "athlete_profile": {
      "detected": "Athlete profile detected as {{profile}}"
    }
  }
}
```

**File**: `frontend/public/locales/es.json`

```json
{
  "validation": {
    "flight_time": {
      "within_range": "Tiempo de vuelo {{value}}{{unit}} dentro del rango esperado para {{profile}}",
      "outside_range": "Tiempo de vuelo {{value}}{{unit}} fuera del rango típico [{{min}}-{{max}}]{{unit}} para {{profile}}",
      "below_minimum": "Tiempo de vuelo {{value}}{{unit}} por debajo del límite de resolución",
      "above_maximum": "Tiempo de vuelo {{value}}{{unit}} excede la capacidad humana"
    }
  }
}
```

### Step 2: React Component

**File**: `frontend/src/components/ValidationIssue.tsx`

```typescript
import { useTranslation } from 'i18next';

interface ValidationIssueData {
  severity: 'error' | 'warning' | 'info';
  metric: string;
  message: string;                    // Fallback for old API versions
  message_key?: string;               // NEW: i18n key
  context?: Record<string, any>;      // NEW: template context
  value?: number;
  bounds?: [number, number];
}

interface ValidationIssueProps {
  issue: ValidationIssueData;
}

export const ValidationIssue: React.FC<ValidationIssueProps> = ({ issue }) => {
  const { t } = useTranslation();

  // Use message_key if available (new i18n approach)
  let displayMessage = issue.message;

  if (issue.message_key) {
    // Format context for i18next interpolation
    const interpolationContext: Record<string, string> = {
      ...issue.context,
    };

    // Format numeric values with appropriate precision
    if (issue.value !== undefined) {
      interpolationContext.value = issue.value.toFixed(3);
    }
    if (issue.bounds) {
      interpolationContext.min = issue.bounds[0].toFixed(3);
      interpolationContext.max = issue.bounds[1].toFixed(3);
    }

    // Translate using i18next
    displayMessage = t(issue.message_key, interpolationContext);
  }

  const severityClass = `validation-issue validation-issue--${issue.severity}`;

  return (
    <div className={severityClass}>
      <span className="severity-icon">
        {issue.severity === 'error' && '❌'}
        {issue.severity === 'warning' && '⚠️'}
        {issue.severity === 'info' && 'ℹ️'}
      </span>
      <span className="metric">{issue.metric}:</span>
      <span className="message">{displayMessage}</span>
    </div>
  );
};
```

### Step 3: i18next Configuration

**File**: `frontend/src/i18n/config.ts`

```typescript
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

// Import translation files
import enMessages from '../../public/locales/en.json';
import esMessages from '../../public/locales/es.json';
import frMessages from '../../public/locales/fr.json';
import deMessages from '../../public/locales/de.json';

const resources = {
  en: { translation: enMessages },
  es: { translation: esMessages },
  fr: { translation: frMessages },
  de: { translation: deMessages },
};

// Detect language from localStorage, URL, or browser
const getInitialLanguage = () => {
  // Check localStorage
  const stored = localStorage.getItem('language');
  if (stored && resources[stored as keyof typeof resources]) {
    return stored;
  }

  // Check URL params
  const params = new URLSearchParams(window.location.search);
  const urlLang = params.get('lang');
  if (urlLang && resources[urlLang as keyof typeof resources]) {
    return urlLang;
  }

  // Check browser language
  const browserLang = navigator.language.split('-')[0];
  if (resources[browserLang as keyof typeof resources]) {
    return browserLang;
  }

  return 'en';
};

i18n
  .use(initReactI18next)
  .init({
    resources,
    lng: getInitialLanguage(),
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false,  // Already safe with React
    },
  });

export default i18n;
```

## JSON Response Example

### Before (Current - without i18n)

```json
{
  "status": "PASS_WITH_WARNINGS",
  "issues": [
    {
      "severity": "warning",
      "metric": "flight_time",
      "message": "Flight time 0.600s outside typical range [0.400-0.500]s for recreational",
      "value": 0.600,
      "bounds": [0.400, 0.500]
    },
    {
      "severity": "info",
      "metric": "jump_height",
      "message": "Jump height 0.450m within expected range for recreational",
      "value": 0.450,
      "bounds": null
    }
  ],
  "athlete_profile": "recreational"
}
```

### After (With i18n support)

```json
{
  "status": "PASS_WITH_WARNINGS",
  "issues": [
    {
      "severity": "warning",
      "metric": "flight_time",
      "message": "Flight time 0.600s outside typical range [0.400-0.500]s for recreational",
      "message_key": "validation.flight_time.outside_range",
      "context": {
        "profile": "recreational",
        "unit": "s",
        "min": 0.400,
        "max": 0.500
      },
      "value": 0.600,
      "bounds": [0.400, 0.500]
    },
    {
      "severity": "info",
      "metric": "jump_height",
      "message": "Jump height 0.450m within expected range for recreational",
      "message_key": "validation.jump_height.within_range",
      "context": {
        "profile": "recreational",
        "unit": "m"
      },
      "value": 0.450,
      "bounds": null
    }
  ],
  "athlete_profile": "recreational"
}
```

## Backward Compatibility

### Strategy

1. Keep `message` field (always populated)
1. Add optional `message_key` and `context` fields
1. Old clients use `message`
1. New clients use `message_key` + `context` for i18n
1. Remove `message` field in v0.70.0 if needed

### Client Compatibility Matrix

| Client Version | Backend Behavior                                       |
| -------------- | ------------------------------------------------------ |
| v0.59.x        | Uses `message` field (works fine)                      |
| v0.60.x+       | Has choice: use `message` or `message_key` + `context` |
| v0.70.x+       | Optional: remove `message` field entirely              |

## Testing Strategy

### Backend Tests

#### Unit Tests

```python
def test_flight_time_error_includes_message_key():
    """Verify error includes message_key and context."""
    validator = CMJMetricsValidator()
    result = CMJValidationResult()

    metrics = {"flight_time_ms": 0.001}  # Below minimum
    validator._check_flight_time(metrics, result, AthleteProfile.RECREATIONAL)

    assert result.issues[0].message_key == "validation.flight_time.below_minimum"
    assert result.issues[0].context == {"unit": "s"}

def test_validation_result_serializes_message_key():
    """Verify to_dict() includes message_key and context."""
    result = CMJValidationResult()
    result.add_error(
        "flight_time",
        "Test error",
        message_key="validation.flight_time.below_minimum",
        context={"unit": "s"}
    )

    data = result.to_dict()
    assert data["issues"][0]["message_key"] == "validation.flight_time.below_minimum"
    assert data["issues"][0]["context"] == {"unit": "s"}
```

#### Integration Tests

- All message_keys are unique
- All message_keys follow naming pattern
- All metrics with messages have message_keys

### Frontend Tests

#### Translation Completeness

```typescript
test('all message keys exist in all languages', () => {
  const enKeys = getAllMessageKeys(enMessages);
  const esKeys = getAllMessageKeys(esMessages);

  expect(esKeys).toEqual(enKeys);
});

test('message templates have correct placeholders', () => {
  const template = t('validation.flight_time.outside_range');
  expect(template).toContain('{{value}}');
  expect(template).toContain('{{unit}}');
  expect(template).toContain('{{profile}}');
  expect(template).toContain('{{min}}');
  expect(template).toContain('{{max}}');
});
```

#### Component Tests

```typescript
test('ValidationIssue renders translated message', () => {
  const issue: ValidationIssueData = {
    severity: 'warning',
    metric: 'flight_time',
    message_key: 'validation.flight_time.outside_range',
    context: {
      value: 0.6,
      unit: 's',
      profile: 'recreational',
      min: 0.4,
      max: 0.5
    },
    value: 0.6,
    bounds: [0.4, 0.5]
  };

  render(<ValidationIssue issue={issue} />);
  expect(screen.getByText(/Flight time 0.600s outside typical range/)).toBeInTheDocument();
});

test('ValidationIssue falls back to message field', () => {
  const issue: ValidationIssueData = {
    severity: 'warning',
    metric: 'flight_time',
    message: 'Test message',
    value: 0.6,
    bounds: [0.4, 0.5]
    // No message_key or context
  };

  render(<ValidationIssue issue={issue} />);
  expect(screen.getByText('Test message')).toBeInTheDocument();
});
```

## Implementation Timeline

1. **Week 1**: Backend changes (ValidationIssue, validator updates)
1. **Week 1**: Backend tests and validation
1. **Week 2**: Frontend translation files and i18next setup
1. **Week 2**: Component updates and testing
1. **Testing**: E2E and cross-browser validation

## Message Key Reference

### CMJ Validator Messages

**Flight Time** (4 keys):

- `validation.flight_time.within_range`
- `validation.flight_time.outside_range`
- `validation.flight_time.below_minimum`
- `validation.flight_time.above_maximum`

**Jump Height** (4 keys):

- `validation.jump_height.within_range`
- `validation.jump_height.outside_range`
- `validation.jump_height.no_jump`
- `validation.jump_height.above_maximum`

**Countermovement Depth** (3 keys):

- `validation.countermovement_depth.within_range`
- `validation.countermovement_depth.outside_range`
- `validation.countermovement_depth.insufficient`

**RSI & Consistency** (6+ keys):

- `validation.rsi.valid`
- `validation.rsi.outlier`
- `validation.rsi.invalid_calculation`
- `validation.consistency.height_flight_time`
- `validation.consistency.height_velocity`
- `validation.consistency.contact_depth`

**Triple Extension & Biomechanics** (6+ keys):

- `validation.triple_extension.normal`
- `validation.triple_extension.insufficient`
- `validation.triple_extension.compensatory`
- `validation.joint_angle.normal`
- `validation.joint_angle.excessive`
- `validation.joint_angle.insufficient`

### Drop Jump Validator Messages

**Contact Time** (4 keys):

- `validation.contact_time.within_range`
- `validation.contact_time.outside_range`
- `validation.contact_time.below_minimum`
- `validation.contact_time.above_maximum`

**Flight Time** (4 keys):

- `validation.flight_time.within_range`
- `validation.flight_time.outside_range`
- `validation.flight_time.below_minimum`
- `validation.flight_time.above_maximum`

**Jump Height** (4 keys):

- `validation.jump_height.within_range`
- `validation.jump_height.outside_range`
- `validation.jump_height.no_jump`
- `validation.jump_height.above_maximum`

**RSI & Consistency** (6+ keys):

- `validation.rsi.valid`
- `validation.rsi.outlier`
- `validation.rsi.invalid_calculation`
- `validation.consistency.height_flight_time`
- `validation.consistency.dual_height`

## Future Enhancements

1. **Dynamic Translation Loading**: Load only the language user selects
1. **Translation Management System**: Integrate with Crowdin or similar
1. **Right-to-Left Support**: For Arabic, Hebrew, etc.
1. **Regional Variants**: en-US, en-GB, es-MX, es-ES, etc.
1. **Glossary**: Medical/biomechanical term translations with context
