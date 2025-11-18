---
title: CI vs Local Test Failure Investigation
type: note
permalink: development/ci-vs-local-test-failure-investigation
---

# CI vs Local Test Failure Investigation

## Issue Summary
- **Test**: `test_deep_squat_cmj_recreational_athlete`
- **Status**: PASSES locally with fix, FAILS in GitHub Actions CI
- **Symptom**: Landing frame detected as frame 11 (~0.3667s) instead of frame 18 (~0.6s)
- **Expected flight time**: 0.5-0.75s
- **Actual in CI**: ~0.3667s (11 frames at 30fps)

## Root Cause Hypothesis
The test failure error message matches the UNFIXED version of the code (0.5s window), suggesting:
1. CI is running an older version of analysis.py
2. Or the compiled .pyc cache in CI contains the old code
3. Or the fix commit hasn't been picked up by the CI workflow

## Investigation Steps

### Commit Status (VERIFIED)
- Fix commit: c4a6e7b (Nov 17 23:50:35)
- Change: `fps * 0.5` → `fps * 1.0` at line 466
- Status in origin/main: ✓ PRESENT
- Status locally: ✓ PRESENT (line 466 verified)

### Local Test Status (VERIFIED)
- Test runs: PASSES
- Code verified: Line 466 has `fps * 1.0`
- Coverage: 13.70% (single test run)

### CI Workflow File
- Location: `.github/workflows/test.yml`
- uv version: 0.8.17 (specified)
- uv cache: enabled
- Python: 3.12

## Potential Issues to Investigate

### 1. GitHub Actions Workflow Cache Issue
**Problem**: The `setup-uv@v5` action enables caching with `enable-cache: true`
**Symptoms**:
- CI runs old version of code
- `uv sync` doesn't properly update cached dependencies
- Virtual environment has stale .pyc files

**Solution Needed**:
- Add cache invalidation to workflow
- Or run `uv sync --refresh` instead of `uv sync`
- Or disable cache and force clean install

### 2. Commit/Branch Issue
**Problem**: CI might be running on wrong commit or branch
**Check**:
- Verify PR head commit vs main
- Verify workflow is triggered on the right branch
- Check GitHub Actions run logs for actual commit SHA

### 3. Python Package Cache
**Problem**: .pyc bytecode compiled from old source
**Solution**:
- Add `uv cache clean` to workflow before `uv sync`
- Or delete pytest cache: `find . -type d -name __pycache__ -exec rm -rf {} +`

## Recommended Fix
Add cache invalidation to `.github/workflows/test.yml` at line 50:

```yaml
- name: Install dependencies
  run: |
    uv cache clean
    uv sync --refresh
```

Or alternatively (simpler):
```yaml
- name: Clean cache before install
  run: |
    rm -rf .pytest_cache
    find . -type d -name __pycache__ -exec rm -rf {} +

- name: Install dependencies
  run: uv sync
```

## Files to Check
1. `.github/workflows/test.yml` - CI workflow definition
2. `src/kinemotion/cmj/analysis.py` - Verify line 466 on origin/main
3. GitHub Actions run logs - Check which commit and SHA are being tested

## Next Steps
1. Check if workflow has pending/stale cache
2. Run workflow with cache disabled
3. Force push to main to trigger new workflow run
4. Or manually clear GitHub Actions cache via Settings
