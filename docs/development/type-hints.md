# Modern Type Hints Guide

Guide to using modern Python type hints with NumPy 2.x compatibility.

## Overview

The Kinemotion project uses Python 3.10+ type hints with NumPy 2.x-compatible patterns for better IDE support, type checking, and code documentation.

## TypedDict for Type-Safe Dictionaries

Use TypedDict to create type-safe dictionary returns with IDE autocomplete and type checking.

### Example: Metrics Dictionary

**Before (generic dict):**

```python
def to_dict(self) -> dict:  # Too generic, no autocomplete
    return {
        "ground_contact_time_ms": ...,
        "flight_time_ms": ...,
    }
```

**After (TypedDict):**

```python
from typing import TypedDict

class DropJumpMetricsDict(TypedDict, total=False):
    """Type-safe dictionary for drop jump metrics JSON output."""
    ground_contact_time_ms: float | None
    flight_time_ms: float | None
    jump_height_m: float | None
    contact_start_frame: int | None
    # ... other fields

class DropJumpMetrics:
    def to_dict(self) -> DropJumpMetricsDict:  # ✨ Type-safe!
        """Convert metrics to dictionary for JSON output."""
        return {
            "ground_contact_time_ms": round(self.ground_contact_time * 1000, 2),
            # IDE will autocomplete keys and catch typos!
        }
```

**Benefits:**

- IDE autocomplete for dictionary keys
- Catch typos at edit time: `"flight_tim_ms"` → Type error
- Self-documenting structure
- Type checker validates all keys

### When to Use TypedDict

✅ **Use for:**

- Public API return values
- JSON serialization
- Configuration dictionaries
- Complex nested structures

❌ **Don't use for:**

- Simple internal dictionaries
- Dynamic key dictionaries
- When keys aren't known at type-check time

## Type Aliases for Complex Types

Simplify complex nested type signatures using type aliases.

### Example: Landmark Sequences

**Before (complex and repetitive):**

```python
def smooth_landmarks(
    landmark_sequence: list[dict[str, tuple[float, float, float]] | None],
    window_length: int = 5,
) -> list[dict[str, tuple[float, float, float]] | None]:
    """Smooth landmark trajectories."""
    ...
```

**After (type aliases):**

```python
from typing import TypeAlias

# Define once at module level
LandmarkCoord: TypeAlias = tuple[float, float, float]  # (x, y, visibility)
LandmarkFrame: TypeAlias = dict[str, LandmarkCoord] | None
LandmarkSequence: TypeAlias = list[LandmarkFrame]

def smooth_landmarks(
    landmark_sequence: LandmarkSequence,  # ✨ Much cleaner!
    window_length: int = 5,
) -> LandmarkSequence:
    """Smooth landmark trajectories."""
    ...
```

**Benefits:**

- Much more readable function signatures
- Reusable across module
- Self-documenting (name explains structure)
- Single point of update if structure changes

### When to Use Type Aliases

✅ **Use for:**

- Complex nested types used multiple times
- Domain-specific types (LandmarkSequence, PhaseInfo)
- Types that need descriptive names
- Generic patterns used throughout module

❌ **Don't use for:**

- Simple types used once
- Standard library types (list, dict, tuple)
- When the full type is clearer than the alias

## NDArray with Dtype Specificity

Use `numpy.typing.NDArray` to specify array dtypes for better type checking.

### Example: Explicit Dtype Hints

**Generic (acceptable):**

```python
import numpy as np

def calculate_metrics(positions: np.ndarray) -> float:
    """Calculate from positions."""
    ...
```

**Explicit dtype (better for public API):**

```python
import numpy as np
from numpy.typing import NDArray

def calculate_metrics(
    positions: NDArray[np.float64],  # Explicit dtype
    velocities: NDArray[np.float64],
) -> CMJMetrics:
    """Calculate CMJ metrics from position and velocity arrays.

    Args:
        positions: Vertical positions (float64 array)
        velocities: Vertical velocities (float64 array)

    Returns:
        CMJ metrics object
    """
    ...
```

### When to Use NDArray\[dtype\]

✅ **Use for:**

- Public API functions
- When dtype matters for algorithm correctness
- Documentation purposes (clarify expected dtype)
- Arrays passed between modules

✅ **Keep generic (np.ndarray) for:**

- Internal helper functions
- When any dtype is acceptable
- Temporary/intermediate arrays

### NumPy 2.x Benefits

NumPy 2.x provides default type parameters:

- `np.ndarray` now defaults to `NDArray[Any]` (no warnings)
- Cleaner type hints without explicit parameters
- Better IDE support

## Union Types (Modern Syntax)

Use Python 3.10+ union syntax with `|` operator.

**Modern:**

```python
def process(value: int | None = None) -> str | None:
    ...
```

**Old (avoid):**

```python
from typing import Optional, Union

def process(value: Optional[int] = None) -> Union[str, None]:
    ...
```

## Complete Example

Here's a complete module showing all patterns together:

```python
"""Example module with modern type hints."""

from typing import TypeAlias, TypedDict

import numpy as np
from numpy.typing import NDArray

# Type aliases for complex structures
LandmarkCoord: TypeAlias = tuple[float, float, float]
LandmarkFrame: TypeAlias = dict[str, LandmarkCoord] | None
LandmarkSequence: TypeAlias = list[LandmarkFrame]


class MetricsDict(TypedDict, total=False):
    """Type-safe metrics dictionary."""

    value_ms: float | None
    count: int | None


class Metrics:
    """Example metrics class."""

    def __init__(self) -> None:
        self.value: float | None = None
        self.count: int | None = None

    def to_dict(self) -> MetricsDict:
        """Convert to dictionary."""
        return {
            "value_ms": round(self.value * 1000, 2) if self.value else None,
            "count": int(self.count) if self.count else None,
        }


def process_landmarks(
    landmarks: LandmarkSequence,  # Type alias
    positions: NDArray[np.float64],  # Explicit dtype
) -> Metrics:
    """Process landmarks and positions.

    Args:
        landmarks: Sequence of landmark frames
        positions: Array of vertical positions (float64)

    Returns:
        Metrics object with results
    """
    ...
```

## Type Checking

All code must pass Pyright strict mode:

```bash
uv run pyright
```

**Configuration** (`pyproject.toml`):

```toml
[tool.pyright]
include = ["src"]
pythonVersion = "3.10"
typeCheckingMode = "strict"
```

## Best Practices Summary

1. **Use TypedDict** for dictionary returns (JSON, config)
1. **Use type aliases** for complex nested types
1. **Use NDArray\[dtype\]** when dtype matters
1. **Use modern syntax** (`|` for unions)
1. **Convert NumPy types** in `to_dict()`: `int()`, `float()`
1. **Handle None** in optional fields explicitly
1. **Type all functions** (strict mode enforced)

See individual module files for implementation examples:

- `dropjump/kinematics.py` - TypedDict for metrics
- `cmj/kinematics.py` - TypedDict for CMJ metrics
- `core/smoothing.py` - Type aliases for landmark types
