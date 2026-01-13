# AGENTS.md

This file provides build commands and code style guidelines for agentic coding assistants working in the kinemotion repository.

## Build/Lint/Test Commands

```bash
uv sync                                    # Install dependencies
uv run pytest                             # Run all tests (620 tests, 80.86% coverage)
uv run pytest tests/core/test_smoothing.py::TestExtractLandmarkCoordinates::test_extract_single_landmark  # Single test
uv run pytest tests/core/                 # Test specific module
uv run pytest -m unit                      # Run by marker (unit/integration/slow/requires_video)
uv run pytest --cov-report=html           # Generate HTML coverage at htmlcov/index.html
uv run ruff check --fix                    # Auto-fix linting
uv run ruff format                         # Format code
uv run pyright                             # Type check (strict mode)
pre-commit run --all-files                  # Run all quality checks
```

## Code Style Guidelines

### Type Safety

- **ALL functions must have complete type hints** (pyright strict mode enforced)
- Use type aliases from `core/types.py`: `FloatArray`, `LandmarkCoord`, `MetricsDict`
- See [Type Hints Guide](docs/development/type-hints.md) for detailed patterns

### Formatting (Ruff)

- Line length: 99 characters
- Double quotes for strings/docstrings
- Run `uv run ruff format` before commit

### Import Style

- Standard library → Third-party → Local imports
- No wildcard imports
- Group imports logically (ruff I001)

### Naming Conventions

- Functions/variables: `snake_case`
- Classes: `CamelCase`
- Private functions: `_leading_underscore`
- Constants: `ALL_CAPS`

### Docstrings

- Google-style (Args:, Returns:, Raises:)
- Triple double quotes (`"""`)
- No examples in docstrings

### Code Quality Standards

- Test coverage: ≥50% (current: 80.86%)
- Cognitive complexity: ≤15 per function
- Code duplication: \<3%
- See [Testing Guide](docs/development/testing.md) and [Testing Standards](docs/development/testing-standards.md)

### Commit Format

[Conventional Commits](https://www.conventionalcommits.org/) required: `<type>(<scope>): <description>`

**Types**: feat, fix, perf (version bump); docs, test, refactor, chore, style, ci, build (no bump)
**Breaking changes**: Add `!` after type (e.g., `feat!:`)

### Python Version

- Target: Python 3.10+ (supports >=3.10,\<3.13)
- Development: Python 3.12.7
- Type checking: Pyright strict mode

## Architecture & Implementation Details

- See [CLAUDE.md](CLAUDE.md) for full architecture overview
- See [Implementation Details](docs/technical/implementation-details.md) for video processing, jump algorithms, and sub-frame interpolation
- Data flow: Frontend (React) → Backend API (FastAPI) → kinemotion CLI → Supabase → Frontend

## Maintainability Patterns

- Extract Method: Break down functions with complexity >12
- Parameter Object: Bundle related parameters into dataclasses
- Early Return: Reduce nesting by handling edge cases first
- Helper Functions: Single Responsibility Principle
- Inheritance: Shared behavior via base classes (e.g., `MetricsValidator`)

## CI/CD

- SonarQube Cloud quality gates run on every PR/push: https://sonarcloud.io/project/overview?id=feniix_kinemotion
- Pre-commit hooks enforce ruff, pyright, pytest, and conventional commits
