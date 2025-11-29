#!/bin/bash
# Basic Memory Utilities - Enforces kebab-case naming convention
# Source this in your shell profile: source scripts/basic-memory-utils.sh

# Function to convert Title Case to kebab-case
to_kebab_case() {
    echo "$1" | \
        sed 's/[[:space:]]\+/-/g' | \
        tr '[:upper:]' '[:lower:]' | \
        sed 's/[^a-z0-9-]//g'
}

# Wrapper for write_note that enforces kebab-case filenames
write_note_kebab() {
    local title="$1"
    local content="$2"
    local folder="$3"
    local tags="${4:-}"

    if [ -z "$title" ] || [ -z "$content" ] || [ -z "$folder" ]; then
        echo "Usage: write_note_kebab <title> <content> <folder> [tags]"
        echo "Example: write_note_kebab 'My Feature' 'Some content...' 'biomechanics' 'tag1,tag2'"
        return 1
    fi

    # Generate kebab-case filename
    local kebab_name=$(to_kebab_case "$title")
    local full_path=".basic-memory/${folder}/${kebab_name}.md"

    echo "ℹ️  Creating note: $full_path"

    # Create frontmatter with kebab-case permalink
    local frontmatter="---
title: $title
type: note
permalink: ${folder}/${kebab_name}
tags:
$(echo "$tags" | tr ',' '\n' | sed 's/^/  - /; s/  - $//')
---
"

    # Combine frontmatter + content
    local full_content="${frontmatter}${content}"

    # Create directory if it doesn't exist
    mkdir -p ".basic-memory/${folder}"

    # Write the file
    echo "$full_content" > "$full_path"

    echo "✅ Note created: $full_path"
}

# Auto-fix function for existing badly-named files
fix_basic_memory_filenames() {
    local fixed_count=0

    echo "🔍 Scanning .basic-memory/ for improperly named files..."

    # Find all .md files in .basic-memory that have spaces or capitals
    while IFS= read -r file; do
        local dir=$(dirname "$file")
        local basename=$(basename "$file")
        local new_name=$(to_kebab_case "${basename%.md}")
        local new_path="${dir}/${new_name}.md"

        if [ "$file" != "$new_path" ]; then
            echo "  Renaming: $basename → ${new_name}.md"
            mv "$file" "$new_path"
            ((fixed_count++))
        fi
    done < <(find .basic-memory -name "*.md" -type f)

    if [ $fixed_count -gt 0 ]; then
        echo "✅ Fixed $fixed_count filename(s)"
    else
        echo "✅ All filenames are properly formatted (kebab-case)"
    fi
}

echo "✅ Basic Memory utilities loaded"
echo "   Use: write_note_kebab <title> <content> <folder> [tags]"
echo "   Or:  fix_basic_memory_filenames (to auto-fix existing files)"
