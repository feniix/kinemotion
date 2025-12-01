---
title: KeyboardInterrupt Test Suite Failure Analysis
type: note
permalink: development/keyboard-interrupt-test-suite-failure-analysis
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
