---
title: Structured Logging Implementation
type: note
permalink: development/structured-logging-implementation-1
tags:
- logging
- structlog
- monitoring
- production
---

## Structured Logging Implementation

### Overview
Production-ready structured logging using `structlog` to replace all `print()` statements in backend.

### Dependencies
- `structlog>=24.1.0` added to backend/pyproject.toml
- `httpx>=0.27.0` for Auth server verification

### New Modules
- **`logging_config.py`**: Configures structlog (JSON/human-readable)
- **`middleware.py`**: Request tracking with automatic request ID
- **`auth.py`**: Supabase JWT validation

### Features
- Request ID tracking (UUID per request)
- Context variables: method, path, client_ip, user_id, user_email
- JSON logs (production) or colored logs (development)
- Duration tracking (milliseconds)
- X-Request-ID header in responses

### Configuration

**Development:**
```
LOG_LEVEL=INFO
JSON_LOGS=false
```

**Production (Cloud Run):**
```
LOG_LEVEL=INFO
JSON_LOGS=true
```

### Example Logs

**Production (JSON):**
```json
{
  \"event\": \"request_started\",
  \"request_id\": \"abc123\",
  \"user_id\": \"user-uuid\",
  \"user_email\": \"coach@example.com\",
  \"method\": \"POST\",
  \"path\": \"/api/analyze\"
}
```

### Log Events
- `request_started`, `request_completed`, `request_failed`
- `user_authenticated`, `auth_token_invalid`
- `video_analysis_completed`, `video_analysis_failed`
- `video_uploaded_to_r2`, `results_uploaded_to_r2`

### User ID Integration
Middleware automatically extracts user ID from Supabase JWT and binds to logging context. All logs include user_id and user_email.

### Testing
- 85 tests pass
- 0 type errors (pyright strict)
- 0 linting errors (ruff)
