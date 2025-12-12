# CLAUDE.md

## Repository Purpose

Kinemotion: Video-based kinematic analysis for athletic performance using MediaPipe pose tracking.

**Supported Jump Types:**

- **Drop Jump**: Ground contact time, flight time, reactive strength index
- **Counter Movement Jump (CMJ)**: Jump height, flight time, countermovement depth, triple extension

## Current Roadmap (MVP-First Approach)

**Phase 1: MVP Validation (Weeks 1-3)**
- Issue #10 (P0): ✅ Validated optimal camera angle for MediaPipe (45° oblique recommended)
- Issue #11 (P0): Validate CMJ metrics with phase progression tests
- Issue #12 (P0): Build simple web UI (upload → analyze → export)
- **Goal:** Get product in coaches' hands, gather market feedback

**Phase 2: Market-Driven Development (Week 4+)**
- Real-Time Analysis (if coaches ask for live feedback)
- Running Gait Analysis (if runners/coaches ask for it)
- API & Integrations (if partners request them)
- **Goal:** Build features customers actually want

**See:**
- `docs/strategy/1-STRATEGIC_SUMMARY.md` - Strategic direction
- `docs/strategy/MVP_VALIDATION_CHECKPOINTS.md` - Phase 2 decision gates
- `docs/strategy/MVP_FEEDBACK_COLLECTION.md` - Feedback collection plan

## Quick Setup

```bash
asdf install        # Install Python 3.12.7 + uv
uv sync            # Install dependencies
uv run kinemotion dropjump-analyze video.mp4
uv run kinemotion cmj-analyze video.mp4
```

**Development:**

```bash
uv run pytest                           # Run all tests (207 test functions)
uv run pytest --cov-report=html         # Generate HTML coverage report
uv run ruff check --fix && uv run pyright  # Lint + type check
```

**Note**: Test count reflects 620 passing tests across 24 test files. Parameterized tests generate additional test instances at runtime. Total coverage: 80.86%.

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
│   ├── validation.py       # Base classes (ValidationResult, MetricsValidator, AthleteProfile)
│   └── [other shared modules]
├── cmj/                    # CMJ: cli, analysis, kinematics, joint_angles, debug_overlay
│   ├── metrics_validator.py    # CMJ validator (extends MetricsValidator)
│   └── validation_bounds.py    # CMJ bounds (CMJBounds, RSIBounds, etc.)
├── dropjump/               # Drop jump: cli, analysis, kinematics, debug_overlay
│   ├── metrics_validator.py    # Drop jump validator (extends MetricsValidator)
│   └── validation_bounds.py    # Drop jump bounds (DropJumpBounds)
└── [other modules]

tests/                      # 620 tests (comprehensive coverage across all modules)
├── conftest.py             # Shared fixtures (cli_runner, minimal_video, sample_video_path)
├── core/                   # Core module tests (9 files)
├── dropjump/               # Drop jump tests (6 files)
├── cmj/                    # CMJ tests (5 files)
└── cli/                    # CLI tests (3 files)
docs/                       # CMJ_GUIDE, TRIPLE_EXTENSION, REAL_TIME_ANALYSIS, etc.
```

**Design**: Each jump type is a sibling module with its own CLI command, metrics, validation, and visualization. Shared validation infrastructure (base classes) in `core/validation.py`.

**Test Organization**: Tests mirror source structure with subdirectories for core/, dropjump/, cmj/, and cli/. Shared fixtures centralized in tests/conftest.py to eliminate duplication.

### Full-Stack Architecture

The project has evolved into a complete platform with three main components:

```text
.
├── frontend/              # React app (Vercel) - v0.1.0
│   ├── src/              # TypeScript + React components
│   └── package.json      # Vite, React, Supabase client
├── backend/              # FastAPI server (Cloud Run) - v0.1.0
│   ├── src/              # Python API endpoints
│   ├── Dockerfile        # Container configuration
│   └── pyproject.toml    # FastAPI, Supabase, structlog
├── src/kinemotion/       # CLI analysis engine - v0.34.0
│   ├── cli.py           # Main CLI commands
│   ├── api.py           # Python API (used by backend)
│   └── [modules]        # Core, dropjump, cmj
└── tests/               # 620 comprehensive tests (80.86% coverage)
```

**Data Flow:**
```
User uploads video → Frontend (React) → Backend API (FastAPI) → kinemotion CLI → Results stored in Supabase → Frontend displays results
```

**Deployment:**
- Frontend: Vercel (auto-deploy from main, manual trigger)
- Backend: Google Cloud Run (GitHub Actions, Workload Identity Federation)
- CLI: PyPI (v0.34.0, standalone usage + backend integration)

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
- **45° oblique view recommended** (better MediaPipe tracking than 90° lateral)
  - At 90° lateral: MediaPipe confuses left/right feet (occlusion)
  - At 45° oblique: Both legs clearly separated → accurate tracking

See [Implementation Details](docs/technical/implementation-details.md) for complete technical reference.

## Testing & Quality

### Before Commit

```bash
uv run ruff check --fix   # Auto-fix linting
uv run ruff format        # Format code
uv run pyright            # Type check (strict)
uv run pytest             # All tests (207 test functions)
```

### Standards

- Pyright strict mode (all functions typed)
- Ruff (88 char lines, both linting and formatting)
- Conventional Commits (see below)
- **Code duplication target: < 3%**
- **Test coverage: ≥ 50% (current: 80.86% with branch coverage)**
- **Test count: 620 tests across 24 test files**
- **SonarQube maintainability: 86% of issues resolved (6/7)**

### Coverage Summary

**Current:** 80.86% (620 tests, 3296 statements, 1088 branches)

**Coverage by tier:**

- Core algorithms: 89-100% ✅ (smoothing: 100%, filtering: 89%, analysis: 88-94%)
- API/Integration: 66% ✅ (api.py - improved with helper extraction)
- CLI modules: 90-91% ✅ (dropjump: 90.24%, cmj: 91.26%)
- Validation: 80-100% ✅ (validators, bounds)
- Kinematics: 92-93% ✅ (cmj: 92.25%, dropjump: 93.03%)
- Visualization: 10-40% ✅ (debug overlays - appropriate)

**Key metrics:**

- All 620 tests pass ✅
- 0 type errors (pyright strict) ✅
- 0 linting errors (ruff) ✅
- 100% coverage on critical modules (smoothing, formatting, validation_bounds) ✅

**Test Organization:**

- Mirrored source structure: tests/core/, tests/dropjump/, tests/cmj/, tests/cli/
- Centralized fixtures in tests/conftest.py
- Zero fixture duplication across test files
- Comprehensive edge case testing (81 new tests added)

See [Testing Guide](docs/development/testing.md) for:

- Detailed coverage breakdown by module
- Test file organization
- CLI testing strategy (maintainable patterns)
- Test breakdown by category

View HTML report: `uv run pytest --cov-report=html && open htmlcov/index.html`

### Code Quality

- **Duplication target:** < 3% (current: 2.96%)
- **SonarQube maintainability:** 86% issues resolved
- **Cognitive complexity:** Target ≤15 per function
- **Check:** `npx jscpd src/kinemotion`

**Principles:**

1. Extract common logic to shared utilities
2. Use inheritance for shared behavior
3. Create helper functions (testable, reusable)
4. Use function composition (pass functions as parameters)
5. Apply Extract Method pattern for complex functions (see recent refactoring)

**Maintainability Patterns:**
- Extract Method: Break down functions with complexity >15
- Parameter Object: Bundle related parameters into dataclasses
- Early Return: Reduce nesting by handling edge cases first
- Helper Functions: Single Responsibility Principle for all helpers

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

- Python: 3.12.7 (supports >=3.10,<3.13)
- NumPy: >=1.26.0
- pytest: 9.0.0
- MediaPipe: >=0.10.9
- OpenCV: >=4.9.0
- SciPy: >=1.11.0
- uv: 0.9.9

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

## Specialized Subagents

This project uses Claude Code's native subagent system for automatic task routing to domain experts.

**Available Agents** (in `.claude/agents/`):

- **project-manager**: Goal coordination, complexity/ROI analysis, task prioritization, milestone tracking
- **computer-vision-engineer**: MediaPipe, pose tracking, video I/O, debug overlays
- **biomechanics-specialist**: Jump metrics, RSI, triple extension, physiological validation
- **python-backend-developer**: Algorithm optimization, NumPy, API design, code quality
- **ml-data-scientist**: Parameter tuning, quality presets, validation, benchmarking
- **devops-cicd-engineer**: GitHub Actions, SonarQube, CI/CD, test infrastructure
- **technical-writer**: Documentation (Diátaxis framework), guides, API reference
- **qa-test-engineer**: Test coverage, edge cases, fixtures, regression testing

**How It Works:**

Claude automatically routes tasks to the appropriate agent based on:

- Task keywords (pose detection → Computer Vision Engineer)
- Files being edited (`*analysis.py` → Biomechanics Specialist)
- Context from the conversation

**Explicit Invocation:**

```bash
Use the computer-vision-engineer agent to debug pose detection
Use biomechanics-specialist to validate RSI calculation
```

**Managing Agents:**

```bash
/agents  # Interactive interface to view, create, edit agents
```

See [Agents Guide](docs/development/agents-guide.md) for complete documentation.

## MCP Servers & Tools

This project integrates multiple MCP (Model Context Protocol) servers for enhanced capabilities. All are configured in `.mcp.json`.

### Core MCP Tools

#### **basic-memory** - Knowledge Management
- **Purpose**: Store and retrieve project context, notes, and architectural decisions
- **Scope**: **Project-scoped** - all operations are constrained to the `dropjump` project
- **Use Cases**:
  - Save project summaries and setup information
  - Build context from memory notes for conversations
  - Search across project knowledge base
- **Key Functions**:
  - `write_note(title, content, folder)` - Save information in organized folders
  - `search_notes(query)` - Find relevant project context by keyword
  - `build_context(url)` - Load context from specific memory paths (supports pattern matching like `folder/*`)
  - `read_note(identifier)` - Retrieve a specific note by title or path
  - `list_directory(dir_name)` - Browse memory structure
- **Current Memory Structure**:
  - `codebase/` - Architecture overview, module relationships
  - `biomechanics/` - Jump metrics, RSI, triple extension formulas
  - `development/` - Quality gates, testing standards
  - `api/` - API reference and quick commands
  - `project-management/` - Subagent routing guide, task prioritization
  - `strategy/` - Roadmap and strategic priorities
- **Usage Patterns**:
  - **Save findings**: `write_note("New test pattern", "...", "development")`
  - **Retrieve context**: `build_context("memory://biomechanics/*")` to load all biomechanics notes
  - **Search knowledge**: `search_notes("CMJ triple extension")` to find relevant information
  - **Build conversations**: Call `build_context()` before complex tasks to enhance context

#### **exa** - Web Search & Code Context
- **Purpose**: Real-time web search and code example retrieval
- **Use Cases**:
  - Search for libraries, SDKs, and API documentation
  - Find code examples and best practices
  - Retrieve fresh information beyond knowledge cutoff
- **Key Functions**:
  - `web_search_exa()` - Search the web with context optimization
  - `get_code_context_exa()` - Find relevant code examples (React, Python, etc.)
- **Example**: "React useState hook examples" returns fresh, high-quality code context

#### **ref** - Documentation Search
- **Purpose**: Search and retrieve documentation from web and private resources
- **Use Cases**:
  - Find API reference documentation
  - Access framework/library guides
  - Search private documentation (repos, PDFs)
- **Key Functions**:
  - `ref_search_documentation()` - Search public docs and private resources
  - `ref_read_url()` - Fetch and read specific documentation pages
- **Example**: Search Python pandas documentation or GitHub repo guides

#### **sequential-thinking** - Complex Reasoning
- **Purpose**: Break down complex problems into step-by-step thinking
- **Use Cases**:
  - Plan multi-step implementations
  - Debug complex issues systematically
  - Design architecture decisions with full context
- **Key Functions**:
  - `sequentialthinking()` - Decompose problems, revise thinking, verify solutions
- **Features**:
  - Branch thinking into alternative approaches
  - Revise earlier conclusions as understanding deepens
  - Verify hypotheses before finalizing

#### **serena** - Semantic Code Analysis
- **Purpose**: Intelligent code exploration and precise symbol manipulation
- **Use Cases**:
  - Understand codebase architecture efficiently
  - Find and refactor symbols across the project
  - Track code relationships and dependencies
- **Key Functions**:
  - `get_symbols_overview()` - Get high-level symbol structure
  - `find_symbol()` - Locate classes, functions, methods
  - `find_referencing_symbols()` - See all references to a symbol
  - `replace_symbol_body()` - Precise code editing
  - `search_for_pattern()` - Regex search with context
- **Philosophy**: Read only what's necessary - use symbolic tools before full file reads

### Usage Patterns

**For Research & Context Building:**
```
exa (code context) + ref (documentation) → build_context (in basic-memory)
```

**For Complex Problem Solving:**
```
sequential-thinking (decompose) → serena (code analysis) → implement
```

**For Code Refactoring:**
```
serena (find_symbol) → sequential-thinking (plan changes) → serena (replace/insert)
```

**For Knowledge Management:**
```
write_note (save findings) → search_notes (retrieve later) → build_context (enhance conversations)
```

### When to Use Each Tool

| Task | Primary | Secondary |
|------|---------|-----------|
| Understand codebase architecture | **serena** (symbols overview) | basic-memory (build_context) |
| Find specific function/class | **serena** (find_symbol) | - |
| Search for best practices | **exa** (get_code_context_exa) | ref (documentation) |
| Debug complex logic | **sequential-thinking** | serena (find_referencing_symbols) |
| Save findings for future use | **basic-memory** (write_note) | - |
| Load project context into conversation | **basic-memory** (build_context) | - |
| Search project knowledge base | **basic-memory** (search_notes) | - |
| Edit code precisely | **serena** (replace_symbol_body) | - |
| Search project code patterns | **serena** (search_for_pattern) | - |
| Find API documentation | **ref** (ref_search_documentation) | exa (web_search_exa) |

### Practical Memory Usage Examples

**Example 1: Building Context for CMJ Development**
```python
# At start of complex CMJ work, load existing knowledge
build_context("memory://biomechanics/*")  # Load all biomechanics notes
# Returns context on triple extension, RSI formulas, metric validation

# After discovering new pattern, save it
write_note(
    title="CMJ Takeoff Detection Edge Case",
    content="Found that backward search fails when...",
    folder="biomechanics"
)
```

**Example 2: Retrieving API Reference During Implementation**
```python
# Search for quick reference while implementing
search_notes("API reference CMJ metrics")  # Find API documentation
# Or directly load
build_context("memory://api/*")  # Get all API quick commands
```

**Example 3: Quality Gate Review Before Commit**
```python
# Load quality standards and testing patterns
build_context("memory://development/*")  # Load quality gates
search_notes("test coverage requirements")  # Find specific requirements
# Use this context to ensure commit meets standards
```

**Example 4: Task Prioritization and Strategic Planning**
```python
# Load roadmap and priorities when planning new work
build_context("memory://strategy/*")  # Get current roadmap
build_context("memory://project-management/*")  # Get subagent routing
# This helps route work to appropriate specialized agents
```
