---
title: codebase-architecture-overview
type: note
permalink: codebase/codebase-architecture-overview
tags:
- architecture
- overview
- structure
---

# Codebase Architecture Overview

## Project Identity
**Kinemotion**: Video-based kinematic analysis for athletic performance using MediaPipe pose tracking.

**Current Version**: v0.28.0 | **Status**: Pre-1.0, active development

## Supported Jump Types

### Drop Jump
- **Starting**: Elevated box
- **Algorithm**: Forward search
- **Velocity**: Absolute (magnitude)
- **Key Metrics**: Ground contact time, flight time, reactive strength index (RSI)

### Counter Movement Jump (CMJ)
- **Starting**: Floor level
- **Algorithm**: Backward search from peak
- **Velocity**: Signed (direction matters)
- **Key Metrics**: Jump height (from flight time), countermovement depth, triple extension angles

## Module Structure

```
src/kinemotion/
├── cli.py                  # Main CLI (registers subcommands)
├── api.py                  # Python API (process_video, process_cmj_video, bulk)
├── core/                   # Shared: pose, smoothing, filtering, auto_tuning, video_io
├── dropjump/               # Drop jump: cli, analysis, kinematics, debug_overlay
└── cmj/                    # CMJ: cli, analysis, kinematics, joint_angles, debug_overlay

tests/                      # 261 tests (74.27% coverage)
docs/                       # Diátaxis framework: guides/, reference/, technical/, development/
```

## Shared Core Components (`src/kinemotion/core/`)

- **pose.py**: MediaPipe pose detection, center of mass calculation
- **smoothing.py**: Savitzky-Golay filtering
- **filtering.py**: Adaptive threshold, butterworth filters
- **auto_tuning.py**: Quality preset parameter tuning
- **video_io.py**: Video reading, SAR metadata handling
- **debug_overlay_utils.py**: Shared visualization utilities

## Design Patterns

1. **Each jump type is a sibling module** with own CLI, analysis, kinematics, visualization
2. **Shared utilities in core/** - no duplication
3. **Auto-tuning system** - parameters optimize based on video characteristics
4. **Function composition** - functions passed as parameters for flexibility
5. **Inheritance for shared behavior** - base classes for common patterns

## Critical Implementation Details

- Read first actual frame for dimensions (not OpenCV properties)
- Handle SAR (Sample Aspect Ratio) metadata for mobile videos
- Convert NumPy types to native Python for JSON: `int()`, `float()`
- CMJ uses signed velocity (not absolute)
- Backward search algorithm for CMJ (find peak first, then work backward)
- Lateral view required for accurate analysis
