# Specialist Agent Routing Guide

## Available Agents & Specializations

### project-manager

**Focus**: Goal coordination, complexity/ROI analysis, task prioritization
**Signals**:

- Creating roadmaps, sprint planning
- Prioritizing work across multiple domains
- Complexity/effort estimation for features
- Milestone planning, deadline management
- Trade-off decisions (quality vs speed, scope vs time)
  **Invoke**: "Use the project-manager to prioritize these features"

### computer-vision-engineer

**Focus**: MediaPipe, pose tracking, video I/O, debug visualization
**Signals**:

- Pose detection accuracy issues
- Video processing pipeline problems
- Frame reading, rotation metadata handling
- Debug overlay visualization
- Performance optimization for video processing
  **Invoke**: "Use computer-vision-engineer to debug pose detection"
  **Key Files**: `src/kinemotion/core/pose.py`, `src/kinemotion/core/video_io.py`, `*/debug_overlay.py`

### biomechanics-specialist

**Focus**: Jump metrics, RSI, triple extension, physiological validation
**Signals**:

- Jump height calculation, contact time accuracy
- Reactive Strength Index (RSI) validation
- Triple extension tracking and measurement
- Physiological bounds establishment for athlete populations
- Metric validation against published research
  **Invoke**: "Use biomechanics-specialist to validate RSI calculation"
  **Key Files**: `src/kinemotion/dropjump/kinematics.py`, `src/kinemotion/cmj/kinematics.py`, `src/kinemotion/cmj/joint_angles.py`

### python-backend-developer

**Focus**: Algorithm optimization, NumPy, API design, code quality
**Signals**:

- Algorithm performance optimization
- NumPy array operations, vectorization
- API design and refactoring
- Code duplication reduction
- Database/persistence layer improvements
  **Invoke**: "Use python-backend-developer for algorithm optimization"
  **Key Files**: `src/kinemotion/api.py`, `src/kinemotion/*/analysis.py`, `src/kinemotion/core/filtering.py`

### ml-data-scientist

**Focus**: Parameter tuning, quality presets, validation, benchmarking
**Signals**:

- Quality preset configuration (lite, balanced, quality)
- Auto-tuning parameter optimization
- Benchmarking against test datasets
- Validation dataset creation
- Model accuracy testing
  **Invoke**: "Use ml-data-scientist for quality preset tuning"
  **Key Files**: `src/kinemotion/core/auto_tuning.py`, test fixtures and datasets

### devops-cicd-engineer

**Focus**: GitHub Actions, SonarQube, CI/CD infrastructure, test infrastructure
**Signals**:

- CI/CD pipeline improvements
- GitHub Actions workflow modifications
- SonarQube integration and quality gates
- Test infrastructure, coverage reporting
- Automated release process
  **Invoke**: "Use devops-cicd-engineer for GitHub Actions setup"
  **Key Files**: `.github/workflows/`, `sonar-project.properties`, `pyproject.toml` (pytest config)

### technical-writer

**Focus**: Documentation (Diátaxis framework), guides, API reference
**Signals**:

- Creating or updating guides and tutorials
- API documentation and reference
- Architectural documentation
- Contribution guidelines
- Documentation structure and organization
  **Invoke**: "Use technical-writer for CMJ biomechanics guide"
  **Key Files**: `docs/guides/`, `docs/reference/`, `docs/technical/`

### qa-test-engineer

**Focus**: Test coverage, edge cases, fixtures, regression testing
**Signals**:

- Expanding test coverage (targeting \<3% duplication, >74% coverage)
- Edge case identification and testing
- Test fixtures and test data creation
- Regression test design
- Test pattern establishment
  **Invoke**: "Use qa-test-engineer for edge case testing"
  **Key Files**: `tests/`, test configuration in `pyproject.toml`

## Routing Decision Tree

```
Task Type → Primary Agent → Secondary Support

Feature Development
├─ New jump type analysis? → computer-vision-engineer + biomechanics-specialist
├─ Algorithm improvement? → python-backend-developer + biomechanics-specialist
├─ Quality preset tuning? → ml-data-scientist + qa-test-engineer
└─ Real-time streaming? → computer-vision-engineer + python-backend-developer

Documentation
├─ Biomechanics guide? → technical-writer + biomechanics-specialist
├─ API reference? → technical-writer + python-backend-developer
├─ Installation/setup? → technical-writer + devops-cicd-engineer
└─ Contribution guide? → technical-writer + qa-test-engineer

Quality & Testing
├─ Test coverage gaps? → qa-test-engineer + biomechanics-specialist
├─ Edge case discovery? → qa-test-engineer + domain specialist
├─ Performance optimization? → python-backend-developer + ml-data-scientist
└─ Code duplication? → python-backend-developer

Infrastructure
├─ CI/CD improvements? → devops-cicd-engineer + python-backend-developer
├─ SonarQube setup? → devops-cicd-engineer
├─ Release automation? → devops-cicd-engineer
└─ Test infrastructure? → devops-cicd-engineer + qa-test-engineer

Planning & Strategy
├─ Roadmap creation? → project-manager + domain specialists
├─ Priority decisions? → project-manager + stakeholders
├─ Complexity estimation? → project-manager + relevant specialist
└─ Sprint planning? → project-manager + team
```

## When Multiple Specialists Are Needed

**Parallel Work**: Independent tasks can be delegated simultaneously

```
Feature: Real-time CMJ streaming
├─ CV Engineer: Stream frame capture and pose detection
├─ Backend Developer: Metrics calculation optimization
└─ ML Scientist: Real-time quality preset selection
(Independent, can run in parallel)
```

**Sequential Handoff**: Complex interdependencies

```
Feature: Multi-sport analysis platform
├─ Biomechanics Specialist: Define metrics for running, throwing
└─ Backend Developer: Refactor architecture to support multiple sports
└─ CV Engineer: Test on diverse video sources
(Sequential: design → implementation → testing)
```

## Communication Patterns

### Clear Delegation

"Use the biomechanics-specialist to validate that jump heights are within 0-1.5m range for recreational athletes"

### Context Passing

Include relevant context when delegating:

- Current metrics/algorithms
- Edge cases discovered
- Performance constraints
- Research/validation requirements

### Integration Points

Specify how work integrates with other domains:

- "Coordinate with CV engineer on frame timing"
- "Ensure compatibility with existing CLI"
- "Validate against test fixtures created by QA"
