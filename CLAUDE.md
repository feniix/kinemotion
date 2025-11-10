# CLAUDE.md

## Repository Purpose

Kinemotion: Video-based kinematic analysis for athletic performance using MediaPipe pose tracking.

**Supported Jump Types:**

- **Drop Jump**: Ground contact time, flight time, reactive strength index
- **Counter Movement Jump (CMJ)**: Jump height, flight time, countermovement depth, triple extension

## Quick Setup

```bash
asdf install        # Install Python 3.12.7 + uv
uv sync            # Install dependencies
uv run kinemotion dropjump-analyze video.mp4
uv run kinemotion cmj-analyze video.mp4
```

**Development:**

```bash
uv run pytest                           # Run all 206 tests with coverage (73.03%)
uv run pytest --cov-report=html         # Generate HTML coverage report
uv run ruff check --fix && uv run pyright  # Lint + type check
```

**Coverage Reports:**

- Terminal: Automatic with `uv run pytest`
- HTML: `htmlcov/index.html` (open in browser)
- XML: `coverage.xml` (for CI integration)

**SonarQube Cloud Integration:**

The project integrates with SonarQube Cloud for continuous code quality and coverage tracking.

Setup (one-time):

1. Visit [SonarCloud](https://sonarcloud.io/) and sign in with GitHub
2. Import the `feniix/kinemotion` repository
3. Generate a token: My Account > Security > Generate Tokens
4. Add token to GitHub: Repository > Settings > Secrets and variables > Actions
   - Name: `SONAR_TOKEN`
   - Value: Your generated token

Configuration files:

- `sonar-project.properties` - SonarQube project configuration
- `.github/workflows/test.yml` - CI workflow with SonarQube scan

The workflow automatically:

- Runs tests with coverage on every PR and push to main
- Uploads coverage.xml to SonarQube Cloud
- Runs quality gate checks

View results: <https://sonarcloud.io/project/overview?id=feniix_kinemotion>

## Architecture

### Module Structure

```text
src/kinemotion/
├── cli.py                  # Main CLI (registers subcommands)
├── api.py                  # Python API (process_video, process_cmj_video, bulk)
├── core/                   # Shared: pose, smoothing, filtering, auto_tuning, video_io
├── dropjump/               # Drop jump: cli, analysis, kinematics, debug_overlay
└── cmj/                    # CMJ: cli, analysis, kinematics, joint_angles, debug_overlay

tests/                      # 206 tests total (comprehensive coverage across all modules)
docs/                       # CMJ_GUIDE, TRIPLE_EXTENSION, REAL_TIME_ANALYSIS, etc.
```

**Design**: Each jump type is a sibling module with its own CLI command, metrics, and visualization.

### Key Differences: Drop Jump vs CMJ

| Feature | Drop Jump | CMJ |
|---------|-----------|-----|
| Starting | Elevated box | Floor level |
| Algorithm | Forward search | Backward search from peak |
| Velocity | Absolute (magnitude) | Signed (direction matters) |
| Parameters | Auto-tuned quality presets | Auto-tuned quality presets |
| Key Metric | Ground contact time | Jump height from flight time |

## Critical Gotchas

**Video Processing:**

- Read first frame for dimensions (not OpenCV properties)
- Handle rotation metadata (mobile videos)
- Convert NumPy types for JSON: `int()`, `float()`

**CMJ Specific:**

- Use signed velocity (not absolute)
- Backward search algorithm (find peak first)
- Lateral view required

See [Implementation Details](docs/technical/implementation-details.md) for complete technical reference.

## Testing & Quality

### Before Commit

```bash
uv run ruff check --fix   # Auto-fix linting
uv run pyright            # Type check (strict)
uv run pytest             # All 206 tests with coverage
```

### Standards

- Pyright strict mode (all functions typed)
- Ruff (100 char lines)
- Conventional Commits (see below)
- **Code duplication target: < 3%**
- **Test coverage: ≥ 50% (current: 73.03% with branch coverage)**

### Coverage Summary

**Current:** 73.03% (206 tests, 2225 statements, 752 branches)

**Coverage by tier:**

- Core algorithms: 85-100% ✅ (analysis, kinematics, filtering, pose)
- API/Integration: 63% ✅ (api.py)
- CLI modules: 62-89% ✅ (dropjump: 88.75%, cmj: 62.27%)
- Visualization: 10-36% ✅ (debug overlays - appropriate)

**Key metrics:**

- All 206 tests pass
- 0 type errors (pyright strict)
- 0 linting errors (ruff)

See [Testing Guide](docs/development/testing.md) for:

- Detailed coverage breakdown by module
- Test file organization
- CLI testing strategy (maintainable patterns)
- Test breakdown by category

View HTML report: `uv run pytest --cov-report=html && open htmlcov/index.html`

### Code Quality

- **Duplication target:** < 3% (current: 2.96%)
- **Check:** `npx jscpd src/kinemotion`

**Principles:**

1. Extract common logic to shared utilities
2. Use inheritance for shared behavior
3. Create helper functions (testable, reusable)
4. Use function composition (pass functions as parameters)

See [Testing Guide](docs/development/testing.md) for detailed duplication avoidance strategies.

## Quick Reference

### CLI

```bash
# Drop jump (auto-tuned parameters)
kinemotion dropjump-analyze video.mp4

# CMJ with debug video
kinemotion cmj-analyze video.mp4 --output debug.mp4

# Batch processing
kinemotion cmj-analyze videos/*.mp4 --batch --workers 4
```

### Python API

```python
# Drop jump
from kinemotion import process_dropjump_video
metrics = process_dropjump_video("video.mp4", quality="balanced")

# CMJ
from kinemotion import process_cmj_video
metrics = process_cmj_video("video.mp4", quality="balanced")
```

## Type Safety & Dependencies

**Type hints:** Use TypedDict, type aliases, NDArray[dtype]. See [Type Hints Guide](docs/development/type-hints.md).

**Key versions:**

- Python: 3.12.7
- NumPy: 2.3.4
- pytest: 9.0.0
- MediaPipe: 0.10.14

## Documentation

Documentation follows the [Diátaxis framework](https://diataxis.fr/):

- **guides/** - How-to tutorials
- **reference/** - Technical specs
- **technical/** - Implementation details
- **development/** - Testing, typing, contribution guides
- **research/** - Background theory

See [docs/README.md](docs/README.md) for complete navigation.

## Commit Format

**Required**: [Conventional Commits](https://www.conventionalcommits.org/) - enforced by pre-commit hook

**Format**: `<type>(<scope>): <description>`

**Types** (triggers version bumps):

- `feat`: New feature → minor version bump (0.x.0)
- `fix`: Bug fix → patch version bump (0.0.x)
- `perf`: Performance improvement → patch
- `docs`, `test`, `refactor`, `chore`, `style`, `ci`, `build` → no version bump

**Examples:**

```bash
feat: add CMJ analysis with triple extension tracking
fix: correct takeoff detection in backward search algorithm
docs: add triple extension biomechanics guide
test: add CMJ phase detection tests
refactor: extract signed velocity to separate function
chore(release): 0.11.0 [skip ci]
```

**Breaking changes**: Add `!` or `BREAKING CHANGE:` footer

```bash
feat!: change API signature for process_video
```

**Important**: Commit messages must never reference Claude or AI assistance. Keep messages professional and focused on the technical changes.

## MCP Servers

Configured in `.mcp.json`: web-search, sequential-thinking, context7, etc.
