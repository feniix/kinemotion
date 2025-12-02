---
title: Unused and Experimental Features Strategy
type: note
permalink: development/unused-and-experimental-features-strategy-1
tags:
- code-quality
- maintenance
- deprecation
- experimental
---

# Unused and Experimental Features Strategy

**Created**: December 2, 2025
**Status**: Active - use for marking features

## Purpose

Mark implemented features that aren't yet integrated into the main pipeline for:
- Easy identification during code reviews
- Future enhancement tracking
- Cleanup/removal decisions
- Documentation generation

## Implementation

### Custom Decorators

Created `src/kinemotion/core/experimental.py` with two decorators:

#### `@unused` - Implemented but Not Integrated

For features that work correctly but aren't called by the pipeline.

**Use when**:
- Feature awaits CLI integration
- Alternative implementation kept for future use
- Backward compatibility code

**Behavior**: No runtime warnings, just metadata for tracking

**Example**:
```python
@unused(
    reason="Not called by analysis pipeline - awaiting CLI integration",
    remove_in="1.0.0",
    since="0.34.0",
)
def calculate_adaptive_threshold(...):
    pass
```

#### `@experimental` - Unstable/Incomplete API

For features actively being developed or with unstable APIs.

**Use when**:
- API may change
- Needs more validation
- Early preview for testing

**Behavior**: Emits FutureWarning when called

**Example**:
```python
@experimental(
    reason="API may change",
    issue=123,
    since="0.35.0",
)
def new_feature(...):
    pass
```

### Finding Marked Features

Use `scripts/find_unused_features.py`:

```bash
uv run python scripts/find_unused_features.py
```

Output:
```
Found 1 marked features:

======================================================================
@unused Features (1)
======================================================================

📍 calculate_adaptive_threshold()
   File: dropjump/analysis.py:27
   Reason: Not called by analysis pipeline - awaiting CLI integration
   ⚠️  Remove in: v1.0.0

======================================================================
Summary:
  • @unused: 1
  • @experimental: 0
  • Total: 1
======================================================================
```

## Current Marked Features

### @unused (1)

1. **calculate_adaptive_threshold()** (`dropjump/analysis.py`)
   - Reason: Not called by analysis pipeline - awaiting CLI integration
   - Remove in: v1.0.0
   - Integration path: Add `--use-adaptive-threshold` CLI flag
   - Phase: Phase 2 (if users report video quality issues)

### @experimental (0)

None currently marked.

## Guidelines

### When to Use @unused

✅ **Use for**:
- Complete, tested implementations not yet in pipeline
- Features waiting for CLI parameters
- Alternative algorithms kept for comparison

❌ **Don't use for**:
- Broken/incomplete code (fix or remove it)
- Deprecated features (use Python's @deprecated instead when Python 3.13+)
- Dead code (just delete it)

### When to Use @experimental

✅ **Use for**:
- New features with unstable APIs
- Beta features for early testing
- Features needing more validation

❌ **Don't use for**:
- Production-ready stable features
- Internal helper functions (use _ prefix instead)
- Test-only code

### Metadata Fields

**Required**:
- `reason`: Why this is unused/experimental

**Optional**:
- `remove_in`: Version when feature might be removed if not integrated
- `issue`: GitHub issue number for tracking
- `since`: Version when decorator was added

## Future Migration

When Python 3.13+ becomes minimum version, migrate to built-in:

```python
from warnings import deprecated

@deprecated("Use new_function() instead")
def old_function():
    pass
```

## Integration Checklist

Before removing @unused decorator:

1. Add CLI parameter (if applicable)
2. Add to quality presets (if applicable)
3. Update user documentation
4. Add integration tests
5. Update CHANGELOG
6. Remove decorator
7. Run `find_unused_features.py` to verify

## See Also

- `docs/development/errors-findings.md` - Documents known unused features
- `scripts/find_unused_features.py` - Find all marked features
- PEP 702 - Type system deprecation marking (Python 3.13+)
