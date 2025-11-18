# Basic Memory: Knowledge Base Guidelines

This directory contains your project's persistent knowledge base using [Basic Memory](https://github.com/basicmachines-co/basic-memory). Notes are stored as Markdown files and indexed in a SQLite database, enabling AI assistants to read, write, and traverse your knowledge graph.

## Quick Start

**Creating a note:**
```
"Create a note about [topic] in the [folder] folder"
```

**Reading notes:**
```
"What do I know about [topic]?"
"Find information about [subject]"
```

**Searching:**
```
"Search for [keyword] in my notes"
"Build context from memory://biomechanics/*"
```

## File Organization

Your knowledge base is organized into folders by domain:

### `api/` - API Reference
Quick commands and API documentation for kinemotion. Useful for implementation reference during coding.

- `api-reference-quick-commands.md` - CLI and Python API quick reference

### `biomechanics/` - Jump Biomechanics
Physiological data, metric definitions, and validation bounds for jump analysis.

- `cmj-physiological-bounds-for-validation.md` - Valid ranges for CMJ metrics
- `cmj-validation-implementation-complete.md` - Validation framework delivery
- `drop-jump-vs-cmj-key-differences.md` - Comparison of jump types

### `codebase/` - Architecture
High-level codebase structure, module relationships, and design patterns.

- `codebase-architecture-overview.md` - Module structure and design decisions

### `development/` - Quality Standards
Testing standards, coverage requirements, and code quality guidelines.

- `development-standards-quality-gates.md` - Quality gates and standards
- `cmj-phase-detection-testing-gap-analysis.md` - Test coverage analysis

### `project-management/` - Task Routing
Guidance on which specialized agent to use for different task types.

- `specialized-subagents-routing-guide.md` - When to use each agent

### `strategy/` - Roadmap
Strategic priorities, feature roadmap, and long-term planning.

- `strategic-priority-tasks-current-roadmap.md` - Current roadmap and priorities

## Naming Standards

**All files must follow lowercase kebab-case:**

```
✓ GOOD:
  cmj-physiological-bounds-for-validation.md
  api-reference-quick-commands.md
  drop-jump-vs-cmj-key-differences.md

✗ BAD:
  CMJ Physiological Bounds.md
  API_REFERENCE.md
  drop jump info.md
```

Why? Kebab-case is URL-friendly, consistent, and works with basic-memory's memory:// URLs and CLI.

## Note Template

Every note should follow this structure:

```markdown
---
title: Human-Readable Title (Can Use Title Case)
type: note
permalink: folder/lowercase-kebab-case-matching-filename
tags:
  - tag1
  - tag2
---

# Main Heading

## Overview or Summary
Brief description of what this note covers.

## Section 1
Content...

## Section 2
Content...

## Relations
Links to related topics using basic-memory wiki-link format:
- relates_to [[Other Topic]]
- requires [[Prerequisites]]
- documented_in [[Reference Note]]
```

## Observations Format

Use structured observations to capture facts about a topic:

```markdown
## Key Findings

- [metric] Flight time ranges from 0.4-0.8 seconds for elite athletes
- [formula] Jump height = g·t²/8 where t is flight time
- [validation] Bounds prevent false positives from noise
- [implementation] Added to cmj_validation_bounds.py module
```

Format: `- [category] content #tag (optional context)`

**Common categories:**
- `[metric]` - Measurements and ranges
- `[formula]` - Mathematical relationships
- `[validation]` - Bounds and constraints
- `[implementation]` - Code references
- `[finding]` - Research discoveries
- `[principle]` - Biomechanical principles
- `[caution]` - Important gotchas

## Relations Format

Link notes together to build your knowledge graph:

```markdown
## Relations

- relates_to [[CMJ Analysis Algorithm]]
- requires [[MediaPipe Pose Detection]]
- depends_on [[Kinematic Calculations]]
- documented_in [[Technical Reference]]
- improves [[Triple Extension Tracking]]
```

## Creating a New Note

1. **Choose the right folder** based on topic domain
2. **Create filename in kebab-case** (lowercase, hyphens between words)
3. **Use the template above** with proper frontmatter
4. **Add meaningful tags** for searchability
5. **Link related topics** using wiki-link format
6. **Include observations** with structured categories

**Example workflow:**

```bash
# AI assistant will handle this, but here's what happens:
1. File created: .basic-memory/biomechanics/new-cmj-finding.md
2. Frontmatter added with permalink: biomechanics/new-cmj-finding
3. Content structured with observations and relations
4. SQLite database updated for search indexing
5. Note immediately accessible via search or build_context()
```

## Accessing Your Knowledge

**In Claude Desktop or Claude Code:**

```python
# Load all biomechanics notes
build_context("memory://biomechanics/*")

# Read a specific note
read_note("cmj-physiological-bounds-for-validation")

# Search across all notes
search_notes("flight time validation")

# Get recent activity
recent_activity(type="notes", timeframe="7d")
```

## Best Practices

1. **Keep notes focused** - One main topic per note
2. **Use descriptive titles** - Clear, searchable titles
3. **Add tags consistently** - Use same tags across related notes
4. **Link heavily** - Connect related concepts via wiki-links
5. **Update regularly** - Keep knowledge current as you learn
6. **Write for future you** - Assume you won't remember context
7. **Use observations** - Structured facts are more queryable

## Syncing with Cloud (Optional)

If using basic-memory cloud sync:

```bash
# One-time sync of local changes
basic-memory sync

# Real-time sync watcher (recommended)
basic-memory sync --watch

# Authenticate with cloud
basic-memory cloud login

# Bidirectional cloud sync
basic-memory cloud sync
```

## Common Tasks

**Add findings from a coding session:**
```
"Create a note in the development folder about [what you discovered]"
```

**Review quality standards before commit:**
```
"Show me the development standards and quality gates"
```

**Load context for new feature work:**
```
"Build context from memory://strategy/* and memory://codebase/*"
```

**Find validation bounds for CMJ:**
```
"What are the physiological bounds for CMJ metrics?"
```

## Files in This Directory

- `README.md` - This file
- `api/` - API reference folder
- `biomechanics/` - Biomechanics notes folder
- `codebase/` - Architecture notes folder
- `development/` - Quality standards folder
- `project-management/` - Task routing folder
- `strategy/` - Roadmap folder

Each folder contains markdown notes organized by topic domain.

## For More Information

- [Basic Memory Documentation](https://memory.basicmachines.co/)
- [Basic Memory GitHub](https://github.com/basicmachines-co/basic-memory)
- Project: See [CLAUDE.md](../CLAUDE.md) for complete project instructions
