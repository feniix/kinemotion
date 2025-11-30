---
title: Using Multiple MCP Reasoning Servers Simultaneously
type: note
permalink: development/using-multiple-mcp-reasoning-servers-simultaneously-1
tags:
- mcp
- configuration
- sequential-thinking
- code-reasoning
- cursor
- claude
---

# Using Multiple MCP Reasoning Servers Simultaneously

## TL;DR
✅ **YES, you can use both sequential-thinking and code-reasoning at the same time**

They run independently in `.mcp.json`. Claude uses its native LLM reasoning to decide which tool is appropriate based on:
1. Tool descriptions and names
2. Your explicit instructions
3. Context of the task
4. Available capabilities

---

## How It Works: The Architecture

### 1. Multiple Servers Run Simultaneously
Each entry in `.mcp.json` creates an **independent MCP server connection**:

```json
{
  "mcpServers": {
    "sequential-thinking": {
      "type": "stdio",
      "command": "bunx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking@2025.7.1"]
    },
    "code-reasoning": {
      "type": "stdio",
      "command": "bunx",
      "args": ["-y", "@mettamatt/code-reasoning"]
    }
  }
}
```

Each server:
- Runs as a separate process
- Provides its own tools
- Maintains its own state
- Has no knowledge of the other

### 2. Claude Reads Available Tools
When Claude starts, it discovers:
- **Tool 1**: `sequential_thinking` (from sequential-thinking server)
- **Tool 2**: `code_reasoning` (from code-reasoning server)

Both tools do similar things but have different prompts internally:
- `sequential-thinking`: Uses original SEQUENTIAL prompt (87%)
- `code-reasoning`: Uses optimized HYBRID_DESIGN prompt (89%)

### 3. Claude Decides Which to Use (Not Algorithmic)
**How Claude chooses:**

Claude uses its **native LLM reasoning**, not hard-coded routing:
- Reads tool descriptions and names
- Understands your request context
- Makes a probabilistic decision about which tool fits best
- Can be guided by explicit instructions

**This is NOT like routing rules** (if request contains "code" → use code-reasoning). It's actual language understanding.

---

## How to Configure Both Servers

### Option 1: Basic Setup (Current Structure)
Add code-reasoning to your existing `.mcp.json`:

```json
{
  "mcpServers": {
    "exa": { ... },
    "ref": { ... },
    "basic-memory": { ... },
    "sequential-thinking": {
      "type": "stdio",
      "command": "bunx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking@2025.7.1"],
      "env": {}
    },
    "code-reasoning": {
      "type": "stdio",
      "command": "bunx",
      "args": ["-y", "@mettamatt/code-reasoning"],
      "env": {}
    },
    "pdf-mcp": { ... },
    "serena": { ... }
  }
}
```

### Option 2: With Custom Names for Clarity
Rename servers to make their purpose clearer to Claude:

```json
{
  "mcpServers": {
    "sequential-thinking-general": {
      "type": "stdio",
      "command": "bunx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking@2025.7.1"]
    },
    "code-reasoning-optimized": {
      "type": "stdio",
      "command": "bunx",
      "args": ["-y", "@mettamatt/code-reasoning"]
    }
  }
}
```

⚠️ **Issue**: Both expose a tool called `sequential_thinking` internally, so Claude might see confusion about which is which.

### Option 3: Use MCP Funnel (Advanced)
If you want a single unified interface:

```json
{
  "mcpServers": {
    "reasoning-hub": {
      "type": "stdio",
      "command": "bunx",
      "args": ["-y", "@chrischris-schra/mcp-funnel"],
      "env": {
        "MCP_SERVERS": "[sequential-thinking, code-reasoning]"
      }
    }
  }
}
```

This aggregates both into one server with filtered tools.

---

## How to Instruct Claude Which to Use

### Option 1: Explicit Instruction (Most Reliable)
Tell Claude directly:

```
For this biomechanics analysis, use the code-reasoning tool
since it's optimized for complex logic. "Use sequential thinking to reason about this."
```

Or:

```
I want to explore multiple solutions. Use sequential thinking to reason about this.
```

### Option 2: System Prompt Hint
Add to your Cursor/Claude system prompt:

```
When the user asks for:
- Code analysis or technical reasoning: prefer code-reasoning server
- General reasoning, planning, or non-code analysis: prefer sequential-thinking
```

### Option 3: Let Claude Decide
Just describe what you need, Claude will choose:

```
"Help me debug this jump detection algorithm"
```
Claude sees both tools available, reads their descriptions, and picks the more appropriate one.

---

## What Happens in Practice

### Scenario 1: User Request
```
"Help me design the CMJ analysis pipeline architecture"
```

Claude's reasoning:
- Available: sequential-thinking, code-reasoning
- Request is about design/planning (not code-specific yet)
- Could use either, but sequential-thinking is better for pure planning
- **Chooses**: sequential-thinking

### Scenario 2: User Request
```
"Debug why the ankle angle calculation is giving wrong values. Use code reasoning."
```

Claude's reasoning:
- User explicitly asked for code reasoning
- Available: code-reasoning with HYBRID_DESIGN (89%)
- **Chooses**: code-reasoning

### Scenario 3: User Request
```
"Think through all the edge cases in the drop jump detection algorithm"
```

Claude's reasoning:
- Both tools are good for this
- Code-reasoning is optimized for code logic
- Sequential-thinking is general-purpose
- Task involves edge cases (code concept)
- **Chooses**: Likely code-reasoning, but could go either way
- **Your hint needed**: "Use sequential thinking to make sure we don't miss non-code edge cases"

---

## Potential Issues & Solutions

### Issue 1: Both Servers Provide `sequential_thinking` Tool
**Problem**: Both expose the same tool name, Claude might get confused

**Solution**:
- Use explicit instructions to clarify
- Add custom wrappers with different names
- Use MCP Funnel to distinguish them

### Issue 2: Latency
**Problem**: Running multiple servers adds slight startup overhead

**Solution**:
- Not significant in practice (< 100ms per server)
- Claude's decision-making happens once per request
- Inactive servers use minimal resources

### Issue 3: Resource Usage
**Problem**: Both servers running means more memory/CPU

**Solution**:
- Sequential-thinking: ~50MB memory
- Code-reasoning: ~50MB memory
- Total: Minimal for Cursor/Claude Code
- Only disable if you're severely constrained

---

## Best Practice for Your Kinemotion Project

### Recommended Setup

```json
{
  "mcpServers": {
    "sequential-thinking": {
      "type": "stdio",
      "command": "bunx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking@2025.7.1"],
      "env": {}
    },
    "code-reasoning": {
      "type": "stdio",
      "command": "bunx",
      "args": ["-y", "@mettamatt/code-reasoning"],
      "env": {}
    }
  }
}
```

### Usage Patterns

1. **For general biomechanics planning**:
   - "Break down the CMJ analysis process for validation"
   - Claude uses: sequential-thinking

2. **For algorithm analysis**:
   - "Debug the triple extension calculation. Use code reasoning."
   - Claude uses: code-reasoning (HYBRID_DESIGN)

3. **For complex reasoning with multiple paths**:
   - "Explore different approaches to detect ground contact. Use sequential thinking to branch."
   - Claude uses: sequential-thinking

4. **For when you're unsure**:
   - Ask naturally, let Claude choose

---

## Key Takeaway

✅ **You can use both simultaneously**
- Each runs independently
- Claude uses LLM reasoning to decide (not routing rules)
- You can guide Claude's choice explicitly
- No conflicts or resource issues for your use case

**Start with both enabled, use explicit instructions when you need specific behavior.**

Next step: Update your `.mcp.json` with both servers and test Claude's behavior with different prompts.
