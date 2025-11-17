# Kinemotion Specialized Agents

This directory contains specialized Claude Code subagents for the Kinemotion project. Each agent has specific expertise and is automatically invoked by Claude when tasks match their domain.

## Available Agents

### Core Technical Agents

1. **Computer Vision Engineer** (`computer-vision-engineer.md`)

   - **Expertise**: MediaPipe, pose tracking, video processing, debug overlays
   - **Auto-invoked for**: Pose detection issues, video I/O, landmark tracking, rotation problems
   - **Key files**: `*pose.py`, `*video_io.py`, `*debug_overlay.py`

1. **Biomechanics Specialist** (`biomechanics-specialist.md`)

   - **Expertise**: Jump biomechanics, RSI, triple extension, kinematic analysis
   - **Auto-invoked for**: Metric validation, physiological accuracy, velocity calculations
   - **Key files**: `*analysis.py`, `*kinematics.py`, `*joint_angles.py`

1. **Python Backend Developer** (`python-backend-developer.md`)

   - **Expertise**: Algorithm optimization, NumPy vectorization, API design, code quality
   - **Auto-invoked for**: Performance bottlenecks, duplication, type safety, architecture
   - **Key files**: `api.py`, `core/*.py`, algorithm implementations

1. **ML/Data Scientist** (`ml-data-scientist.md`)

   - **Expertise**: Parameter tuning, quality presets, validation, benchmarking
   - **Auto-invoked for**: Auto-tuning, filtering parameters, validation studies
   - **Key files**: `*auto_tuning.py`, `*filtering.py`, `*smoothing.py`

### Supporting Agents

5. **DevOps/CI-CD Engineer** (`devops-cicd-engineer.md`)

   - **Expertise**: GitHub Actions, SonarQube, test infrastructure, CI/CD
   - **Auto-invoked for**: Workflow issues, quality gates, coverage reporting
   - **Key files**: `.github/workflows/*`, `sonar-project.properties`

1. **Technical Writer** (`technical-writer.md`)

   - **Expertise**: Diátaxis framework, API docs, guides, tutorials
   - **Auto-invoked for**: Documentation creation, structure, examples
   - **Key files**: `docs/**/*.md`, `README.md`, `CLAUDE.md`

1. **QA/Test Automation Engineer** (`qa-test-engineer.md`)

   - **Expertise**: Test coverage, edge cases, fixtures, regression testing
   - **Auto-invoked for**: Test creation, coverage improvement, edge case testing
   - **Key files**: `tests/**/*.py`, test fixtures

## How Agents Work

### Automatic Routing

Claude Code automatically routes tasks to the appropriate agent based on:

1. **Task description keywords** (pose detection, RSI, performance, etc.)
1. **File paths** being worked on (`*pose.py` → Computer Vision Engineer)
1. **Context** from the conversation

### Explicit Invocation

You can also explicitly request a specific agent:

```bash
# Use specific agent
Use the computer-vision-engineer agent to debug pose detection

# Chain agents
Use the biomechanics-specialist to validate metrics, then use the technical-writer to document them
```

### Agent Capabilities

Each agent:

- Has a **custom system prompt** with specialized knowledge
- **Limited tool access** for security and focus
- Operates in a **separate context** to preserve main conversation
- Returns results to the main conversation

## Agent Configuration

Agents are configured with YAML frontmatter:

```yaml
---
name: agent-name
description: When this agent should be used (automatic routing)
tools: Read, Edit, Write, Bash, Grep, Glob  # Optional
model: sonnet  # Optional: sonnet, opus, haiku, or inherit
---

System prompt and instructions...
```

### Key Configuration Fields

- **name**: Unique identifier (lowercase-with-hyphens)
- **description**: Clear description triggering automatic routing
  - Use **"Use PROACTIVELY"** to encourage automatic use
  - Use **"MUST BE USED"** for mandatory routing
- **tools**: Comma-separated list (omit to inherit all tools)
- **model**: Model to use (defaults to sonnet if omitted)

## Managing Agents

### View All Agents

```bash
/agents
```

This opens an interactive interface to:

- View all available agents
- Create new agents
- Edit existing agents
- Delete agents
- Manage tool permissions

### Create New Agent

```bash
/agents  # Select "Create New Agent"
```

**Recommended:** Generate with Claude first, then customize.

### Edit Agent

You can edit agent files directly or use:

```bash
/agents  # Select agent to edit
```

## Best Practices

1. **Single Responsibility**: Each agent should have one clear focus
1. **Detailed Prompts**: Include specific instructions, examples, constraints
1. **Limited Tools**: Only grant necessary tools for the agent's purpose
1. **Clear Descriptions**: Make automatic routing triggers obvious
1. **Version Control**: Commit agents to git for team sharing

## Agent Coordination

For complex tasks requiring multiple specialties:

1. **Sequential Handoff**: One agent completes, passes to next

   ```
   Use biomechanics-specialist to define metric, then python-backend-developer to implement
   ```

1. **Parallel Consultation**: Multiple agents work independently

   ```
   Have computer-vision-engineer check pose quality while qa-test-engineer creates tests
   ```

1. **Validation Chain**: Implementation → Review → Documentation

   ```
   python-backend-developer implements → qa-test-engineer tests → technical-writer documents
   ```

## Example Scenarios

### Scenario 1: Pose Detection Issue

**User:** "Landmarks are jittery in the video"

**Automatic Routing:** Computer Vision Engineer

**Workflow:**

1. Agent analyzes video quality and lighting
1. Checks MediaPipe confidence thresholds
1. Recommends filtering parameters
1. May consult ML/Data Scientist for parameter tuning

### Scenario 2: Add New Metric

**User:** "Add countermovement depth to CMJ analysis"

**Automatic Routing:** Multi-agent coordination

**Workflow:**

1. Biomechanics Specialist defines metric biomechanically
1. Python Backend Developer implements calculation
1. QA Test Engineer creates tests
1. Technical Writer documents API and usage

### Scenario 3: Performance Issue

**User:** "Video processing is too slow"

**Automatic Routing:** Python Backend Developer

**Workflow:**

1. Agent profiles code to find bottleneck
1. Applies NumPy vectorization
1. May consult Computer Vision Engineer for video I/O
1. QA Test Engineer validates no regression

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

## Resources

- [Claude Code Subagents Documentation](https://docs.claude.com/en/docs/claude-code/sub-agents)
- [CLAUDE.md](../../CLAUDE.md) - Project instructions
- [Development Guides](../../docs/development/) - Testing, type hints, contribution guides

## Contributing New Agents

When creating new agents:

1. Identify a clear, focused responsibility
1. Define automatic routing triggers in `description`
1. Grant minimal necessary tools
1. Write detailed system prompt with examples
1. Test automatic routing with example scenarios
1. Document in this README
1. Commit to version control
