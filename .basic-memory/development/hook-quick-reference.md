---
title: Hook Quick Reference - Deployment & Debugging
type: note
permalink: development/hook-quick-reference
tags:
  - development
  - hooks
  - quick-reference
  - troubleshooting
  - deployment
---

# Hook Quick Reference

**Hook Name**: `fix-basic-memory-names.sh`
**Type**: `UserPromptSubmit`
**Status**: ✅ Production Ready

## One-Line Summary

Automatically normalizes `.basic-memory/` filenames to kebab-case whenever you submit a prompt in Claude Code.

## Key Files

| File | Purpose | Permissions |
|------|---------|-------------|
| `.claude/hooks/fix-basic-memory-names.sh` | Main hook script | 755 (rwx--x--x) |
| `.claude/settings.local.json` | Hook configuration | 644 (rw-r--r--) |
| `.basic-memory/development/` | Documentation | Various |

## Hook Configuration (settings.local.json)

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

## What It Does

| Input | Output | Example |
|-------|--------|---------|
| Spaces + capitals | kebab-case | `Frontend Dependencies Analysis` → `frontend-dependencies-analysis` |
| camelCase | kebab-case | `CMJPhysiologicalBounds` → `cmj-physiological-bounds` |
| Mixed separators | Clean kebab | `Test-File-Name` → `test-file-name` |
| No separators | Warning + skip | `frontenddependenciesanalysis` → ⚠️ warn user |

## Quick Start

### Test the Hook

```bash
# Test with debug output
cd /Users/feniix/src/personal/cursor/dropjump-claude
DEBUG=1 bash .claude/hooks/fix-basic-memory-names.sh

# Should output:
# [DEBUG] Starting basic-memory filename normalization
# [DEBUG] Scan complete: fixed=0 warned=0 errors=0
```

### Check if Executable

```bash
ls -la .claude/hooks/fix-basic-memory-names.sh
# Should show: -rwx--x--x (755 permissions)

# Fix if needed:
chmod +x .claude/hooks/fix-basic-memory-names.sh
```

### View Configuration

```bash
cat .claude/settings.local.json | grep -A 8 "UserPromptSubmit"
```

## Troubleshooting

### Problem: Hook Not Running

**Check 1**: Is the script executable?
```bash
test -x .claude/hooks/fix-basic-memory-names.sh && echo "✅ Executable" || echo "❌ Not executable"
```

**Check 2**: Is settings.json valid?
```bash
jq . .claude/settings.local.json > /dev/null && echo "✅ Valid JSON" || echo "❌ Invalid JSON"
```

**Check 3**: Is Claude Code recognizing the hook?
```bash
# Look for the status message when you submit a prompt
# You should see: "Normalizing basic-memory filenames to kebab-case..."
```

### Problem: Files Not Being Renamed

**Likely Reason 1**: Files already have correct names (nothing to do)
```bash
ls .basic-memory/*/  # Check current names
```

**Likely Reason 2**: Files have no word separators (intentionally skipped)
```bash
DEBUG=1 bash .claude/hooks/fix-basic-memory-names.sh 2>&1 | grep "Cannot auto-fix"
```

**Likely Reason 3**: Git operations failing (permissions)
```bash
cd .basic-memory && git status
```

### Problem: Hook Takes Too Long (Timeout)

**Check 1**: How many markdown files?
```bash
find .basic-memory -name "*.md" | wc -l
# Each file takes ~10ms, so 100 files = ~1 second
```

**Check 2**: Increase timeout if needed
```json
"timeout": 60000  // Changed from 30000 to 60 seconds
```

**Check 3**: Profile the script
```bash
time DEBUG=1 bash .claude/hooks/fix-basic-memory-names.sh
```

## Enabling Debug Mode

To see what the hook is doing:

```bash
# Run with debug enabled
DEBUG=1 bash .claude/hooks/fix-basic-memory-names.sh

# Output includes:
# [DEBUG] Starting basic-memory filename normalization
# [DEBUG] Fixing: .basic-memory/dev/test.md → .basic-memory/dev/test-name.md
# [DEBUG] Successfully fixed: .basic-memory/dev/test-name.md
# [DEBUG] Scan complete: fixed=1 warned=0 errors=0
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success (hook completed) |
| 1 | Error (hook failed) |

Claude Code interprets non-zero exit codes as failures and may block operations.

## Normal Output

```
✅ Fixed 2 basic-memory filename(s) to kebab-case
```

## Warning Output

```
⚠️  Cannot auto-fix: frontenddependenciesanalysis.md
   Reason: No word separators detected
   Action: Rename manually to follow kebab-case (e.g., my-file-name.md)
```

## Naming Rules

### ✅ GOOD - Use word separators

```
- Frontend Dependencies Analysis → frontend-dependencies-analysis.md
- CMJ Physiological Bounds → cmj-physiological-bounds.md
- API Reference Quick Commands → api-reference-quick-commands.md
- Test-File-Name → test-file-name.md
```

### ❌ AVOID - No separators

```
- frontenddependenciesanalysis (will get warning)
- CMJPhysiologicalBounds (will get warning)
- myfilename (will get warning)
```

Use camelCase or spaces or hyphens - at least ONE word separator!

## Performance

| Scenario | Time | Impact |
|----------|------|--------|
| 0-10 files | 50ms | Unnoticeable |
| 10-50 files | 150ms | Unnoticeable |
| 50-100 files | 300ms | Slightly noticeable |
| 100+ files | 500ms+ | May approach timeout |

**Timeout**: 30 seconds (30000ms) - plenty of margin

## Related Documentation

📖 **Detailed Configuration**: `.basic-memory/development/claude-code-hook-configuration.md`
🔍 **Audit Report**: `.basic-memory/development/hook-configuration-audit.md`
📋 **Analysis**: `.basic-memory/development/basic-memory-naming-hook-analysis.md`

## Need Help?

### Check the Script
```bash
cat .claude/hooks/fix-basic-memory-names.sh
# Well-commented, each section explains what it does
```

### Check the Configuration
```bash
cat .claude/settings.local.json
# Search for "UserPromptSubmit" section
```

### Run With Debug
```bash
DEBUG=1 bash .claude/hooks/fix-basic-memory-names.sh 2>&1 | less
# Shows exactly what the hook is doing
```

### Create a Test File
```bash
# Create a badly named file
mkdir -p .basic-memory/test
touch .basic-memory/test/TestBadName.md

# Run the hook
bash .claude/hooks/fix-basic-memory-names.sh

# Check result
ls .basic-memory/test/
# Should show: test-bad-name.md

# Clean up
rm -rf .basic-memory/test/
```

## Important Notes

⚠️ **The hook runs BEFORE Claude processes your prompt**
- Naming fixes happen silently
- You'll see "Normalizing basic-memory filenames..." status message
- Takes <1 second for typical usage

✅ **Git integration is automatic**
- File renames are staged immediately
- Next commit will include renamed files
- Clean history for project

🔒 **Security**
- Runs with your user permissions only
- No sudo or escalation required
- Only touches `.basic-memory/` directory

## Last Updated

November 29, 2025

**Version**: 2.0
**Status**: Production Ready ✅
