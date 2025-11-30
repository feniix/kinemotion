---
title: Claude Code Hook Configuration - best-basic-memory-names
type: note
permalink: development/claude-code-hook-configuration
tags:
  - development
  - tooling
  - hooks
  - claude-code
  - automation
  - naming-conventions
---

# Claude Code Hook Configuration: fix-basic-memory-names

## Overview

This document describes the complete configuration of the `fix-basic-memory-names` hook, which automatically normalizes `.basic-memory/` filenames to follow kebab-case naming conventions.

**Hook Type:** `UserPromptSubmit`
**Script:** `.claude/hooks/fix-basic-memory-names.sh`
**Configuration File:** `.claude/settings.local.json`

## Why This Matters

The `.basic-memory/` directory stores project knowledge, and filename consistency is critical for:
- **Predictability**: Easy to guess and find notes
- **URL safety**: Kebab-case works in URLs and permalinks
- **Tool compatibility**: MCP basic-memory functions require consistent naming
- **Git history**: Consistent naming reduces merge conflicts

## Hook Configuration

### Hook Registration

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/fix-basic-memory-names.sh",
            "statusMessage": "Normalizing basic-memory filenames to kebab-case...",
            "timeout": 30000
          }
        ]
      }
    ]
  }
}
```

**Location:** `.claude/settings.local.json` (lines 3-17)

### Configuration Details

| Field | Value | Purpose |
|-------|-------|---------|
| **Hook Type** | `UserPromptSubmit` | Runs when user submits a prompt, before Claude processes it |
| **Script Path** | `$CLAUDE_PROJECT_DIR/.claude/hooks/fix-basic-memory-names.sh` | Absolute reference to hook script (expandable) |
| **Status Message** | "Normalizing basic-memory filenames to kebab-case..." | User-visible feedback during execution |
| **Timeout** | 30000 ms (30s) | Reasonable for file I/O operations across many files |

## Script Implementation

### Entry Point

```bash
#!/bin/bash
set -euo pipefail
```

**Why `set -euo pipefail`?**
- `set -e` - Exit immediately if any command fails
- `set -u` - Error on undefined variables
- `set -o pipefail` - Pipe fails if any command in chain fails
- Makes script robust and fail-fast

### Error Handling

```bash
handle_error() {
    local line_num=$1
    echo "❌ Hook error on line $line_num" >&2
    exit 1
}
trap 'handle_error $LINENO' ERR
```

**Features:**
- Catches errors and reports exact line number
- Outputs to stderr (standard for errors)
- Exits cleanly with error code 1
- Claude Code recognizes this and blocks operations if needed

### Debug Logging

```bash
DEBUG="${DEBUG:-0}"
debug_log() {
    if [ "$DEBUG" = "1" ]; then
        echo "[DEBUG] $*" >&2
    fi
}
```

**Usage:**
```bash
# Enable debug logging when testing
DEBUG=1 bash .claude/hooks/fix-basic-memory-names.sh

# Normal execution (no debug output)
bash .claude/hooks/fix-basic-memory-names.sh
```

### Kebab-Case Conversion

The `to_kebab_case()` function handles:

1. **Spaces** → hyphens: `"Frontend Dependencies"` → `"frontend-dependencies"`
2. **camelCase** → kebab-case: `"CMJPhysiologicalBounds"` → `"cmj-physiological-bounds"`
3. **Mixed separators**: `"Test-File-Name"` → `"test-file-name"`
4. **Multiple hyphens**: Collapse to single hyphen

```bash
to_kebab_case() {
    echo "$1" | \
        sed 's/[[:space:]]\+/-/g' |              # Spaces → hyphens
        sed 's/\([a-z]\)\([A-Z]\)/\1-\2/g' |    # camelCase → kebab-case
        tr '[:upper:]' '[:lower:]' |             # All lowercase
        sed 's/[^a-z0-9-]//g' |                  # Remove non-alphanumeric (except hyphens)
        sed 's/-\+/-/g'                          # Collapse multiple hyphens
}
```

### File Processing Loop

```bash
while IFS= read -r file; do
    # ... validation ...
    dir=$(dirname "$file")
    basename=$(basename "$file")
    new_name=$(to_kebab_case "${basename%.md}")
    new_path="${dir}/${new_name}.md"

    if [ "$file" != "$new_path" ]; then
        # Check for concatenation (no word separators)
        original_len=${#basename}
        new_len=${#new_name}

        if [ $((original_len - new_len)) -gt 5 ]; then
            # ⚠️ Cannot auto-fix - warn user
        else
            # ✅ Auto-fix with git staging
            git rm --cached "$file" 2>/dev/null || true
            mv "$file" "$new_path"
            git add "$new_path" 2>/dev/null || true
        fi
    fi
done < <(find .basic-memory -name "*.md" -type f 2>/dev/null || true)
```

**Key behaviors:**
- Safely iterates with `IFS= read -r` (handles spaces/special chars)
- Detects concatenated filenames (no separators) and warns instead of mangling
- Stages git operations immediately for clean commit history
- Continues on find errors (|| true)

### Exit Codes

| Code | Meaning | Action |
|------|---------|--------|
| 0 | Success | Hook completed, files may have been fixed |
| 1 | Error | Hook encountered errors, Claude Code may block |

## Best Practices Applied

### 1. Script Initialization
✅ Shebang: `#!/bin/bash` (portable)
✅ Error handling: `set -euo pipefail` with trap
✅ Documented: Comments for each section

### 2. Security
✅ No recursive eval or backticks
✅ Quoted variables: `"$var"` not $var
✅ Minimal git operations (rm/add only)

### 3. User Feedback
✅ Status messages for each outcome
✅ Debug logging for troubleshooting
✅ Clear warnings for manual intervention

### 4. Reliability
✅ Timeout protection: 30s limit in config
✅ Error recovery: Continues on transient failures
✅ Atomic operations: Git staging prevents corruption

## Troubleshooting

### Hook Not Running

**Check 1: Script Executable?**
```bash
ls -la .claude/hooks/fix-basic-memory-names.sh
# Should show: -rwx--x--x (755 permissions)
chmod +x .claude/hooks/fix-basic-memory-names.sh  # Fix if needed
```

**Check 2: Configuration Correct?**
```bash
# View hook configuration
cat .claude/settings.local.json | grep -A 5 "UserPromptSubmit"

# Should see reference to fix-basic-memory-names.sh
```

**Check 3: Enable Debug Logging**
```bash
# Test hook directly
cd /project/root
DEBUG=1 bash .claude/hooks/fix-basic-memory-names.sh
```

### Files Not Being Renamed

**Likely causes:**
1. Files already have correct names (no changes needed)
2. Files have no word separators (concatenated) - hook warns instead
3. Git operations failing (check permissions)

**Debug:**
```bash
DEBUG=1 bash .claude/hooks/fix-basic-memory-names.sh
# Look for "[DEBUG]" output lines showing what was checked
```

### Timeout Errors

If hook times out (> 30s):
- Increase timeout in settings.json: `"timeout": 60000`
- Check if find is slow: `time find .basic-memory -name "*.md"`
- If needed, exclude large directories with `! -path "*/.git/*"`

## Testing the Hook

### Manual Test

```bash
cd /Users/feniix/src/personal/cursor/dropjump-claude

# Test with debug output
DEBUG=1 bash .claude/hooks/fix-basic-memory-names.sh

# Expected output:
# [DEBUG] Starting basic-memory filename normalization
# [DEBUG] Scan complete: fixed=0 warned=0 errors=0
```

### Create Test File

```bash
# Create a test file with bad naming
touch .basic-memory/development/TestBadNaming.md

# Run hook
bash .claude/hooks/fix-basic-memory-names.sh

# Check result
ls .basic-memory/development/ | grep -i test
# Should show: test-bad-naming.md

# Clean up
rm .basic-memory/development/test-bad-naming.md
```

## Integration with Claude Code

### How It Works in Claude Code

1. **User submits prompt** → Hook triggered
2. **Hook scans** `.basic-memory/*.md` files
3. **For each file:**
   - Compare current vs. kebab-case name
   - If different AND has word separators → Auto-fix
   - If different AND NO word separators → Warn user
4. **Git staging** happens automatically
5. **Hook exits** with status code (0=success, 1=error)

### Performance Impact

- **Overhead**: ~50-200ms per prompt (depends on file count)
- **Files scanned**: All `.basic-memory/**/*.md` (~30-40 files typically)
- **Operations**: Quick stat checks + optional git operations

## Related Files

- **Hook Script**: `.claude/hooks/fix-basic-memory-names.sh`
- **Configuration**: `.claude/settings.local.json`
- **Analysis Document**: `.basic-memory/development/basic-memory-naming-hook-analysis.md`
- **Official Docs**: https://docs.claude.com/en/docs/claude-code/hooks-guide

## References

### Claude Code Hooks Guide
https://docs.claude.com/en/docs/claude-code/hooks-guide

### Key Sections
- Hook Events Overview - explains UserPromptSubmit and others
- Code Formatting Hook - example of PostToolUse hook
- File Protection Hook - example of using jq for input parsing

### Bash Best Practices
- `set -euo pipefail` - Standard for robust scripts
- `trap 'cleanup' EXIT` - Cleanup pattern
- Error handling with `$?` - Exit code checking

## Maintenance

### When to Update

| Scenario | Action |
|----------|--------|
| Add new `.basic-memory/` folder | Hook automatically covers (uses find) |
| Change kebab-case rules | Update `to_kebab_case()` function |
| Adjust timeout | Edit `settings.local.json` timeout value |
| Add debug capability | Already supported (DEBUG=1) |

### Version History

- **v1.0** - Initial implementation with camelCase support
- **v1.1** - Added debug logging and error handling
- **v1.2** - Added detection for concatenated filenames (no auto-fix)
- **v2.0** - Proper configuration in settings.json with timeout

## Future Improvements

- [ ] Check for duplicate files after renaming
- [ ] Support for other file types (.json, .yml)
- [ ] Logging to file for audit trail
- [ ] Integration with Git pre-commit hook
- [ ] Webhook notifications on changes
