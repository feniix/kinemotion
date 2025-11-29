#!/bin/bash
# Claude Code Hook: Auto-fix basic-memory filename naming convention
# This hook runs after user prompts to ensure all .basic-memory/ files follow kebab-case naming
# Triggered on: user-prompt-submit

# Convert Title Case to kebab-case
to_kebab_case() {
    echo "$1" | \
        sed 's/[[:space:]]\+/-/g' | \
        tr '[:upper:]' '[:lower:]' | \
        sed 's/[^a-z0-9-]//g'
}

# Check if .basic-memory directory exists
if [ ! -d ".basic-memory" ]; then
    exit 0
fi

# Find and fix improperly named files
fixed_count=0
while IFS= read -r file; do
    if [ -f "$file" ]; then
        local dir=$(dirname "$file")
        local basename=$(basename "$file")
        local new_name=$(to_kebab_case "${basename%.md}")
        local new_path="${dir}/${new_name}.md"

        if [ "$file" != "$new_path" ]; then
            # Stage the old file for deletion
            git rm --cached "$file" 2>/dev/null || true

            # Rename the file
            mv "$file" "$new_path"

            # Stage the new file
            git add "$new_path" 2>/dev/null || true

            ((fixed_count++))
        fi
    fi
done < <(find .basic-memory -name "*.md" -type f)

# If files were fixed, exit with 1 to indicate changes made
# (Claude Code will re-run or notify user)
if [ $fixed_count -gt 0 ]; then
    echo "🔧 Fixed $fixed_count basic-memory filename(s) to kebab-case"
    exit 1  # Signal that changes were made
fi

exit 0
