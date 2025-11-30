#!/bin/bash
# Claude Code Hook: Auto-fix basic-memory filename naming convention
# This hook runs when users submit prompts to ensure all .basic-memory/ files follow kebab-case naming
# Triggered on: UserPromptSubmit hook event
# Reference: https://docs.claude.com/en/docs/claude-code/hooks-guide

set -euo pipefail

# Error handling
handle_error() {
    local line_num=$1
    echo "❌ Hook error on line $line_num" >&2
    exit 1
}
trap 'handle_error $LINENO' ERR

# Debug logging (set DEBUG=1 to enable)
DEBUG="${DEBUG:-0}"
debug_log() {
    if [ "$DEBUG" = "1" ]; then
        echo "[DEBUG] $*" >&2
    fi
}

# Convert Title Case and mixed case to kebab-case
# Handles: spaces, camelCase, multiple hyphens
# Examples:
#   "Frontend Dependencies Analysis" → "frontend-dependencies-analysis"
#   "CMJPhysiologicalBounds" → "cmj-physiological-bounds"
#   "Test-File-Name" → "test-file-name"
to_kebab_case() {
    echo "$1" | \
        sed -E 's/[[:space:]]+/-/g' |              # Spaces → hyphens
        sed 's/\([a-z]\)\([A-Z]\)/\1-\2/g' |    # camelCase → kebab-case (e.g. myName → my-Name)
        tr '[:upper:]' '[:lower:]' |             # All to lowercase
        sed 's/[^a-z0-9-]//g' |                  # Remove non-alphanumeric (except hyphens)
        sed -E 's/-+/-/g'                        # Collapse multiple hyphens
}

# Check if .basic-memory directory exists
if [ ! -d ".basic-memory" ]; then
    debug_log "No .basic-memory directory found, skipping"
    exit 0
fi

debug_log "Starting basic-memory filename normalization"

# Find and fix improperly named files
fixed_count=0
warned_count=0
error_count=0

while IFS= read -r file; do
    if [ ! -f "$file" ]; then
        debug_log "Skipping non-existent file: $file"
        continue
    fi

    dir=$(dirname "$file")
    basename=$(basename "$file")
    new_name=$(to_kebab_case "${basename%.md}")
    new_path="${dir}/${new_name}.md"

    if [ "$file" != "$new_path" ]; then
        # Check if the new_name is significantly shorter (indicates concatenation without separators)
        basename_no_ext="${basename%.md}"
        original_len=${#basename_no_ext}
        new_len=${#new_name}

        if [ $((original_len - new_len)) -gt 5 ]; then
            echo "⚠️  Cannot auto-fix: $basename"
            echo "   Reason: No word separators detected"
            echo "   Action: Rename manually to follow kebab-case (e.g., my-file-name.md)"
            ((warned_count++))
            debug_log "Warned about: $file (no separators)"
        else
            debug_log "Fixing: $file → $new_path"

            # Stage the old file for deletion
            git rm --cached "$file" 2>/dev/null || true

            # Rename the file
            if mv "$file" "$new_path"; then
                # Stage the new file
                git add "$new_path" 2>/dev/null || true
                ((fixed_count++))
                debug_log "Successfully fixed: $new_path"
            else
                echo "❌ Failed to rename: $file"
                ((error_count++))
            fi
        fi
    fi
done < <(find .basic-memory -name "*.md" -type f 2>/dev/null || true)

debug_log "Scan complete: fixed=$fixed_count warned=$warned_count errors=$error_count"

# Output summary
if [ $fixed_count -gt 0 ]; then
    echo "✅ Fixed $fixed_count basic-memory filename(s) to kebab-case"
fi

if [ $warned_count -gt 0 ]; then
    echo "⚠️  Found $warned_count file(s) that need manual renaming (no word separators)"
fi

if [ $error_count -gt 0 ]; then
    echo "❌ Encountered $error_count error(s) during file operations"
fi

# Exit with appropriate code
if [ $error_count -gt 0 ]; then
    exit 1  # Signal failure if there were errors
fi

exit 0
