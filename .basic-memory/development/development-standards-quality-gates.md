---
title: development-standards-quality-gates
type: note
permalink: development/development-standards-quality-gates
tags:
- standards
- quality
- testing
---

# Development Standards & Quality Gates

## Before Every Commit

```bash
uv run ruff check --fix   # Auto-fix linting
uv run pyright            # Type check (strict mode)
uv run pytest             # All tests with coverage
```

## Code Quality Standards

| Standard | Target | Current | Status |
|----------|--------|---------|--------|
| Test Coverage | ≥50% | 74.27% | ✅ Exceeds |
| Type Safety | Strict (Pyright) | 0 errors | ✅ Pass |
| Linting | Ruff | 0 errors | ✅ Pass |
| Code Duplication | <3% | 2.96% | ✅ Just under |
| Line Length | 100 chars max | Enforced | ✅ Pass |

## Coverage Breakdown by Module

- **Core algorithms**: 85-100% ✅ (analysis, kinematics, filtering, pose)
- **API/Integration**: 63% ✅ (api.py)
- **CLI modules**: 62-89% ✅ (dropjump: 88.75%, cmj: 62.27%)
- **Visualization**: 10-36% ✅ (debug overlays - appropriately lower)

## Key Metrics (Current)

- **Tests**: 261 passing
- **Type Errors**: 0
- **Linting Errors**: 0
- **Duplication**: 2.96% (target: <3%)

## Commit Format

**Required**: [Conventional Commits](https://www.conventionalcommits.org/)

**Format**: `<type>(<scope>): <description>`

**Types**:
- `feat`: New feature → minor version bump
- `fix`: Bug fix → patch version bump
- `perf`: Performance improvement → patch
- `docs`, `test`, `refactor`, `chore`, `style`, `ci`, `build` → no version bump

**Examples**:
```
feat: add CMJ analysis with triple extension tracking
fix: correct takeoff detection in backward search algorithm
docs: add triple extension biomechanics guide
test: add CMJ phase detection tests
refactor: extract signed velocity to separate function
```

**Important**: Commit messages must never reference Claude or AI assistance. Keep messages professional and focused on technical changes.

## Test Structure

- `tests/` - Unit tests (mocked, fast)
- HTML report: `uv run pytest --cov-report=html && open htmlcov/index.html`

## Type Hints

- Use TypedDict, type aliases, `NDArray[dtype]`
- Full type annotations required (Pyright strict)
- See docs/development/type-hints.md for modern patterns

## Code Duplication

- Target: <3%
- Check: `npx jscpd src/kinemotion`
- Strategy: Extract to shared core, use inheritance, function composition
