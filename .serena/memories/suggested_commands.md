# Development Commands for Kinemotion

## Setup Commands

```bash
asdf install              # Install Python 3.12.7 + uv (from .tool-versions)
uv sync                   # Install dependencies from pyproject.toml
```

## Running the Application

```bash
# Drop jump analysis
uv run kinemotion dropjump-analyze video.mp4

# CMJ analysis
uv run kinemotion cmj-analyze video.mp4

# CMJ with debug video output
uv run kinemotion cmj-analyze video.mp4 --output debug.mp4

# Batch processing
uv run kinemotion cmj-analyze videos/*.mp4 --batch --workers 4
```

## Testing & Quality (Must Run Before Commit)

```bash
# Run all 261 tests with coverage
uv run pytest

# Run tests with HTML coverage report
uv run pytest --cov-report=html
open htmlcov/index.html

# Run tests with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_cmj_analysis.py

# Run tests matching pattern
uv run pytest -k "test_takeoff"
```

## Code Quality (Must Run Before Commit)

```bash
# Auto-fix linting issues
uv run ruff check --fix

# Check for linting (no fix)
uv run ruff check src/

# Type checking (strict mode)
uv run pyright

# Check code duplication
npx jscpd src/kinemotion

# All quality checks combined
uv run ruff check --fix && uv run pyright && uv run pytest
```

## Python API Usage

```python
from kinemotion import process_dropjump_video, process_cmj_video

# Drop jump
metrics = process_dropjump_video("video.mp4", quality="balanced")

# CMJ
metrics = process_cmj_video("video.mp4", quality="balanced")

# Batch processing
from kinemotion import process_video_batch
results = process_video_batch("videos/*.mp4", workers=4)
```

## Documentation

```bash
# Build and serve docs locally
mkdocs serve

# View coverage report (after pytest --cov-report=html)
open htmlcov/index.html

# View SonarQube results
open https://sonarcloud.io/project/overview?id=feniix_kinemotion
```

## Git Operations

```bash
# Check git status
git status

# View recent commits
git log --oneline -10

# Commit with conventional format
git commit -m "fix: correct takeoff detection algorithm"

# Create feature branch
git checkout -b feat/cmj-streaming-analysis
```

## Other Utilities

```bash
# View coverage from XML
cat coverage.xml

# Run Docker build (if needed)
docker build -t kinemotion .

# View test failures more clearly
uv run pytest --tb=short

# Generate type stub
pyright --outputjson coverage.json
```

## Key Notes

- Always run quality checks before committing: `ruff check --fix && pyright && pytest`
- Use conventional commits: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `perf:`, `chore:`
- Coverage report automatically generated with pytest
- Pre-commit hooks enforce conventional commits and quality standards
