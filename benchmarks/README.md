# Performance Benchmarks

This directory contains performance benchmarks for kinemotion using pytest-benchmark.

## Running Benchmarks

### Run all benchmarks (no tests)

```bash
uv run pytest benchmarks/ --benchmark-only
```

### Run benchmarks with comparison to previous run

```bash
# First run (saves baseline)
uv run pytest benchmarks/ --benchmark-only --benchmark-autosave

# Second run (compares to baseline)
uv run pytest benchmarks/ --benchmark-only --benchmark-compare
```

### Run specific benchmark class

```bash
uv run pytest benchmarks/test_filtering.py::TestBilateralTemporalFilter --benchmark-only
uv run pytest benchmarks/test_drop_jump.py::TestAssignContactStates --benchmark-only
```

### Generate histogram visualization

```bash
uv run pytest benchmarks/ --benchmark-only --benchmark-histogram
# Output: .benchmarks/*/histogram.svg
```

## Output Format

```
---------------------------------------------------------------------------------------
Name (time in ms)         Min       Max      Mean    StdDev    Median     Rounds  Iterations
---------------------------------------------------------------------------------------
test_small_30_frames      0.0391   0.0451   0.0404   0.0021    0.0395          6           1
test_medium_90_frames     0.0401   0.0461   0.0414   0.0022    0.0405          6           1
test_large_300_frames     0.0451   0.0521   0.0464   0.0024    0.0455          6           1
---------------------------------------------------------------------------------------
```

## Comparison Mode

When comparing to a previous run, pytest-benchmark shows:

- **+X%**: Slower (regression)
- **-X%**: Faster (improvement)
- **~**: No significant change

Example:

```
test_large_300_frames                0.0464     -23%  (from 0.0602)
```

## Adding New Benchmarks

1. Create a new test class with `@pytest.mark.benchmark`
1. Use the `benchmark` fixture to time your function
1. Generate realistic test data

```python
@pytest.mark.benchmark
class TestMyFunction:
    def test_small_input(self, benchmark: pytest.fixture) -> None:
        data = generate_test_data(30)
        result = benchmark(my_function, data)
        assert len(result) == 30  # Verify correctness
```

## Benchmark Files

| File                | Tests                                             |
| ------------------- | ------------------------------------------------- |
| `test_filtering.py` | bilateral_temporal_filter, detect_outliers_ransac |
| `test_drop_jump.py` | \_assign_contact_states, detect_ground_contact    |

## CI Integration

To prevent performance regressions in CI, add:

```yaml
- name: Run benchmarks
  run: uv run pytest benchmarks/ --benchmark-only --benchmark-compare
  continue-on-error: true  # Don't fail CI on regression
```
