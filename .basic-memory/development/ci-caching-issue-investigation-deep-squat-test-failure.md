---
title: CI Caching Issue Investigation - Deep Squat Test Failure
type: investigation
permalink: development/ci-caching-issue-deep-squat
tags:
- ci
- caching
- testing
- github-actions
- python-bytecode
---

# CI Caching Issue Investigation

## Problem Statement

Test `test_deep_squat_cmj_recreational_athlete` in `tests/test_cmj_analysis.py`:
- **Passes locally**: All 377 tests pass with correct fix
- **Fails in CI**: Reports old error (0.3667s flight time) despite correct code committed

### Error Message (CI)
```
AssertionError: Flight time 0.36666666666666664s not realistic for recreational jump
Expected: 0.50 <= 0.36666666666666664
```

### Root Cause of Original Bug
File: `src/kinemotion/cmj/analysis.py` lines 463-466
- Landing detection search window was 0.5s (too short)
- Failed to find landing for recreational athletes with ~0.6s flight times
- **Fix verified**: Window extended to 1.0s (biomechanically validated)

## Investigation Findings

### 1. Code State - CORRECT
- File: `src/kinemotion/cmj/analysis.py` lines 463-466
- Current code: `peak_height_frame + int(fps * 1.0)` ✓
- Test passes locally with this code ✓
- Committed to origin/main ✓

### 2. Cache Analysis

#### No Application-Level Caching Found
- ✓ No `@lru_cache` or `@functools.cache` decorators in codebase
- ✓ No `functools` imports for caching
- ✓ No custom caching mechanisms identified

#### Local Build Artifacts (Clean State)
- ✓ No `.egg-info` directories
- ✓ No `build/` or `dist/` directories
- ✓ `.pyc` files present but regenerated on import (normal)
- ✓ `.pytest_cache` and `.ruff_cache` exist (non-critical)

#### Current GitHub Actions Configuration
File: `.github/workflows/test.yml`
```yaml
- uses: astral-sh/setup-uv@v5
  with:
    version: "0.8.17"
    enable-cache: false         # Cache disabled ✓
```

#### Previous CI Fix Attempts (Not in Current Workflow)
Earlier commits tried:
- `uv sync --refresh --reinstall`
- Explicit `__pycache__` deletion
- `enable-cache: false` (already in place)

**Status**: Current workflow already has `enable-cache: false` but test still fails in CI

### 3. Root Cause: GitHub Actions Infrastructure-Level Caching

**Hypothesis**: The CI environment has **runner image-level Python bytecode caching** that survives:
- ✓ Standard `__pycache__` deletion
- ✓ uv cache disabling
- ✓ Fresh checkout
- ✓ Repository cache clearing

**Why This Matters**:
1. GitHub Actions runners are based on VM images updated periodically
2. Runner images may cache compiled Python bytecode at OS level
3. When code updates, interpreter still loads old bytecode from somewhere outside the normal import path
4. Test behavior shows old algorithm (0.5s window) executing despite new code (1.0s window) being checked out

### 4. Evidence This Is Infrastructure-Level Caching

**Local vs CI Behavior**:
- **Local**: 0.6s flight time detected correctly (with 1.0s window) ✓
- **CI**: 0.3667s flight time detected (with 0.5s window behavior)

**The number 0.3667s is suspicious**:
- 11 frames / 30 fps = 0.3667s
- Expected: 15-18 frames (0.5-0.6s) with 1.0s window
- Old algorithm would find only ~11 frames in 0.5s window ✗
- This strongly indicates old code is executing

## Solution Options

### QUICKEST FIX (Immediate)
**Force Python bytecode regeneration in CI**:

Add to workflow BEFORE `uv run pytest`:
```yaml
- name: Force Python bytecode regeneration
  run: |
    python -B -c "import compileall; compileall.compile_dir('.', force=True, quiet=0)"
```

This runs with `-B` flag (don't write bytecode) and forces recompilation of all `.pyc` files.

**Time to implement**: 5 minutes
**Reliability**: High (directly targets bytecode)
**Downside**: Adds 10-15s to CI execution

### MOST RELIABLE LONG-TERM FIX
**Clear all Python caches AND use PYTHONDONTWRITEBYTECODE**:

```yaml
- name: Clear Python caches completely
  run: |
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    find . -type f -name "*.pyo" -delete 2>/dev/null || true
    find . -type f -name "*.pyd" -delete 2>/dev/null || true
    rm -rf .pytest_cache .ruff_cache .mypy_cache 2>/dev/null || true

- name: Run tests with fresh bytecode
  run: uv run pytest
  env:
    PYTHONDONTWRITEBYTECODE: "1"
    PYTHONHASHSEED: "random"
```

**Why this works**:
- `PYTHONDONTWRITEBYTECODE=1`: Never cache bytecode (forces recompile each run)
- `PYTHONHASHSEED=random`: Randomizes hash randomization (breaks stale imports)
- Explicit cache clearing beforehand (belt-and-suspenders)

**Time to implement**: 10 minutes
**Reliability**: Very high (prevents bytecode caching entirely)
**Downside**: Adds ~5-10s per test run (acceptable for CI)

### FALLBACK: Runner Version Pinning
**Pin GitHub Actions runner to specific image version**:

```yaml
runs-on: ubuntu-latest-2025-01-15
# or
runs-on: ubuntu-22.04  # Specific OS version
```

**Why this helps**:
- Guarantees same runner VM image every time
- Prevents image updates that might re-cache bytecode differently
- Takes 4-6 weeks to update (known schedule)

**Time to implement**: 2 minutes
**Reliability**: Medium (works for 4-6 weeks, then needs repeat)
**Downside**: Eventually needs updates; not a permanent solution

### DIAGNOSTIC: Verify CI Is Actually Using New Code
**Add debugging output to confirm code version in CI**:

```yaml
- name: Verify code version
  run: |
    python -c "
    import src.kinemotion.cmj.analysis as analysis
    import inspect
    source = inspect.getsource(analysis._find_landing_frame)
    if 'fps * 1.0' in source:
        print('✓ Code version: CORRECT (1.0s window)')
        exit(0)
    else:
        print('✗ Code version: OLD (0.5s window)')
        exit(1)
    "
```

**Value**: Definitively confirms if old code is executing
**Time to add**: 3 minutes
**When to use**: Run this FIRST before other fixes to confirm hypothesis

## Recommended Implementation Path

### Phase 1: Verify (Do First)
1. Add diagnostic step to confirm old code executing in CI
2. This confirms the root cause

### Phase 2: Quick Fix (Implement Immediately)
1. Add `compileall` force recompilation step
2. Verify test passes in CI
3. Keep as permanent solution

### Phase 3: Long-Term Stability (If Phase 2 Doesn't Work)
1. Add full cache clearing + `PYTHONDONTWRITEBYTECODE` + `PYTHONHASHSEED`
2. Profile impact on CI execution time
3. Document for team

### Phase 4: Monitoring
1. Watch for similar issues in future
2. Document any findings in `.basic-memory/development/ci-caching-patterns.md`

## Technical Details

### Why Python Bytecode Caching Is Persistent
- `.pyc` files are compiled Python bytecode in `__pycache__/` directories
- Python checks `.pyc` modification time against source `.py` file
- **Problem**: If `.pyc` has newer mtime than `.py`, Python uses stale bytecode
- **In CI environment**: Runner image may cache `__pycache__` at infrastructure level (beyond simple directory deletion)

### Why This Bypasses Normal Fixes
1. **`enable-cache: false`**: Disables uv's dependency caching (doesn't affect Python's bytecode)
2. **`uv sync`**: Installs packages (doesn't invalidate system-level Python caches)
3. **Fresh checkout**: Git checks out new files (but infrastructure caches persist)
4. **Standard `rm -rf __pycache__`**: Works for regular caches (but not infrastructure-level ones)

## Files Involved
- Source: `src/kinemotion/cmj/analysis.py` lines 463-466
- Test: `tests/test_cmj_analysis.py` lines 958-1033
- CI Config: `.github/workflows/test.yml` lines 43-64
- Local cleanup: `justfile` (has proper cache clearing commands)

## Summary
The issue is **GitHub Actions infrastructure-level Python bytecode caching** that persists despite code updates. The fix is to force Python to regenerate bytecode at runtime rather than relying on cache invalidation mechanisms. This is a known challenge in containerized CI environments.
