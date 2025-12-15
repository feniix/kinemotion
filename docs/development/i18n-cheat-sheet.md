# i18n Implementation Cheat Sheet

## Quick Reference

### Backend: Add message_key to ValidationIssue

**Old**:

```python
result.add_error("flight_time", f"Flight time {flight_time:.3f}s...")
```

**New**:

```python
result.add_error(
    "flight_time",
    f"Flight time {flight_time:.3f}s...",                    # Keep for backward compat
    message_key="validation.flight_time.below_minimum",      # NEW
    context={"unit": bounds.unit}                             # NEW
)
```

### Frontend: Translate with i18next

**Old** (display raw message):

```typescript
<span>{issue.message}</span>  // "Flight time 0.600s outside range..."
```

**New** (translate with context):

```typescript
const displayMessage = t(issue.message_key, {
  value: issue.value?.toFixed(3),
  unit: issue.context?.unit,
  profile: issue.context?.profile,
  min: issue.context?.min?.toFixed(3),
  max: issue.context?.max?.toFixed(3),
});
<span>{displayMessage}</span>
```

## Message Key Patterns

```
validation.flight_time.within_range    → INFO message
validation.flight_time.outside_range   → WARNING message
validation.flight_time.below_minimum   → ERROR message
validation.flight_time.above_maximum   → ERROR message

validation.jump_height.within_range    → INFO message
validation.jump_height.outside_range   → WARNING message
validation.jump_height.no_jump         → ERROR message
validation.jump_height.above_maximum   → ERROR message

validation.rsi.valid                   → INFO message
validation.rsi.outlier                 → WARNING message
validation.rsi.invalid_calculation     → ERROR message

validation.triple_extension.normal     → INFO message
validation.triple_extension.insufficient → WARNING message
validation.triple_extension.compensatory → WARNING message
```

## JSON Response Fields

**Always present** (backward compat):

```json
{
  "severity": "warning",
  "metric": "flight_time",
  "message": "Flight time 0.600s outside...",  // For old clients
  "value": 0.600,
  "bounds": [0.400, 0.500]
}
```

**NEW** (for i18n):

```json
{
  "message_key": "validation.flight_time.outside_range",
  "context": {
    "profile": "recreational",
    "unit": "s",
    "min": 0.400,
    "max": 0.500
  }
}
```

## Translation Template Placeholders

| Placeholder     | Example Value       | Format              |
| --------------- | ------------------- | ------------------- |
| `{{value}}`     | 0.600               | Number (3 decimals) |
| `{{unit}}`      | s, m, degrees       | String              |
| `{{profile}}`   | recreational, elite | String              |
| `{{min}}`       | 0.400               | Number (3 decimals) |
| `{{max}}`       | 0.500               | Number (3 decimals) |
| `{{tolerance}}` | 10                  | Number (integer)    |

## Translation File Structure

**File**: `frontend/public/locales/en.json`

```json
{
  "validation": {
    "flight_time": {
      "within_range": "...",
      "outside_range": "...",
      "below_minimum": "...",
      "above_maximum": "..."
    },
    "jump_height": {
      "within_range": "...",
      "outside_range": "...",
      "no_jump": "...",
      "above_maximum": "..."
    }
  }
}
```

**Same structure** for: es.json, fr.json, de.json, ja.json

## Code Changes Summary

### Backend

**1. Update ValidationIssue** (1 file, 2 lines):

```python
message_key: str | None = None
context: dict[str, Any] | None = None
```

**2. Update ValidationResult methods** (1 file, 3 methods):

- `add_error(...)` → add `message_key`, `context` params
- `add_warning(...)` → add `message_key`, `context` params
- `add_info(...)` → add `message_key`, `context` params

**3. Update validators** (2 files, 22 methods):

- CMJ: `_check_flight_time()`, `_check_jump_height()`, etc.
- Drop Jump: `_check_contact_time()`, `_check_flight_time()`, etc.
- Pattern: Add `message_key=...` and `context={...}` to each add\_\* call

**4. Update serialization** (2 files):

- CMJ: `CMJValidationResult.to_dict()` → add `message_key`, `context`
- Drop Jump: `DropJumpValidationResult.to_dict()` → add `message_key`, `context`

### Frontend

**1. Create translation files** (5 files):

- `frontend/public/locales/en.json` (and es, fr, de, ja)

**2. Setup i18next** (1 file):

- `frontend/src/i18n/config.ts`
- Update `frontend/src/main.tsx` to initialize i18n

**3. Update component** (1 file):

- `frontend/src/components/ValidationIssue.tsx` → use `t()` for translation

## Testing Checklist

**Backend**:

- [ ] message_key set correctly
- [ ] context dict populated correctly
- [ ] to_dict() includes new fields
- [ ] message field still works (backward compat)
- [ ] NumPy types converted to Python types

**Frontend**:

- [ ] All message keys in all languages
- [ ] Translation templates valid i18next syntax
- [ ] Component uses message_key + context
- [ ] Fallback to message field works
- [ ] Language switching works
- [ ] Number formatting correct (0.600)

**E2E**:

- [ ] Video → analysis → validation → translation → display
- [ ] Multiple languages tested
- [ ] URL parameter (?lang=es) works
- [ ] localStorage persistence works

## Time Estimates

| Task                                   | Time            |
| -------------------------------------- | --------------- |
| Update ValidationIssue + methods       | 1 hour          |
| Update CMJ validator (16 methods)      | 2-3 hours       |
| Update Drop Jump validator (6 methods) | 1-2 hours       |
| Update serialization                   | 30 min          |
| Backend tests                          | 1-2 hours       |
| **Backend Total**                      | **4-6 hours**   |
| Create translation files (5 languages) | 1 hour          |
| Setup i18next                          | 2 hours         |
| Update components                      | 2-3 hours       |
| Frontend tests                         | 1-2 hours       |
| **Frontend Total**                     | **6-8 hours**   |
| Integration & E2E tests                | 2-3 hours       |
| QA & validation                        | 2-3 hours       |
| **Testing Total**                      | **4-6 hours**   |
| **TOTAL**                              | **14-20 hours** |

## Files Modified

**Backend**:

```
src/kinemotion/core/validation.py               (1 file, +5 lines)
src/kinemotion/cmj/metrics_validator.py         (1 file, +code for 16 methods)
src/kinemotion/dropjump/metrics_validator.py    (1 file, +code for 6 methods)
tests/cmj/test_metrics_validator_i18n.py        (NEW)
tests/dropjump/test_metrics_validator_i18n.py   (NEW)
```

**Frontend**:

```
frontend/public/locales/en.json                 (NEW)
frontend/public/locales/es.json                 (NEW)
frontend/public/locales/fr.json                 (NEW)
frontend/public/locales/de.json                 (NEW)
frontend/public/locales/ja.json                 (NEW)
frontend/src/i18n/config.ts                     (NEW)
frontend/src/components/ValidationIssue.tsx     (UPDATED)
frontend/src/main.tsx                           (UPDATED)
frontend/src/components/__tests__/ValidationIssue.test.tsx (NEW)
```

## Backward Compatibility Guarantee

**For v0.60.0 and beyond**:

- ✅ Old clients using `message` field continue to work
- ✅ New clients can opt into `message_key` + `context`
- ✅ Response includes both fields
- ✅ No breaking changes to existing API

**Example**: Client built for v0.59 works fine with v0.60 response

```javascript
// Old code (still works!)
const message = issue.message;  // ✅ Field still exists
displayMessage(message);

// New code (also available!)
const message = t(issue.message_key, issue.context);  // ✅ New fields present
displayMessage(message);
```

## Context Values by Metric

| Metric                | Context Keys            | Example                                                   |
| --------------------- | ----------------------- | --------------------------------------------------------- |
| flight_time           | unit, profile, min, max | {unit: "s", profile: "recreational", min: 0.4, max: 0.5}  |
| jump_height           | unit, profile, min, max | {unit: "m", profile: "elite", min: 0.5, max: 0.8}         |
| countermovement_depth | unit, profile, min, max | {unit: "m", profile: "trained", min: 0.3, max: 0.6}       |
| rsi                   | unit, profile           | {unit: "", profile: "elite"}                              |
| contact_time          | unit, profile, min, max | {unit: "ms", profile: "recreational", min: 200, max: 400} |
| triple_extension      | pattern_name            | {pattern_name: "compensatory"}                            |

## Common Mistakes to Avoid

❌ **Mistake**: Format value in validator

```python
# DON'T DO THIS
result.add_error(
    "flight_time",
    f"Flight time {flight_time:.3f}s...",
    # No message_key!
)
```

✅ **Correct**: Provide raw value and let frontend format

```python
# DO THIS
result.add_error(
    "flight_time",
    f"Flight time {flight_time:.3f}s...",  # Keep for backward compat
    message_key="validation.flight_time.below_minimum",
    context={"unit": "s"}  # Raw value passed to frontend
)
```

❌ **Mistake**: Use different key format

```python
# DON'T DO THIS
message_key="flight_time_below_min"  # Invalid format
message_key="FlightTimeBelow"        # Invalid format
```

✅ **Correct**: Use consistent pattern

```python
# DO THIS
message_key="validation.flight_time.below_minimum"  # Correct format
```

❌ **Mistake**: Forget to update all validators

```python
# DON'T DO THIS - some methods have message_key, others don't
# This creates inconsistency
```

✅ **Correct**: Update all validation methods

```python
# DO THIS - all _check_* methods have message_key + context
```

## Validation Checklist

### Before Committing

```bash
# Backend
uv run pytest                    # All tests pass
uv run ruff check --fix         # No linting errors
uv run pyright                  # No type errors

# Frontend
npm test                        # All tests pass
npm run lint                    # No linting errors
npm run type-check             # No type errors
```

### Before Merging

```bash
# Verify message key patterns
python scripts/validate_message_keys.py

# Check all keys present in all languages
python scripts/validate_translation_completeness.py

# Verify backward compatibility
npm run test:e2e -- --old-client  # Test with v0.59 client
```

### Before Release

```bash
# Full test suite
uv run pytest --cov
npm test --coverage

# Integration test
npm run test:e2e

# Manual smoke test
# 1. Upload video
# 2. Verify messages appear in multiple languages
# 3. Test language switching
# 4. Verify format (0.600 not 0.6)
```

______________________________________________________________________

**Print this page for quick reference during implementation!**
