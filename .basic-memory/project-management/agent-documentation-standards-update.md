---
title: Agent Documentation Standards Update
type: note
permalink: project-management/agent-documentation-standards-update
---

# Agent Documentation Standards Update

**Date**: 2025-12-14
**Status**: Completed

## Summary
Updated all 9 specialized agents (`.claude/agents/`) to enforce consistent documentation scoping. All agents now have explicit guidelines requiring documentation to be placed in `docs/` directory or basic-memory, preventing ad-hoc markdown files scattered throughout the project.

## Changes Made

### 1. Technical Writer Agent ✅
**File**: `technical-writer.md`
- **Added**: Explicit constraints in Output Standards
- **Key Points**:
  - ALL documentation files MUST go in `docs/` directory or basic-memory
  - Never create ad-hoc markdown files outside `docs/` structure
  - Coordinate with other agents: route documentation creation requests to this agent

### 2. Python Backend Developer ✅
**File**: `python-backend-developer.md`
- **Added**: Documentation routing section in Output Standards
- **Key Points**:
  - Docstrings stay in code (not separate files)
  - API documentation files → route to Technical Writer for `docs/reference/`
  - Implementation details → coordinate with Technical Writer for `docs/technical/`

### 3. Biomechanics Specialist ✅
**File**: `biomechanics-specialist.md`
- **Added**: Documentation guidelines in Output Standards
- **Key Points**:
  - Research/documentation → coordinate with Technical Writer
  - Validation study results → save to basic-memory
  - Never create ad-hoc markdown files

### 4. Computer Vision Engineer ✅
**File**: `computer-vision-engineer.md`
- **Added**: Documentation guidelines in Output Standards
- **Key Points**:
  - Video processing docs → coordinate with Technical Writer
  - Debug findings → save to basic-memory
  - Never create ad-hoc markdown files

### 5. ML Data Scientist ✅
**File**: `ml-data-scientist.md`
- **Added**: Documentation guidelines in Output Standards
- **Key Points**:
  - Parameter tuning docs → coordinate with Technical Writer
  - Validation study findings → save to basic-memory
  - Never create ad-hoc markdown files

### 6. QA Test Engineer ✅
**File**: `qa-test-engineer.md`
- **Added**: New "Documentation Guidelines" section
- **Key Points**:
  - Test documentation/guides → coordinate with Technical Writer
  - Test patterns/findings → save to basic-memory
  - Never create ad-hoc markdown files

### 7. DevOps/CI-CD Engineer ✅
**File**: `devops-cicd-engineer.md`
- **Added**: Documentation guidelines in Output Standards
- **Key Points**:
  - CI/CD process documentation → coordinate with Technical Writer for `docs/development/ci-cd-guide.md`
  - SonarQube/coverage setup → update `docs/technical/ci-cd-configuration.md`
  - Never create ad-hoc markdown files

### 8. Project Manager ✅
**File**: `project-manager.md`
- **Added**: New "Documentation Guidelines" section
- **Key Points**:
  - Roadmap/strategy docs → coordinate with Technical Writer or use basic-memory
  - Milestone tracking → save to basic-memory
  - Complex planning → ensure proper organization in `docs/`
  - Use basic-memory for strategic decisions

### 9. Frontend Developer ✅
**File**: `frontend-developer.md`
- **Added**: Documentation Guidelines subsection in Output Standards
- **Key Points**:
  - UI/UX design documentation → coordinate with Technical Writer
  - Component API documentation → save as code comments, escalate larger docs to Technical Writer
  - Never create ad-hoc markdown files

## Impact & Benefits

### Prevents
- ❌ Ad-hoc markdown files scattered across the project
- ❌ Outdated documentation in random locations
- ❌ Duplicate documentation
- ❌ Unclear documentation ownership

### Ensures
- ✅ All documentation in `docs/` directory (organized by Diátaxis framework)
- ✅ Findings/context in basic-memory (easily searchable project knowledge)
- ✅ Technical Writer coordinates all documentation creation
- ✅ Clear routing and ownership
- ✅ Consistent documentation quality

## How Agents Should Now Work

### When Documentation Is Needed:
1. **Specialist Agent creates/documents findings** → saves to basic-memory or inline code
2. **If full documentation file needed** → specialist coordinates with Technical Writer
3. **Technical Writer creates** → organized in `docs/` with proper Diátaxis structure
4. **Other agents reference** → via basic-memory or `docs/` links

### Quick Reference:
- **Inline/in-code documentation** → Any agent can write (docstrings, comments)
- **Research/validation findings** → Save to basic-memory
- **Formal documentation files** → Route through Technical Writer → placed in `docs/`
- **Strategic decisions** → Save to basic-memory or `docs/strategy/`

## Files Modified
- `.claude/agents/technical-writer.md`
- `.claude/agents/python-backend-developer.md`
- `.claude/agents/biomechanics-specialist.md`
- `.claude/agents/computer-vision-engineer.md`
- `.claude/agents/ml-data-scientist.md`
- `.claude/agents/qa-test-engineer.md`
- `.claude/agents/devops-cicd-engineer.md`
- `.claude/agents/project-manager.md`
- `.claude/agents/frontend-developer.md`

## Next Steps
- No action needed - agents now have explicit guidelines
- Document any new findings in basic-memory with proper organization
- When new documentation files are needed, route through Technical Writer
