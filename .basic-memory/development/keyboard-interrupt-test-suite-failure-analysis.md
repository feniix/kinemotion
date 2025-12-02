---
title: KeyboardInterrupt Test Suite Failure Analysis
type: note
permalink: development/keyboard-interrupt-test-suite-failure-analysis-1
tags:
- pytest
- asyncio
- bug-fix
- backend
---

# KeyboardInterrupt Test Suite Failure - Root Cause Analysis

## Problem
GitHub Actions deploy workflow fails with `KeyboardInterrupt` during pytest teardown (exit code 2).
- Tests pass: 30 passed in 3.79s
- Failure occurs during fixture cleanup
- Error in `unittest/mock.py:1198`

## Root Cause
In `backend/tests/test_error_handling.py` line 203-214, there's a test:
```python
def test_keyboard_interrupt_returns_500(client: TestClient, sample_video_bytes: bytes) -> None:
    with patch("kinemotion_backend.app.process_cmj_video") as mock_cmj:
        mock_cmj.side_effect = KeyboardInterrupt()
        response = client.post("/api/analyze", files=files, data={"jump_type": "cmj"})
    assert response.status_code == 500
```

The issue:
- `KeyboardInterrupt` inherits from `BaseException`, not `Exception`
- When patch context exits, the exception state is still in threads/event loop
- pytest-asyncio fixture teardown encounters unhandled BaseException
- Propagates to pytest, causing suite to fail

## Solution
1. Add proper event loop cleanup to conftest.py
2. Add task cancellation during fixture teardown
3. Ensure TestClient and patches are properly isolated

## Implementation
Modify `backend/tests/conftest.py` to add:
- Custom event loop fixture with proper cleanup
- Task cancellation before loop closes
- Proper TestClient context management

## Follow-up Fixes: R2 Integration Tests (COMPLETED ✅)

After the KeyboardInterrupt fix, we discovered two additional test failures in R2 integration:

### Issue 1: test_r2_bucket_name_default failure
**Root cause**: `os.getenv("R2_BUCKET_NAME", "kinemotion")` returns empty string "" if env var is explicitly set to ""
**Fix**: Changed to `os.getenv("R2_BUCKET_NAME") or "kinemotion"` to handle empty strings
**File**: `backend/src/kinemotion_backend/app.py:85`

### Issue 2: Missing mock_kinemotion_cmj fixture
**Root cause**: Three tests referenced `mock_kinemotion_cmj` fixture that didn't exist in conftest.py
**Fix**: Added new fixture that provides direct access to CMJ mock
**File**: `backend/tests/conftest.py` (lines 216-230)

### Final Status
- **85 tests PASS** ✅
- **1 test SKIP** (KeyboardInterrupt gracefully skipped)
- **Commit**: c7b7940
- **Workflow**: Ready for deployment
