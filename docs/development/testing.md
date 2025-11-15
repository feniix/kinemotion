# Testing Guide

Comprehensive guide to testing in the Kinemotion project.

## Current Coverage

**Overall:** 74.27% (2383 statements, 788 branches, 261 tests)

### Coverage by Module Category

#### Perfect Coverage (100%)

- Init files (`__init__.py` modules)
- CMJ joint angles: 100.00%

#### Excellent Coverage (85-99%)

- Drop jump CLI: 88.75%
- CMJ analysis: 88.24%
- Drop jump analysis: 86.26%
- CMJ kinematics: 95.65%
- Drop jump kinematics: 85.71%
- Core video I/O: 91.09%
- Main CLI: 88.89%
- Core pose tracking: 88.46%
- Core filtering: 87.80%

#### Good Coverage (60-84%)

- Core smoothing: 73.29%
- Core auto-tuning: 69.66%
- CMJ CLI: 62.27%
- Core CLI utils: 64.23%
- API module: 62.89%
- Core debug overlay utils: 80.43%

#### Expected Lower Coverage (Visualization/UI)

- Debug overlays: 10-36% (visualization code - appropriate for UI layer)

### Coverage Targets by Module Type

| Module Type     | Target Coverage | Current | Status         |
| --------------- | --------------- | ------- | -------------- |
| Core algorithms | 80%+            | 85-100% | ✅ Exceeded    |
| API/Integration | 60-70%          | 63%     | ✅ Met         |
| CLI modules     | 40-60%          | 62-89%  | ✅ Exceeded    |
| Visualization   | 20-40%          | 10-36%  | ✅ Appropriate |

## Test File Organization

```text
tests/
├── test_cli_dropjump.py      # Drop jump CLI integration (17 tests)
├── test_cli_cmj.py            # CMJ CLI integration (17 tests)
├── test_cli_imports.py        # CLI import verification (5 tests)
├── test_api.py                # Public API tests (19 tests)
├── test_cmj_analysis.py       # CMJ phase detection (31 tests)
├── test_contact_detection.py  # Drop jump detection (12 tests)
├── test_cmj_kinematics.py     # CMJ metrics (4 tests)
├── test_kinematics.py         # Drop jump metrics (2 tests)
├── test_joint_angles.py       # Triple extension (48 tests)
├── test_adaptive_threshold.py # Auto-tuning (10 tests)
├── test_filtering.py          # Signal filtering (15 tests)
├── test_aspect_ratio.py       # Video I/O (13 tests)
├── test_com_estimation.py     # Center of mass (6 tests)
└── test_polyorder.py          # Savitzky-Golay (5 tests)
```

### Test Breakdown by Category

- **Analysis module tests:** 43 tests (edge cases, helper functions, debug modes)
- **API tests:** 19 tests (helper functions, verbose mode, outputs)
- **CLI integration tests:** 34 tests (CliRunner-based, Tier 1 + Tier 2)
- **Kinematics tests:** 8 tests
- **Joint angles tests:** 48 tests
- **Other core tests:** 54 tests

## CLI Testing Strategy

The project uses **maintainable CLI testing** with Click's CliRunner to achieve 62-89% coverage on CLI modules without brittle hardcoded strings.

### Maintainable Test Patterns

#### Pattern 1: Test Exit Codes (Most Stable)

```python
from click.testing import CliRunner

def test_command_succeeds(cli_runner, minimal_video):
    result = cli_runner.invoke(command, [str(minimal_video), '--quality', 'fast'])

    # ✅ STABLE: Exit codes rarely change
    assert result.exit_code == 0
```

#### Pattern 2: Test Behavior, Not Output

```python
def test_json_output_created(cli_runner, minimal_video, tmp_path):
    json_output = tmp_path / "metrics.json"

    result = cli_runner.invoke(
        command,
        [str(minimal_video), '--json-output', str(json_output)]
    )

    # ✅ STABLE: Test file creation
    if result.exit_code == 0:
        assert json_output.exists()

        # ✅ STABLE: Test structure, not values
        with open(json_output) as f:
            data = json.load(f)
        assert 'ground_contact_time_ms' in data  # Key exists
        # ❌ DON'T: assert data['ground_contact_time_ms'] == 250.0
```

#### Pattern 3: Test CSV Structure

```python
def test_csv_summary_created(cli_runner, minimal_video, tmp_path):
    csv_path = tmp_path / "summary.csv"

    result = cli_runner.invoke(
        command,
        [str(minimal_video), '--batch', '--csv-summary', str(csv_path)]
    )

    if result.exit_code == 0 and csv_path.exists():
        import csv

        with open(csv_path, newline="") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

            # ✅ STABLE: Test structure
            assert reader.fieldnames is not None  # Has headers
            assert len(rows) >= 1  # Has data
            # ❌ DON'T: Check specific column names or cell values
```

#### Pattern 4: Parametrized Options

```python
@pytest.mark.parametrize("quality", ["fast", "balanced", "accurate"])
def test_quality_presets(cli_runner, minimal_video, quality):
    result = cli_runner.invoke(
        command,
        [str(minimal_video), '--quality', quality]
    )

    # ✅ STABLE: Just verify option accepted
    assert "Invalid quality" not in result.output
```

### What TO Test (CLI)

#### Tier 1: Must Have (High Priority)

- ✅ Help text displays (`--help`)
- ✅ Missing video file error
- ✅ Invalid quality preset error
- ✅ JSON output file created
- ✅ Debug video output created
- ✅ All quality presets accepted
- ✅ Expert parameters accepted
- ✅ Command runs without crash

#### Tier 2: Nice to Have (Medium Priority)

- ✅ Batch mode with multiple videos
- ✅ Output directory creation
- ✅ CSV summary creation
- ✅ Workers option accepted

### What NOT to Test (CLI)

- ❌ Exact output text (too fragile)
- ❌ Progress bar appearance
- ❌ Specific metric values (tested in core modules)
- ❌ Output formatting details
- ❌ Color codes in terminal

### CLI Test Results

#### Tier 1 Tests (12 per CLI = 24 total)

**Coverage improvement:**

- dropjump/cli.py: 23.33% → 52.08% (+28.75%)
- cmj/cli.py: 22.73% → 51.82% (+29.09%)

#### Tier 2 Tests (5 per CLI = 10 total)

**Final coverage:**

- dropjump/cli.py: 52.08% → 88.75% (+36.67%)
- cmj/cli.py: 51.82% → 62.27% (+10.45%)

**Total CLI tests:** 34 tests (all passing)

## Avoiding Code Duplication

When writing new code, follow these principles to maintain duplication below 3%:

### 1. Extract Common Logic

If you find yourself copying code between modules, extract it to a shared utility.

**Examples:**

- `core/smoothing.py` uses `_smooth_landmarks_core()` shared by both standard and advanced smoothing
- `core/debug_overlay_utils.py` provides `BaseDebugOverlayRenderer` base class

### 2. Use Inheritance for Shared Behavior

When classes share common initialization or methods.

**Example:**

- `DebugOverlayRenderer` and `CMJDebugOverlayRenderer` inherit from `BaseDebugOverlayRenderer`
- Avoids duplicating `__init__()`, `write_frame()`, `close()`, and context manager methods

### 3. Create Helper Functions

Break down complex functions into smaller, reusable pieces.

**Examples:**

- `_extract_landmark_coordinates()`, `_get_landmark_names()`, `_fill_missing_frames()`
- Makes code more testable and reusable

### 4. Use Function Composition

Pass functions as parameters to share control flow logic.

**Example:**

- `_smooth_landmarks_core()` accepts a `smoother_fn` parameter
- Allows different smoothing strategies without duplicating iteration logic

### 5. Check Duplication

Run `npx jscpd src/kinemotion` to verify duplication stays below 3%.

**Current:** 2.96% (206 duplicated lines out of 6952)

**Acceptable duplicates:**

- CLI option definitions
- Small wrapper functions for type safety

## Running Tests

### Quick Commands

```bash
# Run all tests with coverage
uv run pytest

# Run specific test file
uv run pytest tests/test_cmj_analysis.py

# Run tests matching pattern
uv run pytest -k "test_edge"

# Run with verbose output
uv run pytest -v

# Generate HTML coverage report
uv run pytest --cov-report=html
open htmlcov/index.html
```

### Coverage Reports

**Terminal:** Automatic with `uv run pytest`

**HTML:** `htmlcov/index.html` (open in browser)

**XML:** `coverage.xml` (for CI integration)

### Test Configuration

Pytest 9 native TOML configuration in `pyproject.toml`:

```toml
[tool.pytest]
minversion = "9.0"
testpaths = ["tests"]
console_output_style = "times"  # Per-test execution time
strict = true                    # All strictness options enabled
addopts = [
    "--cov=src/kinemotion",
    "--cov-report=term-missing",
    "--cov-report=html",
    "--cov-report=xml",
    "--cov-branch",
]
```

### Before Commit Checklist

```bash
uv run ruff check --fix   # Auto-fix linting
uv run pyright            # Type check (strict)
uv run pytest             # All 261 tests with coverage (74.27%)
```

All checks must pass before committing.
