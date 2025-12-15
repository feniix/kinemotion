# i18n Architecture Diagram

## Data Flow: From Analysis to Localized UI

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          USER INTERACTION FLOW                          │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────┐
│   1. VIDEO UPLOAD       │
│   (React Frontend)      │
│   - Select language:    │
│     English, Spanish,   │
│     French, German      │
└────────────┬────────────┘
             │
             │ POST /api/cmj-analyze
             │ Accept-Language: es
             │
             ▼
┌──────────────────────────────────────────┐
│      2. BACKEND PROCESSING               │
│      (FastAPI Python Server)             │
│                                          │
│  ┌──────────────────────────────┐        │
│  │ MediaPipe Pose Detection     │        │
│  │ - Extract joint positions    │        │
│  │ - Detect jump phases         │        │
│  └──────────────────┬───────────┘        │
│                     │                    │
│  ┌──────────────────▼───────────┐        │
│  │ Kinematic Calculation         │        │
│  │ - Flight time               │        │
│  │ - Jump height               │        │
│  │ - Velocity, acceleration    │        │
│  └──────────────────┬───────────┘        │
│                     │                    │
│  ┌──────────────────▼──────────────────┐ │
│  │ VALIDATION (key change here)        │ │
│  │                                     │ │
│  │ validator = CMJMetricsValidator()   │ │
│  │ result = validator.validate(metrics)│ │
│  │                                     │ │
│  │ # Old: message = formatted string  │ │
│  │ # New: message_key + context       │ │
│  │                                     │ │
│  │ For each issue:                     │ │
│  │ ├─ metric: "flight_time"            │ │
│  │ ├─ severity: "warning"              │ │
│  │ ├─ message: "Flight time 0.600s..." │ │
│  │ ├─ message_key: "validation.       │ │
│  │ │    flight_time.outside_range"    │ │
│  │ ├─ value: 0.600                    │ │
│  │ ├─ bounds: [0.4, 0.5]              │ │
│  │ └─ context: {                       │ │
│  │    "profile": "recreational",      │ │
│  │    "unit": "s",                     │ │
│  │    "min": 0.400,                    │ │
│  │    "max": 0.500                     │ │
│  │   }                                 │ │
│  └──────────────────┬──────────────────┘ │
│                     │                    │
│  ┌──────────────────▼──────────────────┐ │
│  │ JSON SERIALIZATION                  │ │
│  │ (to_dict() method)                  │ │
│  │                                     │ │
│  │ ✓ Converts NumPy types to Python   │ │
│  │ ✓ Includes both message fields     │ │
│  │ ✓ IMPORTANT: No translation!       │ │
│  └──────────────────┬──────────────────┘ │
│                     │                    │
└─────────────────────┼────────────────────┘
                      │
                      │ HTTP 200 OK
                      │ Content-Type: application/json
                      │
                      ▼
┌─────────────────────────────────────────┐
│  3. RESPONSE JSON (Language-Independent)│
│     (Same response for all users)        │
│                                         │
│  {                                      │
│    "metrics": { ... },                  │
│    "validation": {                      │
│      "status": "PASS_WITH_WARNINGS",    │
│      "issues": [                        │
│        {                                │
│  "metric": "flight_time",              │
│  "severity": "warning",                │
│  "message": "Flight time 0.600s...",   │ (Backward compat)
│  "message_key": "validation.          │ (NEW)
│     flight_time.outside_range",       │
│  "context": {                          │ (NEW)
│    "profile": "recreational",          │
│    "unit": "s",                         │
│    "min": 0.400,                        │
│    "max": 0.500                         │
│  },                                    │
│  "value": 0.600,                       │
│  "bounds": [0.400, 0.500]              │
│        }                                │
│      ]                                  │
│    }                                    │
│  }                                      │
│                                         │
│  ✓ No translation logic on backend!     │
│  ✓ Structured data only                 │
│  ✓ Frontend makes presentation decision │
└─────────────────┬───────────────────────┘
                  │
                  │ Response delivered to browser
                  │
                  ▼
┌──────────────────────────────────────────────────────┐
│  4. FRONTEND TRANSLATION (React Component)           │
│     (i18next)                                        │
│                                                      │
│  ValidationIssue component receives:                 │
│  ├─ message_key: "validation.flight_time.         │
│  │              outside_range"                     │
│  ├─ context: { profile, unit, min, max }           │
│  └─ language: "es" (from localStorage/URL/header)  │
│                                                      │
│  Steps:                                              │
│  1. Load translation from locales/es.json            │
│  2. Template: "Tiempo de vuelo {{value}}{{unit}}..." │
│  3. Replace {{value}} = "0.600", {{unit}} = "s"     │
│  4. Replace {{profile}} = "recreational"            │
│  5. Replace {{min}} = "0.400", {{max}} = "0.500"   │
│                                                      │
│  Result: "Tiempo de vuelo 0.600s fuera del rango..." │
└──────────────────────────────────────────────────────┘
                      │
                      ▼
┌────────────────────────────────────────────────┐
│  5. RENDERED UI                                │
│     (Browser Display)                          │
│                                                │
│  Validation Results                            │
│  ═════════════════════════════════════════    │
│  Status: PASS WITH WARNINGS                   │
│                                                │
│  ⚠️  flight_time: Tiempo de vuelo 0.600s     │
│     fuera del rango típico [0.400-0.500]s    │
│     para atleta recreational                  │
│                                                │
│  ℹ️  jump_height: Altura de salto 0.450m    │
│     dentro del rango esperado para            │
│     atleta recreational                       │
│                                                │
│  Athlete Profile: Recreational                │
└────────────────────────────────────────────────┘
```

## Component Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      KINEMOTION SYSTEM                          │
└─────────────────────────────────────────────────────────────────┘

BACKEND (Python/FastAPI)
├── src/kinemotion/core/
│   ├── validation.py
│   │   ├── ValidationIssue (dataclass)
│   │   │   ├─ severity: ValidationSeverity
│   │   │   ├─ metric: str
│   │   │   ├─ message: str (backward compat)
│   │   │   ├─ message_key: str | None (NEW)
│   │   │   ├─ context: dict | None (NEW)
│   │   │   ├─ value: float | None
│   │   │   └─ bounds: tuple[float, float] | None
│   │   │
│   │   └── ValidationResult (abstract)
│   │       ├─ add_error(metric, message, ..., message_key, context)
│   │       ├─ add_warning(metric, message, ..., message_key, context)
│   │       ├─ add_info(metric, message, ..., message_key, context)
│   │       └─ finalize_status()
│   │
│   └── [other core modules]
│
├── src/kinemotion/cmj/
│   ├── metrics_validator.py
│   │   ├── CMJMetricsValidator
│   │   │   ├─ validate(metrics) → CMJValidationResult
│   │   │   ├─ _check_flight_time(metrics, result, profile)
│   │   │   │  └─ result.add_info/warning/error(..., message_key=..., context=...)
│   │   │   ├─ _check_jump_height(metrics, result, profile)
│   │   │   ├─ _check_countermovement_depth(metrics, result, profile)
│   │   │   ├─ _check_rsi_validity(metrics, result)
│   │   │   ├─ _check_triple_extension(metrics, result, profile)
│   │   │   └─ [10 more validation methods]
│   │   │
│   │   └── CMJValidationResult(ValidationResult)
│   │       ├─ to_dict() → dict with all fields
│   │       ├─ rsi: float | None
│   │       ├─ height_flight_time_consistency: float | None
│   │       ├─ velocity_height_consistency: float | None
│   │       └─ [other CMJ-specific metrics]
│   │
│   └── api.py
│       └─ process_cmj_video(...) → CMJVideoResult
│          └─ metrics.validation_result = validator.validate(...)
│
├── src/kinemotion/dropjump/
│   ├── metrics_validator.py
│   │   ├── DropJumpMetricsValidator
│   │   │   ├─ validate(metrics) → DropJumpValidationResult
│   │   │   ├─ _check_contact_time(...)
│   │   │   ├─ _check_flight_time(...)
│   │   │   ├─ _check_jump_height(...)
│   │   │   ├─ _check_rsi(...)
│   │   │   └─ _check_dual_height_consistency(...)
│   │   │
│   │   └── DropJumpValidationResult(ValidationResult)
│   │       └─ to_dict() → dict with all fields
│   │
│   └── api.py
│       └─ process_dropjump_video(...) → DropJumpVideoResult

FRONTEND (React/TypeScript)
├── public/locales/
│   ├── en.json (English translations)
│   ├── es.json (Spanish translations)
│   ├── fr.json (French translations)
│   ├── de.json (German translations)
│   └── ja.json (Japanese translations)
│
├── src/i18n/
│   └── config.ts
│       ├─ Initialize i18next
│       ├─ Load all language files
│       ├─ Detect user language preference
│       └─ Export useTranslation() hook
│
└── src/components/
    └── ValidationIssue.tsx
        ├─ Receives: ValidationIssueData
        ├─ Uses: useTranslation() hook
        ├─ Renders translated message with context substitution
        └─ Fallback to message field if no message_key
```

## Message Key Resolution Flow

```
Frontend receives ValidationIssueData:
{
  message_key: "validation.flight_time.outside_range",
  context: {profile: "recreational", unit: "s", min: 0.4, max: 0.5}
}

         │
         ▼

i18next.t("validation.flight_time.outside_range", context)

         │
         ▼

Load from active language file (locales/es.json):
{
  "validation": {
    "flight_time": {
      "outside_range":
        "Tiempo de vuelo {{value}}{{unit}} fuera del rango típico
         [{{min}}-{{max}}]{{unit}} para {{profile}}"
    }
  }
}

         │
         ▼

Interpolate template variables:
- {{value}} → context.value → "0.600"
- {{unit}} → context.unit → "s"
- {{min}} → context.min → "0.400"
- {{max}} → context.max → "0.500"
- {{profile}} → context.profile → "recreational"

         │
         ▼

Final Message:
"Tiempo de vuelo 0.600s fuera del rango típico
 [0.400-0.500]s para recreational"

         │
         ▼

Render to DOM
```

## Message Key Namespace

```
validation (root namespace)
├── flight_time
│   ├── within_range (INFO)
│   ├── outside_range (WARNING)
│   ├── below_minimum (ERROR)
│   └── above_maximum (ERROR)
│
├── jump_height
│   ├── within_range (INFO)
│   ├── outside_range (WARNING)
│   ├── no_jump (ERROR)
│   └── above_maximum (ERROR)
│
├── countermovement_depth
│   ├── within_range (INFO)
│   ├── outside_range (WARNING)
│   └── insufficient (WARNING)
│
├── contact_time
│   ├── within_range (INFO)
│   ├── outside_range (WARNING)
│   ├── below_minimum (ERROR)
│   └── above_maximum (ERROR)
│
├── rsi
│   ├── valid (INFO)
│   ├── outlier (WARNING)
│   └── invalid_calculation (ERROR)
│
├── triple_extension
│   ├── normal (INFO)
│   ├── insufficient (WARNING)
│   └── compensatory (WARNING)
│
├── joint_angle
│   ├── normal (INFO)
│   ├── excessive (WARNING)
│   └── insufficient (WARNING)
│
├── consistency
│   ├── height_flight_time (INFO/WARNING)
│   ├── height_velocity (INFO/WARNING)
│   ├── contact_depth (INFO/WARNING)
│   └── dual_height (INFO/WARNING)
│
└── athlete_profile
    └── detected (INFO)
```

## Backward Compatibility Timeline

```
v0.59.x (Current)
├─ message: formatted string
├─ message_key: (not present)
└─ context: (not present)
    └─ Clients use: message field

v0.60.x (Transition - NEW)
├─ message: formatted string (kept)
├─ message_key: translation key (new)
└─ context: template vars (new)
    └─ Old clients: use message field
    └─ New clients: use message_key + context

v0.70.x (Future - optional cleanup)
├─ Option A: Keep message field indefinitely
├─ Option B: Remove message field (breaking change)
    └─ Forces all clients to migrate to message_key approach
```

## Language Auto-Detection Strategy

```
User opens frontend

    │
    ▼

1. Check localStorage['language']
   ├─ Found? Use it
   └─ Not found? Continue

    │
    ▼

2. Check URL params (?lang=es)
   ├─ Found? Use it & save to localStorage
   └─ Not found? Continue

    │
    ▼

3. Check HTTP Accept-Language header
   ├─ Found supported language? Use it
   └─ Not found? Continue

    │
    ▼

4. Check browser language (navigator.language)
   ├─ Found? Use it
   └─ Not found? Continue

    │
    ▼

5. Default to English (en)

    │
    ▼

Load translation file: locales/{lang}.json

    │
    ▼

Render UI with messages in selected language
```

## Testing Strategy Matrix

```
┌────────────────────────────────────────────────────────────────┐
│                    TESTING MATRIX                             │
├────────────────────────────────────────────────────────────────┤
│ Layer      │ Test Type          │ Coverage                    │
├────────────────────────────────────────────────────────────────┤
│ BACKEND    │ Unit Tests         │ message_key assignment      │
│            │                    │ context dict completeness   │
│            │                    │ serialization (to_dict)     │
│            │                    │                             │
│            │ Integration Tests  │ All validators updated      │
│            │                    │ All message_keys unique     │
│            │                    │ Pattern compliance          │
│            │                    │ NumPy type conversion       │
│            │                    │                             │
│ FRONTEND   │ Unit Tests         │ i18next initialization      │
│            │                    │ Language file loading       │
│            │                    │ Message key resolution      │
│            │                    │ Template interpolation      │
│            │                    │                             │
│            │ Component Tests    │ ValidationIssue rendering   │
│            │                    │ Fallback to message field   │
│            │                    │ Language switching          │
│            │                    │ Missing key handling        │
│            │                    │                             │
│            │ E2E Tests          │ Full video→analysis→UI      │
│            │                    │ Multiple languages          │
│            │                    │ Context substitution        │
│            │                    │ Number formatting (0.600)   │
│            │                    │                             │
│ TRANSLATION│ Completeness       │ All keys exist in all langs │
│            │                    │ All placeholders match      │
│            │                    │ No hardcoded languages      │
└────────────────────────────────────────────────────────────────┘
```
