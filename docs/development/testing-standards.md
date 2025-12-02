# Testing Standards

**Last Updated**: December 2, 2025
**Status**: Active reference for test creation and review

______________________________________________________________________

## Test File Organization

### Naming Convention

**Rule**: Test files MUST mirror source module structure.

| Source Module                           | Test File                           | Status     |
| --------------------------------------- | ----------------------------------- | ---------- |
| `src/kinemotion/core/pose.py`           | `tests/core/test_pose.py`           | ✅ Correct |
| `src/kinemotion/cmj/analysis.py`        | `tests/cmj/test_analysis.py`        | ✅ Correct |
| `src/kinemotion/dropjump/kinematics.py` | `tests/dropjump/test_kinematics.py` | ✅ Correct |

**Bad Examples**:

- ❌ `test_com_estimation.py` - Function-focused, should be `test_pose.py`
- ❌ `test_adaptive_threshold.py` in wrong directory

### When to Use Descriptive Suffixes

For extensive feature testing, use: `test_{module}_{feature}.py`

Examples:

- `test_video_io_rotation.py` - If rotation tests are extensive
- `test_smoothing_polyorder.py` - If polyorder tests are extensive

**Default**: Keep tests in main module file unless >100 lines devoted to one feature.

______________________________________________________________________

## Test Function Naming

### Format

```python
def test_{what}_{condition}_{expected}() -> None:
    """Docstring explaining biomechanical/technical context."""
```

### Good Examples ✅

```python
def test_phase_progression_ordering_valid_cmj() -> None:
    """Test phase progression validation: verify phases occur in correct order."""

def test_velocity_calculation_with_empty_array() -> None:
    """Test velocity calculation handles empty array gracefully."""

def test_batch_continues_after_single_video_error() -> None:
    """Test batch mode continues processing after error."""
```

### Bad Examples ❌

```python
def test_1() -> None:  # ❌ Meaningless name

def test_velocity() -> None:  # ❌ Too vague

def test_the_system_should_validate_metrics_correctly() -> None:  # ❌ Too verbose
```

______________________________________________________________________

## Test Organization Patterns

### Function-Based (Default)

Use for most unit and integration tests:

```python
def test_compute_velocity_normal_case() -> None:
    """Test velocity computation with normal input."""
    # Arrange
    positions = np.array([0.0, 1.0, 2.0])

    # Act
    velocities = compute_velocity(positions, dt=0.1)

    # Assert
    assert len(velocities) == len(positions)
```

### Class-Based (Scenarios)

Use for grouping related test scenarios (especially CLI/API tests):

```python
class TestCMJCLIErrors:
    """Test error handling scenarios."""

    def test_missing_video_file_fails(self, cli_runner) -> None:
        """Test command fails for nonexistent video."""
        result = cli_runner.invoke(cmj_analyze, ["nonexistent.mp4"])
        assert result.exit_code != 0

    def test_invalid_quality_preset_fails(self, cli_runner) -> None:
        """Test invalid quality preset is rejected."""
        result = cli_runner.invoke(cmj_analyze, ["video.mp4", "--quality", "invalid"])
        assert result.exit_code != 0
```

**When to use classes**:

- CLI command testing (group by: help, errors, file operations, options)
- API endpoint testing (group by: authentication, validation, success cases)
- Multiple tests sharing complex setup fixtures

______________________________________________________________________

## Test Structure (AAA Pattern)

### Template

```python
def test_feature_description() -> None:
    """One-line description of what is tested.

    Optional: Extended context about why this matters biomechanically
    or technically. Include constraints, expected ranges, or edge cases.
    """
    # Arrange: Set up test data and preconditions
    input_data = create_test_data()
    expected_output = calculate_expected()

    # Act: Execute the function under test
    result = function_under_test(input_data)

    # Assert: Verify results meet expectations
    assert result == expected_output
    assert additional_property_check()
```

### Good Example from Codebase

```python
def test_phase_progression_temporal_constraints() -> None:
    """Test temporal constraints between CMJ phases are physically plausible.

    Biomechanical context: CMJ phases must satisfy time constraints:
    - Eccentric (squat down): typically 0.3-0.8s (9-24 frames at 30fps)
    - Concentric (push up): typically 0.2-0.5s (6-15 frames at 30fps)
    - Flight (airborne): typically 0.3-1.0s (9-30 frames at 30fps)

    If constraints violated, detection or biomechanics is wrong.
    """
    # Arrange: Create CMJ with controlled phase durations
    fps = 30.0
    positions = np.concatenate([
        np.ones(20) * 1.0,        # Standing: 0.67s
        np.linspace(1.0, 1.4, 30),  # Eccentric: 1.0s
        np.linspace(1.4, 0.6, 20),  # Concentric: 0.67s
        np.linspace(0.6, 0.0, 20),  # Flight: 0.67s
    ])

    # Act: Detect phases
    result = detect_cmj_phases(positions, fps)

    # Assert: Verify temporal constraints
    assert result is not None
    standing, lowest, takeoff, landing = result
    contact_time = (takeoff - lowest) / fps
    assert 0.40 <= contact_time <= 0.75
```

______________________________________________________________________

## Test Types and Markers

### Available Markers

All markers are configured in `pyproject.toml` under `[tool.pytest.ini_options]`:

```python
import pytest

# Module-level markers (apply to all tests in file)
pytestmark = [pytest.mark.unit, pytest.mark.core]

# Or individual test markers
@pytest.mark.unit
def test_velocity_calculation() -> None:
    """Fast, isolated function test."""
    pass

@pytest.mark.integration
@pytest.mark.cmj
def test_cmj_full_pipeline() -> None:
    """Multiple components working together."""
    pass

@pytest.mark.integration
@pytest.mark.cli
@pytest.mark.requires_video
def test_cli_video_processing() -> None:
    """Complete workflow from video to output."""
    pass
```

### Marker Definitions

| Marker           | Purpose                               | Speed  | Example                    |
| ---------------- | ------------------------------------- | ------ | -------------------------- |
| `unit`           | Fast, isolated, no external deps      | \<1s   | `test_compute_velocity()`  |
| `integration`    | Multiple components, may use fixtures | 1-10s  | `test_detect_cmj_phases()` |
| `slow`           | Tests that take >1 second             | >1s    | Long video processing      |
| `requires_video` | Needs video file fixtures             | Varies | CLI/API tests              |
| `core`           | Tests for core/ module                | Varies | `tests/core/test_*.py`     |
| `cmj`            | Tests for CMJ analysis                | Varies | `tests/cmj/test_*.py`      |
| `dropjump`       | Tests for drop jump analysis          | Varies | `tests/dropjump/test_*.py` |
| `cli`            | Tests for CLI interface               | Varies | `tests/cli/test_*.py`      |
| `validation`     | Tests for validation logic            | \<1s   | `test_validation.py`       |

### Running Tests by Marker

```bash
# Fast unit tests during development
uv run pytest -m unit

# Integration tests before commit
uv run pytest -m "unit or integration"

# Skip slow tests
uv run pytest -m "not slow"

# Only CMJ tests
uv run pytest -m cmj

# Core unit tests only
uv run pytest -m "core and unit"

# Run everything
uv run pytest
```

### When to Use Each Marker

**Primary Markers** (choose one):

- `unit`: Pure function tests, no I/O, no fixtures beyond simple data
- `integration`: Multiple modules working together, uses fixtures like video data

**Secondary Markers** (add as appropriate):

- `slow`: If test takes >1 second
- `requires_video`: If test needs video file fixtures
- Module markers (`core`, `cmj`, `dropjump`, `cli`): Always add to match directory
- `validation`: For validation infrastructure tests

**Example Combinations**:

```python
# Core unit test for validation
pytestmark = [pytest.mark.unit, pytest.mark.core, pytest.mark.validation]

# CMJ integration test that uses video
pytestmark = [pytest.mark.integration, pytest.mark.cmj, pytest.mark.requires_video]

# Slow CLI integration test
pytestmark = [pytest.mark.integration, pytest.mark.cli, pytest.mark.slow, pytest.mark.requires_video]
```

______________________________________________________________________

## Edge Cases to Test

### Always Test These

1. **Empty/Null**

   ```python
   def test_function_with_empty_array() -> None:
       result = function(np.array([]))
       assert result is not None  # Or appropriate behavior
   ```

1. **Single Element**

   ```python
   def test_function_with_single_element() -> None:
       result = function(np.array([0.5]))
       assert len(result) == 1
   ```

1. **Boundary Values**

   ```python
   def test_function_at_min_boundary() -> None:
       result = function(0.0)  # Minimum valid value
       assert result is valid

   def test_function_at_max_boundary() -> None:
       result = function(1.0)  # Maximum valid value
       assert result is valid
   ```

1. **Invalid Input**

   ```python
   def test_function_with_negative_value_raises() -> None:
       with pytest.raises(ValueError, match="must be positive"):
           function(-1.0)
   ```

1. **Numerical Stability**

   ```python
   def test_function_with_very_small_values() -> None:
       result = function(1e-10)
       assert not np.isnan(result)
       assert not np.isinf(result)
   ```

______________________________________________________________________

## Assertions

### Use Appropriate Methods

```python
# For floats - use tolerance
np.testing.assert_allclose(result, expected, rtol=1e-6, atol=1e-9)
assert result == pytest.approx(expected, abs=0.01)

# For integers
assert result == 42

# For booleans
assert condition is True  # Not just: assert condition

# For None
assert result is None  # Not: assert result == None

# For exceptions
with pytest.raises(ValueError, match="expected error message"):
    risky_function()

# For warnings
with pytest.warns(UserWarning, match="warning message"):
    function_that_warns()
```

______________________________________________________________________

## Test Fixtures

### Centralized in conftest.py

```python
# tests/conftest.py
@pytest.fixture
def cli_runner() -> CliRunner:
    """Provide Click test runner."""
    return CliRunner(mix_stderr=False)

@pytest.fixture
def minimal_video(tmp_path: Path) -> Path:
    """Create minimal test video for CLI testing."""
    # Create video
    return video_path
```

### When to Create Fixtures

- ✅ Used by 3+ test files → Add to `conftest.py`
- ✅ Complex setup (>5 lines) → Extract to fixture
- ✅ File/resource management → Use fixture with cleanup
- ❌ Simple data (1-2 lines) → Inline in test

______________________________________________________________________

## Parameterized Tests

### Use for Testing Multiple Inputs

```python
@pytest.mark.parametrize("quality,expected_window", [
    ("fast", 5),
    ("balanced", 7),
    ("accurate", 9),
])
def test_quality_preset_window_size(quality, expected_window):
    """Test each quality preset has correct window size."""
    config = get_config(quality)
    assert config["smoothing_window"] == expected_window
```

### When to Parameterize

- ✅ Same test logic, different inputs
- ✅ Testing enum values exhaustively
- ✅ Boundary value testing
- ❌ Completely different test logic
- ❌ Different assertion patterns

______________________________________________________________________

## CLI Testing Tiers

### Tier 1: Stable (Always Test)

```python
def test_command_exit_code(cli_runner, minimal_video):
    """Test command exits with code 0 on success."""
    result = cli_runner.invoke(command, [str(minimal_video)])
    assert result.exit_code == 0

def test_output_file_created(cli_runner, minimal_video, tmp_path):
    """Test output file is created."""
    output = tmp_path / "output.json"
    result = cli_runner.invoke(command, [str(minimal_video), "--output", str(output)])

    if result.exit_code == 0:
        assert output.exists()
```

### Tier 2: Semi-Stable (Test with Loose Matching)

```python
def test_help_mentions_key_options(cli_runner):
    """Test help includes critical options (not exact text)."""
    result = cli_runner.invoke(command, ["--help"])

    # Check for option flags, not full descriptions
    assert "--quality" in result.output or "-q" in result.output
```

### Tier 3: Fragile (Avoid)

```python
# ❌ DON'T TEST EXACT OUTPUT STRINGS
def test_output_format():  # FRAGILE
    result = cli_runner.invoke(command, [video])
    assert result.output == "Jump height: 0.45m\nFlight time: 600ms"  # Will break

# ✅ DO TEST PRESENCE OF KEY INFORMATION
def test_output_contains_metrics():
    result = cli_runner.invoke(command, [video])
    if result.exit_code == 0:
        assert "jump_height" in result.output
        assert "flight_time" in result.output
```

______________________________________________________________________

## Test Checklist

Before committing new tests:

### Structure

- [ ] File name mirrors source module (`test_pose.py` for `pose.py`)
- [ ] File in correct directory (`tests/core/` for `src/kinemotion/core/`)
- [ ] Imports use absolute paths (`from kinemotion.core.pose import ...`)

### Naming

- [ ] Test function starts with `test_`
- [ ] Name is descriptive (what is tested, not how)
- [ ] Edge cases explicitly marked in name

### Documentation

- [ ] Has docstring explaining what is tested
- [ ] Complex tests include biomechanical/technical context
- [ ] Explains why test matters (especially for regression tests)

### Code Quality

- [ ] Follows AAA pattern (Arrange-Act-Assert)
- [ ] Tests one thing (single responsibility)
- [ ] Uses appropriate assertions (pytest.approx for floats)
- [ ] Includes edge cases (empty, single element, boundaries)

### Performance

- [ ] Unit tests \<1s
- [ ] Integration tests \<10s
- [ ] E2E tests \<30s
- [ ] No network calls (mock external services)
- [ ] Deterministic (no random timing dependencies)

### Resources

- [ ] Uses `tmp_path` for file operations
- [ ] Closes resources (files, trackers)
- [ ] Cleans up temporary files
- [ ] Isolated (doesn't depend on test order)

______________________________________________________________________

## Examples from Codebase

### Excellent Test (CMJ Analysis)

```python
def test_deep_squat_cmj_recreational_athlete() -> None:
    """Test realistic CMJ from recreational athlete with deep squat.

    Biomechanical regression test: Validates detection of typical recreational
    jump characteristics:
    - Jump height: 35-55cm (0.35-0.55m) → flight time ~0.53-0.67s
    - Countermovement depth: 28-45cm (deeper squat)
    - Contact time: 0.45-0.65s (moderate push-off)

    This test prevents regression where recreational athlete jumps are
    misclassified as untrained or elite due to detection errors.

    Scenario: Recreational athlete performing CMJ with pronounced
    countermovement (deep squat preparation).
    """
    # Arrange: Create realistic recreational CMJ trajectory
    fps = 30.0
    positions = np.concatenate([
        np.ones(10) * 1.00,      # Standing at 1.0m
        np.linspace(1.00, 1.35, 15),  # Eccentric 0.35m depth
        np.linspace(1.35, 0.60, 15),  # Concentric push-off
        np.linspace(0.60, 0.15, 18),  # Flight phase 0.45m
        np.linspace(0.15, 1.00, 12),  # Landing
    ])

    # Act: Detect CMJ phases
    result = detect_cmj_phases(positions, fps, window_length=5, polyorder=2)

    # Assert: Verify recreational athlete characteristics
    assert result is not None, "Recreational CMJ should be successfully detected"
    standing, lowest, takeoff, landing = result

    # Verify phase sequence
    assert standing < lowest < takeoff < landing

    # Verify realistic recreational phase durations
    contact_time = (takeoff - lowest) / fps
    assert 0.40 <= contact_time <= 0.75

    flight_time = (landing - takeoff) / fps
    assert 0.45 <= flight_time <= 0.75
```

**Why this is excellent**:

- ✅ Descriptive name explains scenario
- ✅ Comprehensive docstring with biomechanical context
- ✅ Clear AAA structure with comments
- ✅ Realistic test data (not arbitrary values)
- ✅ Assertions verify domain constraints
- ✅ Informative assertion messages

### Good Maintainable CLI Test

```python
class TestCMJCLIFileOperations:
    """Test file creation behavior."""

    def test_json_output_file_created(
        self, cli_runner: CliRunner, minimal_video: Path, tmp_path: Path
    ) -> None:
        """Test JSON output file is created when analysis succeeds."""
        json_output = tmp_path / "metrics.json"

        result = cli_runner.invoke(
            cmj_analyze,
            [str(minimal_video), "--json-output", str(json_output), "--quality", "fast"],
        )

        # ✅ STABLE: Test behavior, not output text
        assert result.exception is None or result.exit_code != 0

        # ✅ STABLE: If successful, file should exist
        if result.exit_code == 0:
            assert json_output.exists()

            # ✅ STABLE: Test JSON structure, not values
            with open(json_output) as f:
                data = json.load(f)

            assert isinstance(data, dict)
            assert "jump_height_m" in data
            assert "flight_time_ms" in data
```

**Why this is maintainable**:

- ✅ Tests stable behavior (file creation, not output format)
- ✅ Handles both success and failure gracefully
- ✅ Doesn't depend on exact output strings
- ✅ Uses class grouping for related tests

______________________________________________________________________

## Coverage Guidelines

### Targets by Module Type

| Module Type     | Target  | Current | Priority            |
| --------------- | ------- | ------- | ------------------- |
| Core algorithms | 85-100% | 89-100% | ✅ High             |
| API/Integration | 60-80%  | 72%     | ✅ Medium           |
| CLI commands    | 60-80%  | 76-87%  | ✅ Medium           |
| Debug overlays  | 20-40%  | 10-36%  | ⚠️ Low (acceptable) |

### What to Cover

**Priority 1 (Must test)**:

- Core algorithms (analysis, kinematics, smoothing, filtering)
- Validation logic
- Metric calculations
- Error handling paths

**Priority 2 (Should test)**:

- API integration
- CLI commands
- Parameter validation
- File I/O operations

**Priority 3 (Nice to have)**:

- Debug visualization
- Logging
- Utility functions
- Error messages

______________________________________________________________________

## Test Data Guidelines

### Realistic vs Synthetic

**Realistic data** (preferred for integration tests):

```python
# Real-world CMJ trajectory with natural motion
positions = load_realistic_trajectory("recreational_athlete_cmj.npy")
```

**Synthetic data** (acceptable for unit tests):

```python
# Synthetic trajectory for controlled testing
positions = np.concatenate([
    np.ones(20) * 1.0,           # Standing
    np.linspace(1.0, 1.4, 30),    # Eccentric
    np.linspace(1.4, 0.6, 20),    # Concentric
    np.linspace(0.6, 0.0, 20),    # Flight
])
```

### Data Characteristics

- Use **pronounced movements** for synthetic data (detection algorithms need clear signals)
- Include **realistic noise** for filtering tests
- Create **edge cases deliberately** (zero velocity, perfect stillness)
- Document **expected values** in comments

______________________________________________________________________

## Common Patterns

### Testing NumPy Arrays

```python
def test_array_operation():
    result = function(input_array)

    # Check shape
    assert result.shape == expected_shape

    # Check values with tolerance
    np.testing.assert_allclose(result, expected, rtol=1e-6, atol=1e-9)

    # Check for invalid values
    assert not np.any(np.isnan(result))
    assert not np.any(np.isinf(result))
```

### Testing with Temporary Files

```python
def test_file_operation(tmp_path):
    """Use pytest's tmp_path fixture."""
    test_file = tmp_path / "test.mp4"

    # Create and test
    create_file(test_file)

    assert test_file.exists()
    assert test_file.stat().st_size > 0

    # No cleanup needed - tmp_path is automatically cleaned
```

### Testing Exceptions

```python
def test_function_validates_input():
    # Test specific exception type and message
    with pytest.raises(ValueError, match="must be positive"):
        function(-1)

    # Test exception is raised (any type)
    with pytest.raises(Exception):
        function(invalid_input)
```

______________________________________________________________________

## Documentation Standards

### Test Docstrings

**Minimal** (simple unit tests):

```python
def test_velocity_calculation() -> None:
    """Test velocity computation with normal input."""
```

**Standard** (most tests):

```python
def test_phase_progression_ordering() -> None:
    """Test phase progression validation: verify phases occur in correct order.

    Biomechanical context: A valid CMJ must have phases in this sequence:
    Standing → Eccentric → Lowest point → Concentric → Flight → Landing
    """
```

**Comprehensive** (complex/regression tests):

```python
def test_deep_squat_cmj_recreational_athlete() -> None:
    """Test realistic CMJ from recreational athlete with deep squat.

    Biomechanical regression test: Validates detection of typical recreational
    jump characteristics:
    - Jump height: 35-55cm (0.35-0.55m) → flight time ~0.53-0.67s
    - Countermovement depth: 28-45cm (deeper squat)
    - Contact time: 0.45-0.65s (moderate push-off)

    This test prevents regression where recreational athlete jumps are
    misclassified as untrained or elite due to detection errors.

    Scenario: Recreational athlete performing CMJ with pronounced
    countermovement (deep squat preparation).
    """
```

______________________________________________________________________

## Running Tests

### Local Development

```bash
# Run all tests
uv run pytest

# Run specific file
uv run pytest tests/core/test_pose.py

# Run specific test
uv run pytest tests/core/test_pose.py::test_pose_tracker_initialization

# Run with verbose output
uv run pytest -v

# Run with coverage
uv run pytest --cov=src/kinemotion

# Generate HTML coverage report
uv run pytest --cov-report=html
open htmlcov/index.html
```

### Before Commit

```bash
# 1. Run all tests
uv run pytest

# 2. Check coverage
uv run pytest --cov=src/kinemotion --cov-report=term-missing

# 3. Lint and type check
uv run ruff check --fix
uv run ruff format
uv run pyright

# 4. Verify all pass
echo "All checks passed ✅"
```

______________________________________________________________________

## Anti-Patterns (What NOT to Do)

### ❌ Don't Test Implementation Details

```python
# BAD - Tests internal implementation
def test_function_uses_numpy_mean():
    with patch('numpy.mean') as mock:
        function()
        mock.assert_called_once()

# GOOD - Tests behavior
def test_function_computes_average_correctly():
    result = function([1, 2, 3])
    assert result == pytest.approx(2.0)
```

### ❌ Don't Use Magic Numbers

```python
# BAD - Unclear what 0.42 represents
assert result < 0.42

# GOOD - Named constants
EXPECTED_CONTACT_TIME_MAX = 0.42  # seconds, elite athlete
assert result < EXPECTED_CONTACT_TIME_MAX
```

### ❌ Don't Create Brittle Tests

```python
# BAD - Breaks with any output format change
assert "Jump Height: 0.45m" in output

# GOOD - Tests presence of information
assert "jump_height" in output.lower()
assert "0.45" in output
```

### ❌ Don't Test Multiple Things

```python
# BAD - Tests too many things
def test_everything():
    assert function1() == expected1
    assert function2() == expected2
    assert function3() == expected3

# GOOD - Separate tests
def test_function1():
    assert function1() == expected1

def test_function2():
    assert function2() == expected2
```

______________________________________________________________________

## When Tests Fail

### Debugging Strategy

1. **Run with verbose output**:

   ```bash
   pytest -v --tb=short tests/failing_test.py
   ```

1. **Check assertion details**:

   ```bash
   pytest -vv tests/failing_test.py  # Extra verbose
   ```

1. **Add debug prints** (temporarily):

   ```python
   def test_function():
       result = function(input)
       print(f"DEBUG: result={result}, expected={expected}")
       assert result == expected
   ```

1. **Run single test with pdb**:

   ```bash
   pytest --pdb tests/failing_test.py::test_specific
   ```

______________________________________________________________________

## Summary

**Golden Rules**:

1. **Mirror source structure** - Test files match source files
1. **Use AAA pattern** - Arrange, Act, Assert
1. **Test behavior, not implementation** - Focus on what, not how
1. **Include edge cases** - Empty, single, boundary, invalid
1. **Document domain context** - Especially for biomechanics tests
1. **Keep tests fast** - Unit tests \<1s, integration \<10s
1. **Make tests maintainable** - Test stable behavior, avoid brittle assertions

**Remember**: Good tests are documentation of expected behavior. Write tests that help future developers understand what the code should do.
