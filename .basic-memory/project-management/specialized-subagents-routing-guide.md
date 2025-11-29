---
title: specialized-subagents-routing-guide
type: note
permalink: project-management/specialized-subagents-routing-guide
tags:
- agents
- project-management
- routing
---

# Specialized Subagents - Routing Guide

This project has 8 specialized domain-expert agents configured in `.claude/agents/`.

## Agent Routing Logic

**Claude automatically routes tasks** based on:
- Task keywords (e.g., "pose detection" → Computer Vision Engineer)
- Files being edited (e.g., `*analysis.py` → Biomechanics Specialist)
- Context from conversation

**Or explicitly invoke:**
```
Use the computer-vision-engineer agent to debug pose detection
Use biomechanics-specialist to validate RSI calculation
```

## Available Agents

### 1. Project Manager (30% allocation)
- **Expertise**: Goal coordination, complexity/ROI analysis, task prioritization, milestone tracking
- **Use For**: Breaking down features, estimating effort, assessing ROI
- **Task 1 involvement**: Ankle fix task prioritization
- **Task 5 involvement**: API strategy and integration roadmap

### 2. Computer Vision Engineer (40% allocation)
- **Expertise**: MediaPipe, pose tracking, video I/O, rotation/metadata, debug overlays, occlusion, lighting
- **Use For**: Pose detection issues, video processing, visualization
- **Task 3 involvement**: Real-time WebSocket streaming implementation
- **Key files**: src/kinemotion/core/pose.py, *debug_overlay.py

### 3. Biomechanics Specialist (30% allocation)
- **Expertise**: Jump metrics validation, RSI calculation, triple extension, countermovement depth, flight time physics, velocity calculations
- **Use For**: Metric validation, algorithm accuracy, physiological correctness
- **Task 1 involvement**: Ankle angle calculation fix (foot_index vs heel)
- **Task 2 involvement**: CMJ validation tests
- **Task 4 involvement**: Running gait analysis metrics
- **Key files**: src/kinemotion/{dropjump,cmj}/analysis.py, joint_angles.py

### 4. Python Backend Developer (60% allocation)
- **Expertise**: Algorithm optimization, NumPy vectorization, API design, code quality, performance bottlenecks
- **Use For**: Performance optimization, API implementation, code refactoring, architecture decisions
- **Task involvement**: All tasks (infrastructure)
- **Key files**: src/kinemotion/core/*.py, src/kinemotion/api.py

### 5. ML Data Scientist (auto for certain files)
- **Expertise**: Auto-tuning algorithms, parameter optimization, quality presets, validation studies, benchmark datasets, statistical analysis
- **Use For**: Parameter tuning, quality preset adjustment, validation frameworks
- **Trigger files**: auto_tuning.py, filtering.py, smoothing.py
- **Key file**: src/kinemotion/core/auto_tuning.py

### 6. DevOps/CI-CD Engineer (available for infrastructure)
- **Expertise**: GitHub Actions workflows, SonarQube integration, test infrastructure, coverage reporting, quality gates
- **Use For**: CI/CD pipeline improvements, SonarCloud setup, GitHub workflow issues
- **Trigger files**: .github/workflows/*, sonar-project.properties
- **Task 5 involvement**: API documentation CI/CD

### 7. Technical Writer (30% allocation - Task 5)
- **Expertise**: Documentation (Diátaxis framework), guides, tutorials, API reference, implementation details
- **Use For**: Documentation updates, guide creation, API specs
- **Task 5 involvement**: OpenAPI spec, integration examples, webhooks documentation
- **Key files**: docs/**/*.md, README.md

### 8. QA Test Engineer (30% allocation - Task 2)
- **Expertise**: Test coverage improvement, edge case testing, regression testing, test video creation, pytest fixtures
- **Use For**: Test strategy, coverage analysis, fixture design
- **Task 2 involvement**: CMJ phase progression tests, physiological bounds validation
- **Key files**: tests/**/*.py

## Task-to-Agent Mapping

| Task | Primary Agent | Secondary Agents | Duration |
|------|---------------|------------------|----------|
| Task 1: Ankle fix | Biomechanics + Backend | Computer Vision | 2-3 days |
| Task 2: CMJ tests | QA + Biomechanics | - | 3-4 days |
| Task 3: Real-time | CV Engineer + Backend | Project Manager | 3-4 weeks |
| Task 4: Running gait | Biomechanics + Backend | CV Engineer | 2-3 weeks |
| Task 5: APIs | Technical Writer + Backend | ML Scientist | 2 weeks |

## Managing Agents

```bash
/agents  # Interactive interface to view, create, edit agents
```

See [Agents Guide](../../docs/development/agents-guide.md) for complete documentation.

## Resource Allocation (6-week sprint)

- **Biomechanics Specialist**: 30% (Tasks 1, 2, 4)
- **Computer Vision Engineer**: 40% (Task 3)
- **Python Backend Developer**: 60% (all tasks)
- **QA Engineer**: 30% (Task 2)
- **Technical Writer**: 30% (Task 5)
- **Project Manager**: Coordination
- **ML Data Scientist**: Parameter tuning as needed
