# i18n Implementation Quick Start Guide

## Overview

This guide provides step-by-step instructions to implement i18n support for validation messages. The implementation is **non-breaking** and backward-compatible.

## Quick Stats

- **Backend Changes**: ~4-6 hours (update validators + tests)
- **Frontend Changes**: ~6-8 hours (translations + i18next + component)
- **Testing**: ~4-6 hours (unit + integration + E2E)
- **Total**: 14-20 hours
- **Breaking Change**: No (backward compatible)
- **Version**: Minor version bump (non-breaking change)

## Phase 1: Backend Implementation (4-6 hours)

### Step 1.1: Update Core ValidationIssue (15 min)

**File**: `/Users/feniix/src/personal/cursor/kinemotion/src/kinemotion/core/validation.py`

Add two new optional fields to `ValidationIssue` dataclass:

```python
@dataclass
class ValidationIssue:
    """Single validation issue."""

    severity: ValidationSeverity
    metric: str
    message: str
    message_key: str | None = None        # NEW
    context: dict[str, Any] | None = None # NEW
    value: float | None = None
    bounds: tuple[float, float] | None = None
```

### Step 1.2: Update ValidationResult Methods (30 min)

**File**: `/Users/feniix/src/personal/cursor/kinemotion/src/kinemotion/core/validation.py`

Add optional parameters to `add_error()`, `add_warning()`, `add_info()`:

```python
def add_error(
    self,
    metric: str,
    message: str,
    value: float | None = None,
    bounds: tuple[float, float] | None = None,
    message_key: str | None = None,      # NEW
    context: dict[str, Any] | None = None, # NEW
) -> None:
    """Add error-level issue with optional i18n support."""
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
    message_key: str | None = None,      # NEW
    context: dict[str, Any] | None = None, # NEW
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
    message_key: str | None = None,      # NEW
    context: dict[str, Any] | None = None, # NEW
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

### Step 1.3: Update CMJ Validator (2-3 hours)

**File**: `/Users/feniix/src/personal/cursor/kinemotion/src/kinemotion/cmj/metrics_validator.py`

Update all 16 validation methods. Template for each:

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
            context={"profile": profile.value, "unit": bounds.unit},  # NEW
        )
    else:
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

**Methods to update**:

1. `_check_flight_time()`
1. `_check_jump_height()`
1. `_check_countermovement_depth()`
1. `_check_concentric_duration()`
1. `_check_eccentric_duration()`
1. `_check_peak_velocities()`
1. `_check_flight_time_height_consistency()`
1. `_check_velocity_height_consistency()`
1. `_check_rsi_validity()`
1. `_check_depth_height_ratio()`
1. `_check_contact_depth_ratio()`
1. `_check_triple_extension()`
1. `_check_joint_compensation_pattern()`
1. Plus any other validation methods

### Step 1.4: Update Drop Jump Validator (1-2 hours)

**File**: `/Users/feniix/src/personal/cursor/kinemotion/src/kinemotion/dropjump/metrics_validator.py`

Apply the same pattern to all 6 validation methods:

1. `_check_contact_time()`
1. `_check_flight_time()`
1. `_check_jump_height()`
1. `_check_rsi()`
1. `_check_dual_height_consistency()`

### Step 1.5: Update Serialization (30 min)

**File**: `/Users/feniix/src/personal/cursor/kinemotion/src/kinemotion/cmj/metrics_validator.py`

Update `CMJValidationResult.to_dict()`:

```python
def to_dict(self) -> dict:
    """Convert validation result to JSON-serializable dictionary."""
    return {
        "status": self.status,
        "issues": [
            {
                "severity": issue.severity.value,
                "metric": issue.metric,
                "message": issue.message,
                "message_key": issue.message_key,      # NEW
                "context": issue.context,              # NEW
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

Repeat for `DropJumpValidationResult.to_dict()` in dropjump module.

### Step 1.6: Add Backend Tests (1-2 hours)

**Create/update**: `tests/cmj/test_metrics_validator_i18n.py`

```python
import pytest
from kinemotion.cmj.metrics_validator import CMJMetricsValidator, CMJValidationResult
from kinemotion.core.validation import AthleteProfile

class TestI18nSupport:
    """Test i18n message_key and context fields."""

    def test_flight_time_error_includes_message_key(self):
        """Verify error includes message_key and context."""
        validator = CMJMetricsValidator()
        result = CMJValidationResult()
        metrics = {"flight_time_ms": 0.001}

        validator._check_flight_time(metrics, result, AthleteProfile.RECREATIONAL)

        assert len(result.issues) == 1
        assert result.issues[0].message_key == "validation.flight_time.below_minimum"
        assert result.issues[0].context == {"unit": "s"}

    def test_flight_time_info_includes_context(self):
        """Verify info message includes profile context."""
        validator = CMJMetricsValidator()
        result = CMJValidationResult()
        metrics = {"flight_time_ms": 350}

        validator._check_flight_time(metrics, result, AthleteProfile.RECREATIONAL)

        assert result.issues[0].message_key == "validation.flight_time.within_range"
        assert result.issues[0].context["profile"] == "recreational"
        assert result.issues[0].context["unit"] == "s"

    def test_validation_result_serializes_i18n_fields(self):
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

    def test_backward_compatibility_message_field_preserved(self):
        """Verify 'message' field is still populated for backward compatibility."""
        result = CMJValidationResult()
        result.add_error(
            "flight_time",
            "Old style message",
            message_key="validation.flight_time.below_minimum",
            context={"unit": "s"}
        )

        data = result.to_dict()
        assert data["issues"][0]["message"] == "Old style message"
        assert data["issues"][0]["message_key"] == "validation.flight_time.below_minimum"
```

**Add similar tests for Drop Jump validator**

## Phase 2: Frontend Implementation (6-8 hours)

### Step 2.1: Create Translation Files (1 hour)

**Create directory**: `/Users/feniix/frontend/public/locales/`

**Files to create**:

- `en.json` (English)
- `es.json` (Spanish)
- `fr.json` (French)
- `de.json` (German)
- `ja.json` (Japanese)

**Example**: `en.json`

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
    }
  }
}
```

### Step 2.2: Setup i18next (2 hours)

**Install dependencies**:

```bash
cd frontend
npm install i18next react-i18next i18next-browser-languagedetector
```

**Create**: `frontend/src/i18n/config.ts`

```typescript
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

// Import translation files
import enMessages from '../../public/locales/en.json';
import esMessages from '../../public/locales/es.json';
import frMessages from '../../public/locales/fr.json';
import deMessages from '../../public/locales/de.json';
import jaMessages from '../../public/locales/ja.json';

const resources = {
  en: { translation: enMessages },
  es: { translation: esMessages },
  fr: { translation: frMessages },
  de: { translation: deMessages },
  ja: { translation: jaMessages },
};

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false,
    },
  });

export default i18n;
```

**Update**: `frontend/src/main.tsx`

```typescript
import './i18n/config';
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
```

### Step 2.3: Update ValidationIssue Component (2-3 hours)

**File**: `frontend/src/components/ValidationIssue.tsx`

```typescript
import React from 'react';
import { useTranslation } from 'react-i18next';

interface ValidationIssueData {
  severity: 'error' | 'warning' | 'info';
  metric: string;
  message: string;
  message_key?: string;
  context?: Record<string, any>;
  value?: number;
  bounds?: [number, number];
}

interface ValidationIssueProps {
  issue: ValidationIssueData;
}

export const ValidationIssue: React.FC<ValidationIssueProps> = ({ issue }) => {
  const { t } = useTranslation();

  let displayMessage = issue.message;

  if (issue.message_key && issue.context) {
    const interpolationContext: Record<string, string> = {};

    // Copy all context values, converting to strings
    for (const [key, value] of Object.entries(issue.context)) {
      if (typeof value === 'number') {
        interpolationContext[key] = value.toFixed(3);
      } else {
        interpolationContext[key] = String(value);
      }
    }

    // Format value and bounds if provided
    if (issue.value !== undefined) {
      interpolationContext.value = issue.value.toFixed(3);
    }
    if (issue.bounds) {
      interpolationContext.min = issue.bounds[0].toFixed(3);
      interpolationContext.max = issue.bounds[1].toFixed(3);
    }

    try {
      displayMessage = t(issue.message_key, interpolationContext);
    } catch (error) {
      // Fallback to message field if translation fails
      console.warn(`Missing translation: ${issue.message_key}`);
      displayMessage = issue.message;
    }
  }

  const severityEmoji = {
    error: '❌',
    warning: '⚠️',
    info: 'ℹ️',
  };

  return (
    <div className={`validation-issue validation-issue--${issue.severity}`}>
      <span className="severity-icon">{severityEmoji[issue.severity]}</span>
      <span className="metric">{issue.metric}:</span>
      <span className="message">{displayMessage}</span>
    </div>
  );
};
```

### Step 2.4: Add Language Selector UI (1-2 hours)

**File**: `frontend/src/components/LanguageSelector.tsx`

```typescript
import React from 'react';
import { useTranslation } from 'react-i18next';

export const LanguageSelector: React.FC = () => {
  const { i18n } = useTranslation();

  const languages = [
    { code: 'en', label: 'English' },
    { code: 'es', label: 'Español' },
    { code: 'fr', label: 'Français' },
    { code: 'de', label: 'Deutsch' },
    { code: 'ja', label: '日本語' },
  ];

  const handleLanguageChange = (code: string) => {
    i18n.changeLanguage(code);
    localStorage.setItem('language', code);
  };

  return (
    <div className="language-selector">
      {languages.map((lang) => (
        <button
          key={lang.code}
          onClick={() => handleLanguageChange(lang.code)}
          className={i18n.language === lang.code ? 'active' : ''}
        >
          {lang.label}
        </button>
      ))}
    </div>
  );
};
```

### Step 2.5: Add Frontend Tests (1-2 hours)

**Create**: `frontend/src/components/__tests__/ValidationIssue.test.tsx`

```typescript
import { render, screen } from '@testing-library/react';
import { I18nextProvider } from 'react-i18next';
import i18n from '../../i18n/config';
import { ValidationIssue } from '../ValidationIssue';

describe('ValidationIssue', () => {
  test('renders translated message with context substitution', async () => {
    await i18n.changeLanguage('en');

    const issue = {
      severity: 'warning' as const,
      metric: 'flight_time',
      message: 'Test message',
      message_key: 'validation.flight_time.outside_range',
      context: {
        profile: 'recreational',
        unit: 's',
        min: 0.4,
        max: 0.5,
      },
      value: 0.6,
      bounds: [0.4, 0.5],
    };

    render(
      <I18nextProvider i18n={i18n}>
        <ValidationIssue issue={issue} />
      </I18nextProvider>,
    );

    expect(
      screen.getByText(
        /Flight time 0.600s outside typical range \[0.400-0.500\]s for recreational/,
      ),
    ).toBeInTheDocument();
  });

  test('falls back to message field when message_key not provided', () => {
    const issue = {
      severity: 'info' as const,
      metric: 'jump_height',
      message: 'Fallback message',
      value: 0.45,
    };

    render(
      <I18nextProvider i18n={i18n}>
        <ValidationIssue issue={issue} />
      </I18nextProvider>,
    );

    expect(screen.getByText('Fallback message')).toBeInTheDocument();
  });
});
```

## Phase 3: Integration Testing (2-3 hours)

### Step 3.1: E2E Test

Test full flow: upload video → validate → translate → display

```python
# tests/e2e/test_cmj_with_i18n.py
import json
from kinemotion.cmj.api import process_cmj_video

def test_cmj_validation_includes_message_keys():
    """Verify CMJ analysis response includes i18n fields."""
    result = process_cmj_video("test_video.mp4")

    response_dict = result.metrics.to_dict()

    # Check validation structure
    assert "validation" in response_dict
    validation = response_dict["validation"]

    if validation["issues"]:
        issue = validation["issues"][0]

        # Backward compat: message field exists
        assert "message" in issue
        assert isinstance(issue["message"], str)

        # New fields: message_key and context
        if issue["severity"] != "info":  # May be None for some issues
            assert "message_key" in issue
            assert "context" in issue
            assert isinstance(issue["message_key"], str)
            assert isinstance(issue["context"], dict)
```

### Step 3.2: Validate Message Keys

Create a script to validate all message keys:

```python
# scripts/validate_message_keys.py
import json
import re
from pathlib import Path

def validate_message_keys():
    """Ensure all message_keys follow naming convention."""
    # Pattern: validation.[domain].[metric].[condition]
    pattern = re.compile(r'^validation\.[a-z_]+\.[a-z_]+$')

    locale_dir = Path('frontend/public/locales')
    all_keys = set()

    # Collect all keys from English
    with open(locale_dir / 'en.json') as f:
        en_data = json.load(f)
        extract_keys(en_data, '', all_keys)

    # Verify all other languages have same keys
    for lang_file in locale_dir.glob('*.json'):
        if lang_file.name == 'en.json':
            continue

        with open(lang_file) as f:
            lang_data = json.load(f)
            lang_keys = set()
            extract_keys(lang_data, '', lang_keys)

        missing = all_keys - lang_keys
        if missing:
            print(f"Missing keys in {lang_file.name}:")
            for key in missing:
                print(f"  - {key}")

    # Validate key format
    for key in all_keys:
        if not pattern.match(key):
            print(f"Invalid key format: {key}")

def extract_keys(obj, prefix, keys):
    """Recursively extract all JSON keys."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            full_key = f"{prefix}.{k}" if prefix else k
            if isinstance(v, dict):
                extract_keys(v, full_key, keys)
            else:
                keys.add(full_key)

if __name__ == '__main__':
    validate_message_keys()
```

## Checklist

### Backend Implementation

- [ ] Update `ValidationIssue` with `message_key` and `context` fields
- [ ] Update `add_error()`, `add_warning()`, `add_info()` method signatures
- [ ] Update all 16 CMJ validator methods
- [ ] Update all 6 Drop Jump validator methods
- [ ] Update `CMJValidationResult.to_dict()` to include new fields
- [ ] Update `DropJumpValidationResult.to_dict()`
- [ ] Add unit tests for message_key assignment
- [ ] Add integration tests for message_key uniqueness
- [ ] Test backward compatibility (message field still works)
- [ ] Run full test suite: `uv run pytest`

### Frontend Implementation

- [ ] Create `/public/locales/` directory structure
- [ ] Create translation files: en.json, es.json, fr.json, de.json, ja.json
- [ ] Install i18next and react-i18next
- [ ] Create `src/i18n/config.ts`
- [ ] Update `src/main.tsx` to initialize i18n
- [ ] Update `ValidationIssue.tsx` component
- [ ] Add language selector component
- [ ] Add component tests for ValidationIssue
- [ ] Add E2E test for full flow
- [ ] Test language switching

### Quality Assurance

- [ ] Run backend linting: `uv run ruff check && uv run pyright`
- [ ] Run frontend linting: `npm run lint`
- [ ] Run backend tests: `uv run pytest`
- [ ] Run frontend tests: `npm test`
- [ ] Validate message key format: `python scripts/validate_message_keys.py`
- [ ] Check translation completeness: All keys present in all languages
- [ ] Manual E2E: Upload video, verify messages translate correctly
- [ ] Test with different browser languages
- [ ] Test URL parameter: `?lang=es`
- [ ] Test localStorage persistence

## Deployment Steps

1. **Backend Deploy**:

   - Merge backend PR
   - Tag release with minor version bump
   - Deploy to PyPI

1. **Frontend Deploy**:

   - Merge frontend PR
   - Deploy to Vercel (automatic from main branch)

1. **Documentation**:

   - Update CHANGELOG.md with i18n feature
   - Add i18n documentation to docs/
   - Update API reference with new fields

## Rollback Plan

If issues occur:

1. Revert frontend deployment (Vercel: one-click)
1. Revert backend to previous release
1. Keep `message` field compatibility ensures clients continue to work
1. Issue patch release with fixes

## Success Metrics

- All 620+ backend tests pass
- All frontend tests pass
- Message keys complete in all 5 languages
- No TypeScript errors (pyright strict)
- No linting errors (ruff)
- Coverage maintained at 80%+
- E2E tests verify translations work
