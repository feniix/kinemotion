#!/bin/bash
# List project items with optional filtering

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/helpers.sh"

# Parse arguments
declare -A filters

while [ $# -gt 0 ]; do
    if [[ "$1" == --* ]]; then
        key="${1#--}"
        shift
        if [ $# -gt 0 ]; then
            filters["$key"]="$1"
            shift
        fi
    fi
done

# Query all items
ITEMS=$(gh api graphql -f query='
query {
  node(id: "PVT_kwHOAAFl8c4BJKHO") {
    ... on ProjectV2 {
      items(first: 100) {
        nodes {
          id
          content {
            ... on Issue {
              number
              title
              url
            }
          }
          fieldValues(first: 20) {
            nodes {
              ... on ProjectV2ItemFieldSingleSelectValue {
                field {
                  ... on ProjectV2SingleSelectField {
                    name
                  }
                }
                name
              }
              ... on ProjectV2ItemFieldTextValue {
                field {
                  ... on ProjectV2Field {
                    name
                  }
                }
                text
              }
            }
          }
        }
      }
    }
  }
}
' 2>/dev/null)

# Process items with jq
QUERY='.data.node.items.nodes[]'

# Build filter query
if [ ${#filters[@]} -gt 0 ]; then
    for key in "${!filters[@]}"; do
        value="${filters[$key]}"
        case "$key" in
            "status")
                QUERY="$QUERY | select(.fieldValues.nodes[] | select(.field.name == \"Status\" and .name == \"$value\"))"
                ;;
            "priority")
                QUERY="$QUERY | select(.fieldValues.nodes[] | select(.field.name == \"Priority\" and .name == \"$value\"))"
                ;;
            "domain")
                QUERY="$QUERY | select(.fieldValues.nodes[] | select(.field.name == \"Domain Area\" and .name == \"$value\"))"
                ;;
            "complexity")
                QUERY="$QUERY | select(.fieldValues.nodes[] | select(.field.name == \"Complexity\" and .name == \"$value\"))"
                ;;
            "coverage")
                QUERY="$QUERY | select(.fieldValues.nodes[] | select(.field.name == \"Test Coverage Impact\" and .name == \"$value\"))"
                ;;
        esac
    done
fi

# Format output
FORMAT='
  [
    .content.number,
    .content.title,
    (
      .fieldValues.nodes[] |
      select(.field.name == "Priority") |
      .name
    ) // "—",
    (
      .fieldValues.nodes[] |
      select(.field.name == "Complexity") |
      .name
    ) // "—",
    (
      .fieldValues.nodes[] |
      select(.field.name == "Domain Area") |
      .name
    ) // "—",
    (
      .fieldValues.nodes[] |
      select(.field.name == "Status") |
      .name
    ) // "Backlog"
  ] | @tsv
'

echo "Issue | Title | Priority | Complexity | Domain | Status"
echo "------|-------|----------|------------|--------|--------"

echo "$ITEMS" | jq -r "$QUERY | $FORMAT" | column -t -s $'\t'
