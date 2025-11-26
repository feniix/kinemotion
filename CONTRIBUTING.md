# Contributing to Kinemotion

Thank you for your interest in contributing to Kinemotion! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

This project adheres to the Contributor Covenant [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior via GitHub issues or by contacting the project maintainers.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When creating a bug report, include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples** (video files, command-line parameters)
- **Describe the behavior you observed** and what you expected
- **Include screenshots or debug videos** if relevant
- **Include your environment details**:
  - OS version
  - Python version
  - Kinemotion version
  - Video format and specifications

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

- **Use a clear and descriptive title**
- **Provide a detailed description** of the suggested enhancement
- **Explain why this enhancement would be useful**
- **List any alternative solutions** you've considered

### Pull Requests

We actively welcome pull requests! Here's how to submit one:

1. Fork the repository
1. Create a new branch from `main` for your changes
1. Make your changes following our coding standards
1. Add or update tests as needed
1. Ensure all tests pass and code quality checks succeed
1. Update documentation if needed
1. Submit a pull request

## Development Setup

### Prerequisites

- [asdf](https://asdf-vm.com/) version manager
- asdf plugins for Python and uv

### Installation Steps

1. **Clone your fork**:

   ```bash
   git clone https://github.com/YOUR-USERNAME/kinemotion.git
   cd kinemotion
   ```

1. **Install asdf plugins** (if not already installed):

   ```bash
   asdf plugin add python
   asdf plugin add uv
   ```

1. **Install versions specified in `.tool-versions`**:

   ```bash
   asdf install
   ```

1. **Install project dependencies**:

   ```bash
   uv sync
   ```

### Running the Tool Locally

```bash
# Run from source
uv run kinemotion dropjump-analyze <video_path>

# With debug output
uv run kinemotion dropjump-analyze <video_path> --output debug.mp4 --verbose
```

## Code Quality Standards

This project enforces strict code quality standards. **All contributions must pass these checks** before being merged.

### Type Checking ([pyright](https://github.com/microsoft/pyright))

All code must have complete type annotations and pass pyright strict mode:

```bash
uv run pyright
```

**Requirements**:

- All functions must have type annotations for parameters and return values
- No `Any` types without justification
- No untyped definitions

### Linting ([ruff](https://github.com/astral-sh/ruff))

Code must pass comprehensive linting checks:

```bash
# Check for issues
uv run ruff check

# Auto-fix issues where possible
uv run ruff check --fix
```

### Code Formatting ([black](https://github.com/psf/black))

All code must be formatted with Black:

```bash
uv run black src/
```

### Testing ([pytest](https://docs.pytest.org/))

All tests must pass:

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_contact_detection.py -v
```

### Running All Checks

Before submitting a PR, run all checks:

```bash
uv run ruff check && uv run pyright && uv run pytest
```

Or use the pre-commit hook (if configured):

```bash
git commit -m "Your commit message"
# All checks run automatically
```

## Coding Guidelines

### Python Style

- Follow [PEP 8](https://pep8.org/) style guide
- Use [Black](https://github.com/psf/black) for formatting (line length: 100)
- Use meaningful variable and function names
- Add docstrings to all public functions and classes

### Type Annotations

```python
# Good
def calculate_jump_height(flight_time_ms: float, gravity: float = 9.81) -> float:
    """Calculate jump height from flight time."""
    flight_time_s = flight_time_ms / 1000.0
    return (gravity * flight_time_s ** 2) / 8.0

# Bad - missing type annotations
def calculate_jump_height(flight_time_ms, gravity=9.81):
    flight_time_s = flight_time_ms / 1000.0
    return (gravity * flight_time_s ** 2) / 8.0
```

### Documentation

- Add docstrings to all public functions and classes
- Use [Google-style docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- Document parameters, return values, and exceptions
- Update README.md if adding new features

Example:

```python
def detect_ground_contact(
    positions: np.ndarray,
    fps: float,
    velocity_threshold: float = 0.02,
    min_contact_frames: int = 3
) -> list[ContactPhase]:
    """Detect ground contact phases from position data.

    Args:
        positions: Array of vertical positions (normalized 0-1)
        fps: Video frame rate
        velocity_threshold: Maximum velocity for ground contact detection
        min_contact_frames: Minimum frames required for valid contact

    Returns:
        List of ContactPhase objects with start/end frames

    Raises:
        ValueError: If positions array is empty or invalid
    """
    # Implementation...
```

### Testing

- Write tests for new features
- Maintain or improve code coverage
- Use descriptive test names
- Include edge cases and error conditions

Example:

```python
def test_contact_detection_with_clean_landing():
    """Test contact detection with a clean landing (no bounces)."""
    # Arrange
    positions = create_test_trajectory(clean_landing=True)

    # Act
    phases = detect_ground_contact(positions, fps=30.0)

    # Assert
    assert len(phases) == 1
    assert phases[0].duration_ms > 200
```

## Project Structure

```text
src/kinemotion/
├── __init__.py
├── cli.py                    # Main CLI entry point
├── core/                     # Shared functionality
│   ├── pose.py              # MediaPipe integration
│   ├── smoothing.py         # Signal processing
│   ├── filtering.py         # Outlier rejection
│   └── video_io.py          # Video I/O
└── dropjump/                 # Drop jump analysis
    ├── cli.py               # Drop jump CLI command
    ├── analysis.py          # Contact detection
    ├── kinematics.py        # Metrics calculation
    └── debug_overlay.py     # Video overlay

tests/
├── test_contact_detection.py
├── test_kinematics.py
└── ...
```

### Adding New Features

1. **Core functionality** (reusable across jump types) → `core/`
1. **Jump-specific logic** → appropriate module (e.g., `dropjump/`)
1. **New jump type** → create new module alongside `dropjump/`
1. **Tests** → corresponding test file in `tests/`

## Commit Message Guidelines

Use clear, descriptive commit messages:

- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit first line to 72 characters
- Reference issues and pull requests when relevant

Examples:

```text
Add trajectory curvature analysis for landing detection

Fix sub-frame interpolation edge case at video boundaries

Update CONTRIBUTING.md with type annotation guidelines

Refactor contact detection to use derivative-based velocity
```

## Review Process

1. **Automated checks** run on all pull requests:

   - Type checking ([pyright](https://github.com/microsoft/pyright))
   - Linting ([ruff](https://github.com/astral-sh/ruff))
   - Tests ([pytest](https://docs.pytest.org/))
   - Code formatting ([black](https://github.com/psf/black))

1. **Code review** by maintainers:

   - Code quality and style
   - Test coverage
   - Documentation
   - Performance implications

1. **Feedback and iteration**:

   - Address review comments
   - Push updates to your branch
   - Checks re-run automatically

1. **Merge**:

   - Once approved and all checks pass
   - Squash and merge into `main`

## Getting Help

- **Questions about development**: Open a GitHub issue with the "question" label
- **Stuck on implementation**: Describe what you've tried in an issue
- **General discussion**: Use GitHub Discussions (if enabled)

## License

By contributing to Kinemotion, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors will be recognized in the project README. Thank you for helping make Kinemotion better!
