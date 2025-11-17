# Kinemotion Subagent Quickstart

This guide shows you how Claude Code automatically routes tasks to specialized agents.

## How Automatic Routing Works

Claude Code analyzes your request and automatically selects the right agent based on:

1. **Keywords** in your message
1. **File paths** you're working with
1. **Context** from the conversation

You don't need to manually select agents - Claude does it for you!

## Example Scenarios

### Example 1: Pose Detection Issue

**You say:** "The hip landmarks aren't being detected properly"

**What happens:**

- Claude detects keywords: "landmarks", "detected"
- Automatically routes to: **computer-vision-engineer**
- Agent analyzes MediaPipe settings and video quality
- Returns debugging steps and solutions

### Example 2: Metric Validation

**You say:** "Is an RSI of 3.8 realistic for this jump?"

**What happens:**

- Claude detects keywords: "RSI", "realistic"
- Automatically routes to: **biomechanics-specialist**
- Agent validates against biomechanical research
- Returns physiological assessment

### Example 3: Performance Problem

**You say:** "The video processing is taking too long"

**What happens:**

- Claude detects keywords: "performance", "taking too long"
- Automatically routes to: **python-backend-developer**
- Agent profiles code and identifies bottlenecks
- Returns optimization recommendations

### Example 4: Add New Feature

**You say:** "Add countermovement depth to CMJ analysis"

**What happens:**

- Claude recognizes this needs multiple agents
- **Biomechanics Specialist**: Defines metric biomechanically
- **Python Backend Developer**: Implements calculation
- **QA Test Engineer**: Creates tests
- **Technical Writer**: Documents the API

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

## Agent Coordination

For complex tasks, Claude coordinates multiple agents:

**Sequential** (one after another):

```
You: "Add peak velocity to CMJ analysis"
→ Biomechanics Specialist: Define metric
→ Backend Developer: Implement calculation
→ QA Engineer: Create tests
→ Technical Writer: Document API
```

**Parallel** (independent work):

```
You: "Optimize video processing"
→ Computer Vision Engineer: Check MediaPipe settings
→ Backend Developer: Profile and optimize code
(Both work independently, results combined)
```

**Validation Chain**:

```
You: "Review this implementation"
→ Backend Developer: Check code quality
→ QA Engineer: Verify tests
→ Biomechanics Specialist: Validate metrics
```

## Tips for Best Results

1. **Be specific**: "The hip landmarks are jittery" vs "Something is wrong"
1. **Mention file names**: "Check src/kinemotion/core/pose.py"
1. **Use domain terms**: "RSI", "MediaPipe", "vectorize", "pytest"
1. **Let Claude choose**: Trust automatic routing for most tasks
1. **Explicit when needed**: Use explicit invocation for edge cases

## Agent Capabilities Summary

| Agent                    | Primary Focus                            | Key Tools                   |
| ------------------------ | ---------------------------------------- | --------------------------- |
| Computer Vision Engineer | MediaPipe, video I/O, pose tracking      | Read, Edit, Bash, WebFetch  |
| Biomechanics Specialist  | Metrics validation, physiology           | Read, Edit, Grep, WebSearch |
| Python Backend Developer | Optimization, architecture, code quality | Read, Edit, Write, Bash     |
| ML/Data Scientist        | Parameter tuning, validation             | Read, Edit, WebFetch        |
| DevOps/CI-CD Engineer    | GitHub Actions, SonarQube, CI            | Read, Edit, Bash            |
| Technical Writer         | Documentation, guides, examples          | Read, Edit, Write           |
| QA/Test Engineer         | Test coverage, edge cases, fixtures      | Read, Edit, Bash            |

## Next Steps

1. **Try it out**: Ask Claude questions and watch agents get selected
1. **View agents**: Run `/agents` to see all available agents
1. **Read details**: Check `.claude/agents/README.md` for full documentation
1. **Customize**: Edit agent prompts to match your preferences

## Troubleshooting

**Agent not auto-selected?**

- Be more specific with keywords
- Mention relevant file names
- Explicitly invoke the agent

**Agent gives wrong advice?**

- Edit agent file to clarify instructions
- Add specific examples to system prompt
- Adjust `description` field for better routing

**Need a new agent?**

- Run `/agents` and select "Create New Agent"
- Let Claude generate initial prompt
- Customize to your needs

## Resources

- [Agent README](.claude/agents/README.md) - Detailed documentation
- [CLAUDE.md](../../CLAUDE.md) - Project overview
- [Claude Code Docs](https://docs.claude.com/en/docs/claude-code/sub-agents) - Official documentation
