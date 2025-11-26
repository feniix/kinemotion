# Code Style & Conventions for Kinemotion

## Type Hints

- **Required**: All functions must have type hints (Pyright strict mode)
- **Use**: TypedDict for structured data, type aliases for clarity, NDArray\[dtype\] for NumPy
- **Pattern**: Function signatures include parameter and return type hints
  ```python
  def calculate_jump_height(flight_time: float, gravity: float = 9.81) -> float:
      """Calculate jump height from flight time."""
      return gravity * (flight_time / 2) ** 2
  ```

## Naming Conventions

- **Functions/Variables**: snake_case (e.g., `process_video`, `contact_time`)
- **Classes**: PascalCase (e.g., `DropJumpAnalyzer`, `CMJPhaseDetector`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `DEFAULT_QUALITY_PRESET`, `GRAVITY_CONSTANT`)
- **Private**: Prefix with underscore (e.g., `_internal_helper`)

## Docstrings

- **Format**: Google-style docstrings
- **Include**: Description, Args, Returns, Raises sections
  ```python
  def detect_takeoff(poses: NDArray) -> tuple[int, float]:
      """Detect takeoff frame and velocity from pose sequence.

      Args:
          poses: Array of joint positions (N, 17, 3)

      Returns:
          Tuple of (takeoff_frame, takeoff_velocity)

      Raises:
          ValueError: If poses array is invalid
      """
  ```

## Code Style

- **Line Length**: 100 characters (enforced by Ruff)
- **Formatting**: Black-compatible (via Ruff)
- **Indentation**: 4 spaces
- **Imports**: Organized alphabetically within groups (standard library, third-party, local)

## Key Patterns

1. **Shared Logic**: Extract to core/ modules (pose.py, filtering.py, etc.)
1. **Inheritance**: Use for shared behavior across jump types
1. **Helper Functions**: Create testable, reusable functions
1. **Function Composition**: Pass functions as parameters for flexibility
1. **Type Aliases**: Define at module level for complex types

```python
FrameIndex = int
PoseArray = NDArray[np.float32]  # (N, 17, 3)
MetricsDict = TypedDict("MetricsDict", {"height": float, "contact_time": float})
```

## Video Processing Gotchas

- **Read first frame** for dimensions (not OpenCV properties)
- **Handle rotation metadata** for mobile videos
- **Convert NumPy types** for JSON serialization (use `int()`, `float()`)

## CMJ-Specific Patterns

- **Use signed velocity** (not absolute magnitude)
- **Backward search** algorithm (find peak first, then search backward)
- **Lateral view** required for accurate analysis

## Drop Jump-Specific Patterns

- **Forward search** algorithm (search from ground contact)
- **Absolute velocity** magnitude

## Testing Patterns

- **Test organization**: tests/ mirror src/ structure
- **Fixtures**: Use pytest fixtures for common test data
- **Mocking**: Mock video I/O and external dependencies
- **Edge cases**: Test boundary conditions and error cases
- **Coverage**: Aim for >70% overall, >85% for core algorithms

## Commit Format (Conventional Commits)

```
<type>(<scope>): <description>

<body (optional)>
<footer (optional)>
```

**Types** (determines version bump):

- `feat`: New feature → minor version bump (0.x.0)
- `fix`: Bug fix → patch version bump (0.0.x)
- `perf`: Performance improvement → patch
- `docs`, `test`, `refactor`, `chore`, `style`, `ci`, `build` → no version bump

**Examples**:

- `feat: add real-time CMJ analysis streaming`
- `fix: correct takeoff detection in backward search`
- `test: add edge case tests for low countermovement`
- `docs: add triple extension biomechanics guide`
- `refactor: extract signed velocity calculation`

**Important**: Never reference Claude or AI assistance in commit messages. Keep professional and technical.

## Quality Gates Before Commit

```bash
uv run ruff check --fix       # Auto-fix linting issues
uv run pyright               # Type check (strict mode)
uv run pytest                # All 261 tests with coverage
```

Ensure:

- All tests pass
- No type errors
- No linting errors
- Coverage ≥74% (maintain current level)
- Code duplication \<3%
