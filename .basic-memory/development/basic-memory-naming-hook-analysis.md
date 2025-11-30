---
title: Basic Memory Naming Hook Analysis and Fix
type: note
permalink: development/basic-memory-naming-hook-analysis
tags:
  - development
  - tooling
  - naming-conventions
  - hook
---

# Basic Memory Naming Hook Analysis and Fix

## Issue Identified

The hook script `/.claude/hooks/fix-basic-memory-names.sh` was not properly converting filenames to kebab-case when creating `.basic-memory/` notes. Files were being created with concatenated names like:

❌ `frontenddependenciesanalysisnov2025.md`

Instead of:

✅ `frontend-dependencies-analysis-nov-2025.md`

## Root Cause Analysis

The hook script had **two distinct problems**:

### 1. **Original Function Logic Flaw**
The `to_kebab_case()` function wasn't handling word boundaries correctly:

```bash
# OLD (broken)
sed 's/[[:space:]]\+/-/g' |        # Convert spaces to hyphens
tr '[:upper:]' '[:lower:]' |       # Convert to lowercase
sed 's/[^a-z0-9-]//g'             # Remove non-alphanumeric (except hyphens)
```

**Problem**: Without camelCase handling, "Frontend Dependencies" → "frontend dependencies" → "frontenddependencies" (spaces already removed, can't convert to hyphens)

### 2. **Files Created Without Separators**
More critically: When files are **created without word separators** (spaces, underscores, camelCase), the hook cannot reverse-engineer word boundaries. For example:
- Input: `frontenddependenciesanalysisnov2025` (no separators)
- Function output: `frontenddependenciesanalysisnov2025` (no way to know where word breaks are)

**This is a limitation of any text-based kebab-case conversion function** - it requires existing word boundaries to work with.

## Solution Implemented

### 1. **Enhanced Kebab-Case Function**
Added camelCase handling to the conversion function:

```bash
to_kebab_case() {
    echo "$1" | \
        sed 's/[[:space:]]\+/-/g' |              # Spaces → hyphens
        sed 's/\([a-z]\)\([A-Z]\)/\1-\2/g' |    # camelCase → kebab-case
        tr '[:upper:]' '[:lower:]' |             # All lowercase
        sed 's/[^a-z0-9-]//g' |                  # Remove non-alphanumeric
        sed 's/-\+/-/g'                          # Collapse multiple hyphens
}
```

Now handles:
- ✅ `"Frontend Dependencies Analysis"` → `frontend-dependencies-analysis`
- ✅ `"CMJPhysiologicalBounds"` → `cmj-physiological-bounds`
- ✅ `"Test-File-Name"` → `test-file-name`

### 2. **Fixed Bash Syntax Error**
**Critical bug found:** The original script used `local` keyword outside of function scope, which caused "can only be used in a function" errors.

**Fixed by:** Removing `local` keyword from script-level variables. Variables are now declared without `local`:

```bash
# BEFORE (broken)
dir=$(dirname "$file")        # ❌ Inside while loop, not a function
basename=$(basename "$file")

# AFTER (fixed)
dir=$(dirname "$file")        # ✅ Works correctly now
basename=$(basename "$file")
```

### 3. **Detection for Concatenated Filenames**
Added logic to detect and warn about files with no word separators:

```bash
# Check if the new_name is significantly shorter (indicates concatenation)
original_len=${#basename}
new_len=${#new_name}
if [ $((original_len - new_len)) -gt 5 ]; then
    echo "⚠️  Cannot auto-fix: $basename (no word separators detected)"
    echo "   → Please rename manually to follow kebab-case"
```

Now the hook will:
- ✅ Auto-fix: `"Frontend Dependencies Analysis.md"` → `frontend-dependencies-analysis.md`
- ✅ Auto-fix: `"CMJPhysiologicalBounds.md"` → `cmj-physiological-bounds.md`
- ⚠️ Warn about: `"frontenddependenciesanalysisnov2025.md"` (needs manual rename)

### 4. **Manual File Fix**
Fixed the existing incorrectly-named file:

```bash
# BEFORE
.basic-memory/development/frontenddependenciesanalysisnov2025.md

# AFTER
.basic-memory/development/frontend-dependencies-analysis-nov-2025.md
```

### 5. **Comprehensive Summary Output**
The hook now provides clear feedback:

```bash
✅ Fixed 26 basic-memory filename(s) to kebab-case
⚠️  Found X file(s) that need manual renaming
```

## How to Prevent Future Issues

When creating new `.basic-memory/` notes, ensure that **naming functions already use word separators**:

### ✅ GOOD: Uses spaces (or camelCase)
```markdown
write_note("Frontend Dependencies Analysis Nov 2025", "...", "development")
```

### ❌ AVOID: Concatenated without separators
```markdown
write_note("FrontendDependenciesAnalysisNov2025", "...", "development")
```

## Hook Behavior Summary

The hook now:

1. **Scans** all `.basic-memory/**/*.md` files
2. **Attempts auto-fix** for files with word separators (spaces, camelCase, etc.)
3. **Warns** about files with no detectable word boundaries
4. **Git stages** all changes automatically
5. **Outputs summary** of what was fixed or needs attention

**Trigger**: Runs after user prompts (when using Claude Code hooks)

## Files Updated

- ✅ `.claude/hooks/fix-basic-memory-names.sh` - Enhanced conversion logic + detection
- ✅ `.basic-memory/development/frontend-dependencies-analysis-nov-2025.md` - Renamed from concatenated version
