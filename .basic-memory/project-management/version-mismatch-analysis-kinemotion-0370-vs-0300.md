---
title: 'Version Mismatch Analysis: kinemotion 0.37.0 vs 0.30.0'
type: note
permalink: project-management/version-mismatch-analysis-kinemotion-0-37-0-vs-0-30-0
---

# Version Mismatch Analysis: kinemotion 0.37.0 vs 0.30.0

## Problem Summary

**Critical Determinism Issue**: 9% RSI difference between M1 local and Intel Cloud Run due to version mismatch

- **M1 Local**: kinemotion v0.37.0 (source) → RSI = 3.72
- **Intel Cloud Run**: kinemotion v0.30.0 (backend lock) → RSI = 4.06
- **Impact**: Same video produces different results on different platforms

## Root Cause: Workspace Configuration Issue

### Current Setup (INCORRECT)

**Root `pyproject.toml` (lines 199-204):**
```toml
[tool.uv.workspace]
members = [".", "backend"]

[tool.uv.sources]
# Use workspace member for local development
kinemotion = { workspace = true }
```

**Backend `pyproject.toml` (line 35):**
```toml
"kinemotion>=0.35.1",
```

### The Problem

1. **Root workspace**: Correctly defines `kinemotion` as editable workspace member
2. **Root uv.lock**: Correctly locks kinemotion v0.37.0 (editable = ".")
3. **Backend uv.lock**: LOCKED to kinemotion v0.30.0 from PyPI registry
4. **Why**: Backend has its OWN `uv.lock` file that doesn't inherit workspace configuration

### Why This Happens

- **uv workspace**: Each member can have its own lock file OR share parent lock
- **Backend situation**: Backend has independent `uv.lock` that:
  - Doesn't recognize workspace membership
  - Resolves `kinemotion>=0.35.1` from PyPI (finds v0.30.0)
  - Gets locked to old version permanently

## Correct Approaches

### Option 1: Shared Workspace Lock (Recommended for Monorepo)

**Advantage**: One lock file, always in sync, simplest to manage

**Implementation:**
1. Delete `backend/uv.lock`
2. Run `uv sync` from root
3. Root `uv.lock` becomes source of truth for entire workspace

**Root uv.lock** will contain:
- kinemotion v0.37.0 (editable, from source)
- Backend dependencies with kinemotion v0.37.0

### Option 2: Separate Locks with Exact Version Pin (For Production Backend)

**Advantage**: Backend can pin exact versions independently

**Implementation:**
1. Update `backend/pyproject.toml`:
   ```toml
   "kinemotion==0.37.0",  # Exact match instead of >=0.35.1
   ```
2. Run `uv lock --directory backend` to regenerate backend lock
3. Backend lock freezes to exact version

**Tradeoff**: Must manually update backend version when releasing kinemotion

### Option 3: Docker Production + Local Workspace (Current Intent)

**Current comments in backend/pyproject.toml** suggest this was the intended design:
```python
# Local development: use editable install via `uv sync`
# Production deployment: use released package from PyPI
```

**Implementation:**
1. Keep workspace setup for local development (root uv.lock)
2. Backend Docker uses released kinemotion from PyPI
3. Dockerfile can pin exact version: `kinemotion==0.37.0`

## Recommended Fix for Determinism

**For cross-platform reproducibility:**

1. **Use Option 1 (Shared Workspace Lock)**:
   - Delete `backend/uv.lock`
   - Run: `uv sync` from root
   - Both local dev and backend lock file use v0.37.0

2. **For Cloud Run deployment**:
   - Dockerfile installs from workspace-generated lock
   - OR pin exact version: `kinemotion==0.37.0`
   - Rebuild Docker image to pick up new lock

3. **Verify**:
   ```bash
   # Both should show 0.37.0
   grep -A 1 'name = "kinemotion"' uv.lock
   grep -A 1 'name = "kinemotion"' backend/uv.lock  # Should not exist
   ```

## Files Involved

| File | Current | Status |
|------|---------|--------|
| `pyproject.toml` | v0.37.0 | Correct |
| `uv.lock` | v0.37.0 (editable) | Correct |
| `backend/pyproject.toml` | >=0.35.1 | Outdated |
| `backend/uv.lock` | v0.30.0 | OUTDATED - Root cause |

## Commands to Fix

### Quick Fix (Option 1):
```bash
cd /Users/feniix/src/personal/cursor/kinemotion

# Remove stale backend lock
rm backend/uv.lock

# Regenerate from root workspace
uv sync

# Verify both point to 0.37.0
grep -A 1 'name = "kinemotion"' uv.lock
grep -A 1 'name = "kinemotion"' backend/uv.lock  # Should be workspace reference
```

### Update Pin (Option 2):
```bash
# Update backend to pin exact version
# Edit backend/pyproject.toml line 35: "kinemotion==0.37.0"
# Then regenerate backend lock only:

uv lock --directory backend
```

## Impact

**Fixing this ensures:**
- M1 local → RSI = 3.72 (v0.37.0)
- Intel Cloud Run → RSI = 3.72 (v0.37.0)
- Same video produces identical results regardless of platform
- Determinism achieved through version parity
