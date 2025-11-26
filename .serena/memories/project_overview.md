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
src/kinemotion/
├── cli.py                 # Main CLI (registers subcommands)
├── api.py                 # Python API (process_video, bulk functions)
├── core/                  # Shared utilities
│   ├── pose.py           # Pose detection/smoothing
│   ├── filtering.py      # Signal filtering
│   ├── auto_tuning.py    # Quality preset tuning
│   └── video_io.py       # Video reading/writing
├── dropjump/             # Drop jump specific
│   ├── cli.py
│   ├── analysis.py
│   ├── kinematics.py
│   └── debug_overlay.py
└── cmj/                  # CMJ specific
    ├── cli.py
    ├── analysis.py
    ├── kinematics.py
    ├── joint_angles.py
    └── debug_overlay.py

tests/                    # 261 comprehensive tests (74.27% coverage)
docs/                     # Documentation (Diátaxis framework)
```

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
- Latest Release: 0.29.2
