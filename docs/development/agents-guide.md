# Kinemotion Specialized Agents Guide

This guide explains how Claude Code's specialized agents work in the Kinemotion project and how to use them effectively.

## Quick Start: Automatic Routing

Claude Code automatically selects the right agent based on:

1. **Keywords** in your message
1. **File paths** you're working with
1. **Context** from the conversation

You don't need to manually select agents - Claude does it for you!

### Example Scenarios

#### Pose Detection Issue

**You say:** "The hip landmarks aren't being detected properly"

**What happens:**

- Claude detects keywords: "landmarks", "detected"
- Automatically routes to: **computer-vision-engineer**
- Agent analyzes MediaPipe settings and video quality
- Returns debugging steps and solutions

#### Metric Validation

**You say:** "Is an RSI of 3.8 realistic for this jump?"

**What happens:**

- Claude detects keywords: "RSI", "realistic"
- Automatically routes to: **biomechanics-specialist**
- Agent validates against biomechanical research
- Returns physiological assessment

#### Performance Problem

**You say:** "The video processing is taking too long"

**What happens:**

- Claude detects keywords: "performance", "taking too long"
- Automatically routes to: **python-backend-developer**
- Agent profiles code and identifies bottlenecks
- Returns optimization recommendations

#### Add New Feature

**You say:** "Add countermovement depth to CMJ analysis"

**What happens:**

- Claude recognizes this needs multiple agents
- **Biomechanics Specialist**: Defines metric biomechanically
- **Python Backend Developer**: Implements calculation
- **QA Test Engineer**: Creates tests
- **Technical Writer**: Documents the API

## Available Agents

### Core Technical Agents

#### Computer Vision Engineer

- **Expertise**: MediaPipe, pose tracking, video processing, debug overlays
- **Auto-invoked for**: Pose detection issues, video I/O, landmark tracking, rotation problems
- **Key files**: `*pose.py`, `*video_io.py`, `*debug_overlay.py`

#### Biomechanics Specialist

- **Expertise**: Jump biomechanics, RSI, triple extension, kinematic analysis
- **Auto-invoked for**: Metric validation, physiological accuracy, velocity calculations
- **Key files**: `*analysis.py`, `*kinematics.py`, `*joint_angles.py`

#### Python Backend Developer

- **Expertise**: Algorithm optimization, NumPy vectorization, API design, code quality
- **Auto-invoked for**: Performance bottlenecks, duplication, type safety, architecture
- **Key files**: `api.py`, `core/*.py`, algorithm implementations

#### ML/Data Scientist

- **Expertise**: Parameter tuning, quality presets, validation, benchmarking
- **Auto-invoked for**: Auto-tuning, filtering parameters, validation studies
- **Key files**: `*auto_tuning.py`, `*filtering.py`, `*smoothing.py`

### Supporting Agents

#### DevOps/CI-CD Engineer

- **Expertise**: GitHub Actions, SonarQube, test infrastructure, CI/CD
- **Auto-invoked for**: Workflow issues, quality gates, coverage reporting
- **Key files**: `.github/workflows/*`, `sonar-project.properties`

#### Technical Writer

- **Expertise**: Diátaxis framework, API docs, guides, tutorials
- **Auto-invoked for**: Documentation creation, structure, examples
- **Key files**: `docs/**/*.md`, `README.md`, `CLAUDE.md`

#### QA/Test Automation Engineer

- **Expertise**: Test coverage, edge cases, fixtures, regression testing
- **Auto-invoked for**: Test creation, coverage improvement, edge case testing
- **Key files**: `tests/**/*.py`, test fixtures

## Explicit Agent Invocation

You can also explicitly request a specific agent:

```bash
# Single agent
Use the computer-vision-engineer agent to debug pose detection

# Multiple agents
Use biomechanics-specialist to define the metric, then python-backend-developer to implement it

# Chain of agents
Have qa-test-engineer create tests, then have technical-writer document the feature
```

## View Available Agents

```bash
/agents
```

This opens an interactive menu showing:

- All available agents
- Their descriptions and expertise
- Tools they have access to
- Options to create, edit, or delete agents

## Testing Agent Routing

Try these example requests to see automatic routing in action:

### Computer Vision Engineer

```
"The pose landmarks are jittery in this video"
"How do I handle video rotation from mobile phones?"
"What MediaPipe confidence threshold should I use?"
```

### Biomechanics Specialist

```
"How should I calculate jump height from flight time?"
"Is triple extension measured at takeoff or peak?"
"What's a typical RSI range for trained athletes?"
```

### Python Backend Developer

```
"This loop is slow, can we vectorize it?"
"How can I reduce code duplication in the analysis modules?"
"What's the best way to structure this API?"
```

### ML/Data Scientist

```
"What filter cutoff frequency should I use?"
"How do I tune the quality presets?"
"What parameters should I use for validation?"
```

### DevOps/CI-CD Engineer

```
"The SonarQube quality gate is failing"
"How do I add coverage reporting to GitHub Actions?"
"Why are tests passing locally but failing in CI?"
```

### Technical Writer

```
"Document this new API function"
"Create a how-to guide for processing videos"
"Update the README with the new features"
```

### QA/Test Automation Engineer

```
"Add tests for the new velocity calculation"
"What edge cases should I test?"
"How do I improve coverage for this module?"
```

## How Agents Work

### Agent Capabilities

Each agent:

- Has a **custom system prompt** with specialized knowledge
- **Limited tool access** for security and focus
- Operates in a **separate context** to preserve main conversation
- Returns results to the main conversation

### Agent Configuration

Agents are configured with YAML frontmatter in `.claude/agents/`:

```yaml
---
name: agent-name
description: When this agent should be used (automatic routing)
tools: Read, Edit, Write, Bash, Grep, Glob  # Optional
model: sonnet  # Optional: sonnet, opus, haiku, or inherit
---

System prompt and instructions...
```

#### Key Configuration Fields

- **name**: Unique identifier (lowercase-with-hyphens)
- **description**: Clear description triggering automatic routing
  - Use **"Use PROACTIVELY"** to encourage automatic use
  - Use **"MUST BE USED"** for mandatory routing
- **tools**: Comma-separated list (omit to inherit all tools)
- **model**: Model to use (defaults to sonnet if omitted)

## Agent Coordination

For complex tasks requiring multiple specialties:

### Sequential Handoff (one after another)

```
Use biomechanics-specialist to define metric,
  then python-backend-developer to implement,
  then qa-test-engineer to test,
  then technical-writer to document
```

### Parallel Consultation (independent work)

```
Have computer-vision-engineer check pose quality
  while qa-test-engineer creates tests
(Results combined)
```

### Validation Chain (implementation → review → docs)

```
python-backend-developer implements
  → qa-test-engineer tests
  → technical-writer documents
```

## Example Workflows

### Workflow 1: Pose Detection Issue

**User:** "Landmarks are jittery in the video"

**Automatic Routing:** Computer Vision Engineer

**Steps:**

1. Agent analyzes video quality and lighting
1. Checks MediaPipe confidence thresholds
1. Recommends filtering parameters
1. May consult ML/Data Scientist for parameter tuning

### Workflow 2: Add New Metric

**User:** "Add countermovement depth to CMJ analysis"

**Automatic Routing:** Multi-agent coordination

**Steps:**

1. Biomechanics Specialist defines metric biomechanically
1. Python Backend Developer implements calculation
1. QA Test Engineer creates tests
1. Technical Writer documents API and usage

### Workflow 3: Performance Issue

**User:** "Video processing is too slow"

**Automatic Routing:** Python Backend Developer

**Steps:**

1. Agent profiles code to find bottleneck
1. Applies NumPy vectorization
1. May consult Computer Vision Engineer for video I/O
1. QA Test Engineer validates no regression

## Best Practices

1. **Single Responsibility**: Each agent should have one clear focus
1. **Detailed Prompts**: Include specific instructions, examples, constraints
1. **Limited Tools**: Only grant necessary tools for the agent's purpose
1. **Clear Descriptions**: Make automatic routing triggers obvious
1. **Version Control**: Commit agents to git for team sharing

### Tips for Best Results

1. **Be specific**: "The hip landmarks are jittery" vs "Something is wrong"
1. **Mention file names**: "Check src/kinemotion/core/pose.py"
1. **Use domain terms**: "RSI", "MediaPipe", "vectorize", "pytest"
1. **Let Claude choose**: Trust automatic routing for most tasks
1. **Explicit when needed**: Use explicit invocation for edge cases

## Managing Agents

### View All Agents

```bash
/agents
```

### Create New Agent

```bash
/agents  # Select "Create New Agent"
```

**Recommended:** Generate with Claude first, then customize.

### Edit Agent

You can edit agent files directly in `.claude/agents/` or use:

```bash
/agents  # Select agent to edit
```

### Agent Capabilities Summary

| Agent                    | Primary Focus                            | Key Tools                   |
| ------------------------ | ---------------------------------------- | --------------------------- |
| Computer Vision Engineer | MediaPipe, video I/O, pose tracking      | Read, Edit, Bash, WebFetch  |
| Biomechanics Specialist  | Metrics validation, physiology           | Read, Edit, Grep, WebSearch |
| Python Backend Developer | Optimization, architecture, code quality | Read, Edit, Write, Bash     |
| ML/Data Scientist        | Parameter tuning, validation             | Read, Edit, WebFetch        |
| DevOps/CI-CD Engineer    | GitHub Actions, SonarQube, CI            | Read, Edit, Bash            |
| Technical Writer         | Documentation, guides, examples          | Read, Edit, Write           |
| QA/Test Engineer         | Test coverage, edge cases, fixtures      | Read, Edit, Bash            |

## Troubleshooting

### Agent Not Auto-Selected

If Claude doesn't automatically use an agent:

1. Check if keywords match agent's `description` field
1. Be more specific in your request
1. Explicitly invoke the agent by name

### Agent Lacks Required Tools

If agent reports missing tools:

1. Open `/agents` interface
1. Select the agent
1. Add required tools to the `tools` field

### Agent Provides Incorrect Guidance

1. Review agent's system prompt
1. Edit to clarify instructions
1. Add specific examples or constraints

## Contributing New Agents

When creating new agents:

1. Identify a clear, focused responsibility
1. Define automatic routing triggers in `description`
1. Grant minimal necessary tools
1. Write detailed system prompt with examples
1. Test automatic routing with example scenarios
1. Document in this guide
1. Commit to version control

## Resources

- **Agent Configuration Files**: `.claude/agents/*.md`
- **Project Instructions**: [CLAUDE.md](https://github.com/feniix/kinemotion/blob/main/CLAUDE.md)
- **Development Guides**: [Testing Guide](testing.md), [Type Hints Guide](type-hints.md)
- **Official Docs**: [Claude Code Subagents Documentation](https://docs.claude.com/en/docs/claude-code/sub-agents)
