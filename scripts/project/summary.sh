#!/bin/bash
# Show project overview and statistics

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/helpers.sh"

echo "📊 Kinemotion GitHub Project Summary"
echo "===================================="
echo ""

# Get all items
ITEMS=$(gh api graphql -f query='
query {
  node(id: "PVT_kwHOAAFl8c4BJKHO") {
    ... on ProjectV2 {
      title
      items(first: 100) {
        totalCount
        nodes {
          id
          content {
            ... on Issue {
              number
              title
              state
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
            }
          }
        }
      }
    }
  }
}
' 2>/dev/null)

TOTAL=$(echo "$ITEMS" | jq '.data.node.items.totalCount')
echo "📌 Total Issues: $TOTAL"
echo ""

# Status breakdown
echo "Status:"
for status in "Backlog" "In Progress" "In Review" "Done"; do
    count=$(echo "$ITEMS" | jq "[.data.node.items.nodes[] | select(.fieldValues.nodes[] | select(.field.name == \"Status\" and .name == \"$status\"))] | length")
    echo "  • $status: $count"
done
echo ""

# Priority breakdown
echo "Priority:"
for priority in "Critical" "High" "Medium" "Low"; do
    count=$(echo "$ITEMS" | jq "[.data.node.items.nodes[] | select(.fieldValues.nodes[] | select(.field.name == \"Priority\" and .name == \"$priority\"))] | length")
    echo "  • $priority: $count"
done
echo ""

# Domain breakdown
echo "Domain Area:"
for domain in "Testing" "Documentation" "Pose Detection" "Performance" "CI/CD" "Metrics" "Refactoring"; do
    count=$(echo "$ITEMS" | jq "[.data.node.items.nodes[] | select(.fieldValues.nodes[] | select(.field.name == \"Domain Area\" and .name == \"$domain\"))] | length")
    if [ "$count" -gt 0 ]; then
        echo "  • $domain: $count"
    fi
done
echo ""

# Complexity breakdown
echo "Complexity:"
for complexity in "1 - Simple" "2 - Moderate" "3 - Complex" "4 - High" "5 - Very High"; do
    count=$(echo "$ITEMS" | jq "[.data.node.items.nodes[] | select(.fieldValues.nodes[] | select(.field.name == \"Complexity\" and .name == \"$complexity\"))] | length")
    if [ "$count" -gt 0 ]; then
        echo "  • $complexity: $count"
    fi
done
echo ""

# Recent items
echo "Recent Issues:"
echo "$ITEMS" | jq -r '.data.node.items.nodes[] | "#\(.content.number): \(.content.title)"' | head -5 | sed 's/^/  /'
echo ""

# Project URL
echo "📖 Project Board: https://github.com/users/feniix/projects/2"
