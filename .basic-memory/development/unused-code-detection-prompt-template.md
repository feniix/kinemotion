---
title: Unused Code Detection Prompt Template
type: note
permalink: development/unused-code-detection-prompt-template
tags:
- code-quality
- maintenance
- automation
- prompts
---

# Unused Code Detection Prompt Template

## Purpose
Reusable prompt for systematically identifying and marking unused code in the kinemotion codebase using serena's semantic analysis tools.

## The Prompt

```
Identify all unused code in src/kinemotion/ and mark it with @unused decorators.

**Context:**
- The project uses @unused and @experimental decorators from src/kinemotion/core/experimental.py
- Strategy document: .basic-memory/development/unused-and-experimental-features-strategy.md
- Previous analysis: .basic-memory/development/unused-code-identification-and-decorator-application-december-2025.md

**Your Task:**

### Phase 1: Load Context
1. Read the unused features strategy to understand the marking approach
2. Read the previous analysis to see what's already marked
3. Use serena's initial_instructions to understand available tools

### Phase 2: Systematic Analysis

For each module in src/kinemotion/:

**2.1 Get Overview**
- Use `serena.get_symbols_overview(relative_path="src/kinemotion/[module]/[file].py")`
- List all public functions (not starting with _)

**2.2 Check Each Function**
For each public function:
- Use `serena.find_referencing_symbols(name_path="function_name", relative_path="src/kinemotion/[module]/[file].py")`
- Verify if it's called anywhere in src/ (not just tests)
- Check if it's exported in __init__.py but not actually used

**2.3 Pattern Search (for functions with no obvious references)**
- Use `serena.search_for_pattern(substring_pattern="function_name", relative_path="src")`
- Look for dynamic calls (getattr, string references)
- Check for indirect usage through decorators or callbacks

**2.4 Test-Only Functions**
- Functions called ONLY in tests/ but never in src/ are candidates for @unused
- Exception: Don't mark if they're part of the public API (exported in __init__.py and documented)

### Phase 3: Verification

For each candidate unused function:

**3.1 Read the Function**
- Use `serena.find_symbol(name_path="function_name", include_body=true)`
- Understand what it does
- Check for TODO comments or integration notes

**3.2 Check Execution Paths**
- Trace the main entry points (CLI, API)
- Verify the function is truly not in any execution path
- Check if it's an alternative implementation or experimental feature

**3.3 Determine Category**
- **@unused**: Complete, working, but not called by pipeline
- **@experimental**: Beta features with unstable APIs (emits warnings)
- **Neither**: Actually used or part of public API

### Phase 4: Apply Decorators

For each confirmed unused function:

**4.1 Add Decorator**
```python
from ..core.experimental import unused

@unused(
    reason="<specific reason why it's unused>",
    since="<version>",
)
def function_name(...):
    ...
```

**4.2 Reason Categories**
- "Alternative implementation not called by pipeline"
- "Copy-pasted from [module], never integrated into [current module] pipeline"
- "Code duplication with [module] version, [current module] version unused"
- "Experimental alternative superseded by [current approach]"
- "CLI refactoring remnant"
- "Awaiting CLI integration"

**4.3 Use serena's editing tools**
- Use `serena.insert_before_symbol()` to add decorator
- Or use `serena.replace_symbol_body()` to add decorator to existing function

### Phase 5: Report

Create a report including:

**5.1 Summary Statistics**
- Total unused functions found
- Breakdown by module (core/, cmj/, dropjump/, etc.)
- Breakdown by category (alternative impl, duplication, experimental, etc.)

**5.2 Detailed Inventory**
For each function:
- Function name and location (file:line)
- Why it's unused
- Whether it has test coverage
- Integration path (if applicable)
- Recommendation (keep, integrate, or remove)

**5.3 Code Quality Issues**
- Any code duplication discovered
- Functions with comprehensive tests but never called (false confidence)
- Exported but unused functions

**5.4 Validation**
- Run all tests: `uv run pytest`
- Check coverage hasn't dropped
- Run linting: `uv run ruff check`
- Run type checking: `uv run pyright`

### Phase 6: Documentation

Update `.basic-memory/development/unused-code-identification-and-decorator-application-december-2025.md` with:
- New findings
- Updated inventory
- Strategic implications for current roadmap phase

## Important Rules

**Do Mark:**
- ✅ Functions with no references in src/ (even if tested)
- ✅ Functions only exported but never called
- ✅ Alternative implementations not in production pipeline
- ✅ Code duplicated across modules where only one version is used

**Don't Mark:**
- ❌ Private helper functions (starting with _) that are called internally
- ❌ Functions used in tests if they're part of documented public API
- ❌ CLI entry points (even if simple wrappers)
- ❌ API entry points in api.py
- ❌ Functions called indirectly (callbacks, dynamic dispatch) - verify first

**Conservative Approach:**
- When in doubt, investigate deeper before marking
- Use `serena.find_referencing_symbols()` exhaustively
- Trace through main entry points manually
- False positives are worse than false negatives

## Tools Reference

**Serena Tools:**
- `initial_instructions` - Read serena manual
- `get_symbols_overview(relative_path)` - List top-level symbols
- `find_symbol(name_path, relative_path, include_body)` - Get function details
- `find_referencing_symbols(name_path, relative_path)` - Find all references
- `search_for_pattern(substring_pattern, relative_path)` - Regex search
- `insert_before_symbol()` - Add decorator
- `replace_symbol_body()` - Replace function with decorator

**Basic Memory Tools:**
- `read_note()` - Load strategy and previous analysis
- `write_note()` - Save findings
- `edit_note()` - Update existing documentation

**Sequential Thinking:**
- Use for complex decisions about whether code is truly unused
- Break down verification into steps
- Consider alternative hypotheses

## Example Output

```markdown
## Unused Code Analysis Report

**Date:** [current date]
**Total Found:** X functions
**Previously Marked:** Y functions
**Newly Marked:** Z functions

### Summary by Module

**core/** - N functions
- `function_1()` - Alternative implementation
- `function_2()` - CLI remnant

**cmj/** - N functions
- `function_3()` - Copy-pasted from dropjump, unused

**dropjump/** - N functions
- `function_4()` - Experimental feature

### Key Discoveries

[Notable patterns, code duplication issues, test coverage anomalies]

### Validation

✅ All tests pass
✅ Coverage: X%
✅ 0 linting errors
✅ 0 type errors

### Files Modified

- src/kinemotion/[module]/[file].py - N decorators added

### Recommendations

**Phase 1 (Current):**
- Keep all marked but don't remove
- Focus on [priorities]

**Phase 2 (Post-MVP):**
- Integrate if market demands: [list]
- Refactor to eliminate duplication: [list]

**v1.0.0:**
- Remove unused functions: [list]
```

## Verification Checklist

Before finalizing:

- [ ] Every public function in src/ has been checked
- [ ] All functions with @unused have clear reasons
- [ ] Test suite still passes
- [ ] Coverage hasn't dropped
- [ ] No false positives (actually used functions marked)
- [ ] Documentation updated
- [ ] Commit created with conventional commit format

## Related Documents

- `src/kinemotion/core/experimental.py` - Decorator implementations
- `.basic-memory/development/unused-and-experimental-features-strategy.md` - Strategy
- `.basic-memory/development/unused-code-identification-and-decorator-application-december-2025.md` - Latest analysis
- `CLAUDE.md` - Project standards and guidelines
```

## How to Use This Prompt

1. **Copy the prompt** from the code block above
2. **Paste it** into your conversation with Claude Code
3. **Optional:** Add context like "Focus on module X" or "Quick scan only"
4. **Let the agent work** through all phases systematically

## Tips for Best Results

- Run after major refactoring or feature additions
- Schedule quarterly as part of code quality reviews
- Use with python-backend-developer agent for best results
- Allow time for thorough analysis (15-30 minutes for full codebase)
- Review findings before applying decorators en masse
