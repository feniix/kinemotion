# Kinemotion Project Overview

## Project Purpose

Video-based kinematic analysis for athletic performance using MediaPipe pose tracking.

Supports two jump types with specialized analysis algorithms:

- **Drop Jump**: Ground contact time, flight time, reactive strength index (RSI)
- **Counter Movement Jump (CMJ)**: Jump height, flight time, countermovement depth, triple extension

## Tech Stack

- **Language**: Python 3.12.7 (supports >=3.10,\<3.13)

- **Key Dependencies**:

  - MediaPipe: >=0.10.9 (pose tracking)
  - OpenCV: >=4.9.0 (video processing)
  - NumPy: >=1.26.0 (numerical computations)
  - SciPy: >=1.11.0 (signal processing)
  - pytest: 9.0.0 (testing)
  - pyright: type checking (strict mode)
  - ruff: linting

- **Build Tool**: uv 0.9.9 (Python package manager/runner)

- **CI/CD**: GitHub Actions + SonarQube Cloud (integrated quality gates)

- **Documentation**: MkDocs + Diátaxis framework (guides, references, technical, research)

## Code Structure

```
.
├── frontend/              # React app (Vercel) - v0.1.0
│   ├── src/              # TypeScript + React components
│   └── package.json      # Vite, React, Supabase client
├── backend/              # FastAPI server (Cloud Run) - v0.1.0
│   ├── src/              # Python API endpoints
│   ├── Dockerfile        # Container configuration
│   └── pyproject.toml    # FastAPI, Supabase, structlog
├── src/kinemotion/       # CLI analysis engine - v0.34.0
│   ├── cli.py           # Main CLI (registers subcommands)
│   ├── api.py           # Python API (used by backend)
│   ├── core/            # Shared: pose, filtering, auto_tuning, video_io
│   ├── dropjump/        # Drop jump: cli, analysis, kinematics, debug_overlay
│   └── cmj/             # CMJ: cli, analysis, kinematics, joint_angles, debug_overlay
└── tests/               # 261 comprehensive tests (74.27% coverage)
    └── docs/            # Documentation (Diátaxis framework)
```

**Data Flow:** User uploads video → Frontend (React) → Backend API (FastAPI) → kinemotion CLI → Results stored in Supabase → Frontend displays results

## Quality Standards

- **Type Safety**: Pyright strict mode (0 type errors)
- **Code Style**: Ruff (100 char lines, 0 linting errors)
- **Test Coverage**: ≥50% target (current: 74.27%)
- **Code Duplication**: \<3% target (current: 2.96%)
- **Commit Format**: Conventional Commits (enforced by pre-commit hook)

## Critical Gotchas

1. **Video Processing**: Read first frame for dimensions (not OpenCV properties), handle rotation metadata (mobile videos), convert NumPy types for JSON
1. **CMJ Algorithm**: Use signed velocity (not absolute), backward search from peak, lateral view required
1. **Drop Jump Algorithm**: Forward search, absolute velocity magnitude

## Available Specialized Agents

- project-manager: Goal coordination, complexity/ROI analysis
- computer-vision-engineer: MediaPipe, pose tracking, video I/O
- biomechanics-specialist: Jump metrics, RSI, triple extension
- python-backend-developer: Algorithm optimization, API design
- ml-data-scientist: Parameter tuning, quality presets
- devops-cicd-engineer: CI/CD, SonarQube, GitHub Actions
- technical-writer: Documentation (Diátaxis framework)
- qa-test-engineer: Test coverage, edge cases, fixtures

## Current Metrics

- Tests: 261 (all passing)
- Coverage: 74.27% (2383 statements, 788 branches)
- Type Errors: 0
- Linting Errors: 0
- Code Duplication: 2.96%
- Latest Release: 0.34.0 (released December 2, 2025)

## Current Phase 1 Work (Issue #10 Focus)

### Issue #10: CMJ Ankle Angle Validation

- **Status**: Discovery phase complete, 12-video validation protocol designed
- **Key Discovery**: Algorithms DO NOT account for 45° camera viewing angle (systematic -5-10° underestimation)
- **Implementation Plan**:
  - Phase 1: Collect 12 validation videos (45°/90° × 60fps/120fps)
  - Phase 2: Implement Option 1 (fixed correction factors, 1-2 weeks)
  - Phase 3: Upgrade to calibration-based correction (future)
- **Documents Created**:
  - 12-video recording protocol (Spanish & English)
  - Camera perspective analysis (196 lines)
  - Technical implementation guide (397 lines)
