---
title: i18n Implementation Plan for Validation Messages
type: note
permalink: development/i18n-implementation-plan-for-validation-messages
---

# Internationalization (i18n) Implementation Plan for Validation Messages

## Executive Summary

Implementing i18n for validation messages in the Kinemotion backend using **Option B: Structured Data + Frontend Translation** approach. This decouples the backend from translation logic and aligns with REST API best practices.

## Current State Analysis

### Validator Structure
- **Location**: `src/kinemotion/cmj/metrics_validator.py` and `src/kinemotion/dropjump/metrics_validator.py`
- **ValidationResult Flow**:
  1. Validators generate formatted messages: `"Flight time 0.600s within expected range for recreational"`
  2. Messages stored in `ValidationIssue` objects with metric, value, bounds, severity
  3. Sent to frontend via `CMJMetrics.validation_result` → `to_dict()`

### Current Message Examples
```python
# ERROR
result.add_error("flight_time", f"Flight time {flight_time:.3f}s below frame rate resolution limit")

# WARNING
result.add_warning("flight_time", f"Flight time {flight_time:.3f}s outside typical range [{min:.3f}-{max:.3f}]s for {profile}")

# INFO
result.add_info("flight_time", f"Flight time {flight_time:.3f}s within expected range for {profile}")
```

### Metrics with Validation Messages
**CMJ Validator** (16 validation methods):
- Multiple validation checks generating 30+ message variants

**Drop Jump Validator** (6 validation methods):
- Multiple validation checks generating 15+ message variants

## Design: Structured Data Approach (Option B)

### Why This Approach?
- Decouples backend from translation logic
- Stable API contract (language-independent)
- Frontend-only updates for new languages
- Follows REST API best practices
- Separates concerns: backend = validation logic, frontend = presentation/translation

## New Validation Response Structure

**After (Proposed)**:
```json
{
  "status": "PASS_WITH_WARNINGS",
  "issues": [
    {
      "severity": "warning",
      "metric": "flight_time",
      "message_key": "validation.flight_time.outside_range",
      "value": 0.600,
      "bounds": [0.400, 0.500],
      "context": {
        "min": 0.400,
        "max": 0.500,
        "profile": "recreational",
        "unit": "s"
      }
    }
  ],
  "athlete_profile": "recreational"
}
```

## Message Key Naming Convention

Pattern: `validation.[metric].[condition]`

Examples:
- `validation.flight_time.within_range` - Value in expected range (INFO)
- `validation.flight_time.outside_range` - Value outside but physically possible (WARNING)
- `validation.flight_time.below_minimum` - Below frame rate resolution (ERROR)
- `validation.jump_height.no_jump` - Essentially no jump detected (ERROR)

## Implementation Summary

### Phase 1: Backend Changes
1. Add `message_key` and `context` fields to `ValidationIssue`
2. Update `add_error()`, `add_warning()`, `add_info()` methods
3. Update all 22 validation methods in both validators
4. Update `to_dict()` serialization

### Phase 2: Frontend Changes
1. Create translation files (en, es, fr, de, ja, etc.)
2. Implement i18next or react-intl
3. Update ValidationIssue component to use message_key + context
4. Add language selection UI

### Phase 3: Backward Compatibility
- Keep `message` field for old clients
- Message_key is optional
- Gradual migration over 2-3 releases
