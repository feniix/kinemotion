# i18n Implementation Summary

## Executive Overview

We are implementing internationalization (i18n) support for Kinemotion validation messages using a **structured data approach** where:

1. **Backend** (Python/FastAPI): Returns structured validation data with translation keys and context
1. **Frontend** (React/TypeScript): Handles all translation and presentation logic
1. **Result**: Decoupled, maintainable, and scalable i18n system

## Why This Approach?

| Aspect                 | Backend Translation ❌   | Structured Data ✅    |
| ---------------------- | ------------------------ | --------------------- |
| **Backend Complexity** | High (translation logic) | Low (validation only) |
| **API Changes**        | Per language             | Language-independent  |
| **New Languages**      | Backend redeploy needed  | Frontend files only   |
| **Team Workflow**      | Tight coupling           | Decoupled teams       |
| **Scalability**        | Limited                  | Unlimited             |

**Recommendation**: Option B (Structured Data) for simplicity, maintainability, and scalability.

## What Gets Implemented

### Backend Changes (Python)

**ValidationIssue** - Add optional fields:

```python
message_key: str | None = None          # e.g., "validation.flight_time.outside_range"
context: dict[str, Any] | None = None   # e.g., {"profile": "recreational", "unit": "s"}
```

**All Validators** - Update messages from formatted strings to message_keys + context:

**Before**:

```python
result.add_error(
    "flight_time",
    f"Flight time {flight_time:.3f}s below frame rate resolution limit"
)
```

**After**:

```python
result.add_error(
    "flight_time",
    f"Flight time {flight_time:.3f}s below frame rate resolution limit",  # Keep for backward compat
    message_key="validation.flight_time.below_minimum",                   # NEW
    context={"unit": "s"}                                                  # NEW
)
```

### Frontend Changes (React/TypeScript)

**Translation Files** - Create JSON with message templates:

```json
{
  "validation": {
    "flight_time": {
      "below_minimum": "Flight time {{value}}{{unit}} below frame rate resolution limit"
    }
  }
}
```

**Component** - Use i18next to translate and render:

```typescript
const displayMessage = t(issue.message_key, {
  value: issue.value.toFixed(3),
  unit: issue.context.unit,
  // ... other context values
});
```

## Implementation Scope

### Backend

- **Files to change**: 3 core + 2 specialized validators
- **Methods to update**: 22 validation methods
- **New tests**: 5-10 test cases
- **Time**: 4-6 hours

### Frontend

- **Translation files**: 5 languages (en, es, fr, de, ja)
- **New libraries**: i18next, react-i18next
- **Component updates**: 1-2 components
- **New tests**: 5-10 test cases
- **Time**: 6-8 hours

### Testing

- **Unit tests**: Validate message_key assignment
- **Integration tests**: Message key uniqueness and format
- **E2E tests**: Full video → validation → translation flow
- **Time**: 4-6 hours

**Total Effort**: 14-20 hours

## JSON Response Example

### New Response Format (with i18n)

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
    }
  ],
  "athlete_profile": "recreational"
}
```

**Key Points**:

- `message` field kept for backward compatibility
- `message_key` tells frontend which translation to use
- `context` provides values for template interpolation
- Response is language-independent (no translation on backend)

## Message Key Naming Convention

**Pattern**: `validation.[metric].[condition]`

**Examples**:

- `validation.flight_time.within_range` - Value in expected range (INFO)
- `validation.flight_time.outside_range` - Value outside but physically possible (WARNING)
- `validation.flight_time.below_minimum` - Below frame rate resolution (ERROR)
- `validation.jump_height.no_jump` - Essentially no jump detected (ERROR)
- `validation.rsi.invalid_calculation` - RSI calculation error (WARNING)
- `validation.triple_extension.insufficient` - Poor triple extension (WARNING)

## Backward Compatibility

**Non-Breaking Implementation**:

- `message` field continues to work as-is
- Old clients: use `message` field (works fine)
- New clients: use `message_key` + `context` for i18n
- Optional fields can be safely added

**Migration Timeline**:

- Phase 1: Introduce message_key + context (optional)
- Phase 2: Increase adoption (all validators updated)
- Phase 3+: Optional cleanup (could remove message field if desired)

## Testing Strategy

### Backend Tests

✅ Verify message_key is set for all validation paths
✅ Verify context dict is populated with correct values
✅ Verify serialization includes new fields
✅ Verify backward compatibility (message field still works)

### Frontend Tests

✅ Verify translation files complete (all keys in all languages)
✅ Verify message template placeholders match context
✅ Verify ValidationIssue component renders translated messages
✅ Verify fallback to message field when key missing

### E2E Tests

✅ Upload video → analyze → validate → translate → display
✅ Test multiple languages
✅ Test language switching
✅ Test number formatting (0.600 instead of 0.6)

## Metrics Summary

| Metric                            | Value                                     |
| --------------------------------- | ----------------------------------------- |
| **Backend files to change**       | 5 (1 core + 2 specialized + 2 tests)      |
| **Validation methods to update**  | 22 (CMJ: 16, Drop Jump: 6)                |
| **Frontend components to update** | 1-2 (ValidationIssue + optional selector) |
| **Translation files to create**   | 5 (en, es, fr, de, ja)                    |
| **Message keys needed**           | ~45-50 (organized by metric)              |
| **New tests**                     | 10-20 (unit + integration + E2E)          |
| **Estimated effort**              | 14-20 hours                               |
| **Breaking change**               | No (fully backward compatible)            |
| **Version bump**                  | Minor version bump (non-breaking)         |

## Files to Create/Update

### Backend (Python)

```
src/kinemotion/core/validation.py
├─ Update ValidationIssue dataclass
├─ Update add_error() signature
├─ Update add_warning() signature
└─ Update add_info() signature

src/kinemotion/cmj/metrics_validator.py
├─ Update all 16 _check_* methods
└─ Update CMJValidationResult.to_dict()

src/kinemotion/dropjump/metrics_validator.py
├─ Update all 6 _check_* methods
└─ Update DropJumpValidationResult.to_dict()

tests/cmj/test_metrics_validator_i18n.py (NEW)
└─ Test message_key assignment and context

tests/dropjump/test_metrics_validator_i18n.py (NEW)
└─ Test message_key assignment and context
```

### Frontend (React/TypeScript)

```
frontend/public/locales/
├─ en.json (NEW)
├─ es.json (NEW)
├─ fr.json (NEW)
├─ de.json (NEW)
└─ ja.json (NEW)

frontend/src/i18n/
└─ config.ts (NEW) - i18next initialization

frontend/src/components/
├─ ValidationIssue.tsx (UPDATED)
└─ LanguageSelector.tsx (NEW, optional)

frontend/src/components/__tests__/
└─ ValidationIssue.test.tsx (NEW)

frontend/src/main.tsx (UPDATED)
└─ Initialize i18n
```

## Deployment Steps

1. **Backend Deploy**:

   ```bash
   git tag <version>
   git push origin <version>
   # PyPI automatically deploys on tag
   ```

1. **Frontend Deploy**:

   ```bash
   git push origin main
   # Vercel automatically deploys
   ```

1. **Release Checklist**:

   - [ ] All tests passing (backend + frontend)
   - [ ] No type errors (pyright strict)
   - [ ] No linting errors (ruff)
   - [ ] Message keys complete in all languages
   - [ ] E2E tests pass
   - [ ] CHANGELOG.md updated
   - [ ] Documentation updated
   - [ ] Verify backward compatibility (old clients work)

## Phase Breakdown

### Phase 1: Backend (4-6 hours)

1. Update ValidationIssue dataclass (15 min)
1. Update ValidationResult methods (30 min)
1. Update CMJ validator (2-3 hours)
1. Update Drop Jump validator (1-2 hours)
1. Update serialization (30 min)
1. Add tests (1-2 hours)

### Phase 2: Frontend (6-8 hours)

1. Create translation files (1 hour)
1. Setup i18next (2 hours)
1. Update components (2-3 hours)
1. Add tests (1-2 hours)

### Phase 3: Testing & QA (4-6 hours)

1. Backend unit tests
1. Frontend component tests
1. E2E tests
1. Manual testing with multiple languages
1. Verify message key completeness

## Success Criteria

✅ All 620+ backend tests pass with new fields
✅ All frontend tests pass
✅ Message keys present in all 5 languages
✅ No TypeScript errors (pyright strict)
✅ No linting errors (ruff check)
✅ Code coverage ≥ 80% (maintained)
✅ E2E tests verify translations work
✅ Backward compatibility verified
✅ Release notes document the change
✅ Users can switch languages in UI

## Next Steps

1. **Review this specification** with team
1. **Create feature branch**: `feat/i18n-validation-messages`
1. **Start Phase 1**: Backend implementation
1. **Follow Quick Start Guide** at `docs/development/i18n-quick-start-guide.md`
1. **Reference Architecture** at `docs/development/i18n-architecture-diagram.md`
1. **Full specification** at `docs/development/i18n-validation-messages-specification.md`

## Questions & Support

- **Architecture questions**: See i18n-architecture-diagram.md
- **Implementation details**: See i18n-validation-messages-specification.md
- **Step-by-step guide**: See i18n-quick-start-guide.md
- **Message keys reference**: See i18n-validation-messages-specification.md (Message Key Reference section)

______________________________________________________________________

**Status**: ✅ Specification Complete
**Version**: 1.0
**Date**: 2024-12-14
**Target**: Future release with minor version bump
