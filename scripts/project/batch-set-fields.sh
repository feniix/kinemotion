#!/bin/bash
# Set multiple fields on a project item at once

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/helpers.sh"

if [ $# -lt 2 ]; then
    echo "Usage: $0 <issue-number> [--field value] ..."
    echo ""
    echo "Examples:"
    echo "  $0 5 --priority High --complexity 3 --effort 8"
    echo "  $0 5 --status 'In Progress' --domain Testing --coverage High"
    exit 1
fi

ISSUE_NUM="$1"
shift

# Get issue GitHub ID
ISSUE_ID=$(gh api repos/$REPO/issues/$ISSUE_NUM --jq '.node_id' 2>/dev/null)
if [ -z "$ISSUE_ID" ]; then
    print_error "Issue #$ISSUE_NUM not found"
    exit 1
fi

# Get project item ID
PROJECT_ITEM_ID=$(gh api graphql -f query='
query {
  node(id: "PVT_kwHOAAFl8c4BJKHO") {
    ... on ProjectV2 {
      items(first: 100) {
        nodes {
          id
          content {
            ... on Issue {
              id
            }
          }
        }
      }
    }
  }
}
' --jq ".data.node.items.nodes[] | select(.content.id == \"$ISSUE_ID\") | .id" 2>/dev/null)

if [ -z "$PROJECT_ITEM_ID" ]; then
    print_error "Issue #$ISSUE_NUM is not in the project"
    exit 1
fi

# Parse arguments
declare -A fields

while [ $# -gt 0 ]; do
    if [[ "$1" == --* ]]; then
        key="${1#--}"
        shift
        if [ $# -gt 0 ]; then
            fields["$key"]="$1"
            shift
        fi
    fi
done

# Map short field names to full names
declare -A field_map=(
    ["priority"]="Priority"
    ["complexity"]="Complexity"
    ["effort"]="Effort (Story Points)"
    ["coverage"]="Test Coverage Impact"
    ["domain"]="Domain Area"
    ["status"]="Status"
)

# Apply each field
for key in "${!fields[@]}"; do
    if [ -z "${field_map[$key]}" ]; then
        print_error "Unknown field: $key"
        echo "Valid fields: priority, complexity, effort, coverage, domain, status"
        continue
    fi

    field_name="${field_map[$key]}"
    value="${fields[$key]}"

    # Get field ID
    FIELD_ID=$(get_field_id "$field_name")
    if [ -z "$FIELD_ID" ]; then
        print_error "Field '$field_name' not found"
        continue
    fi

    # Determine if it's a single select or number field
    FIELD_TYPE=$(gh api graphql -f query='
    query {
      node(id: "PVT_kwHOAAFl8c4BJKHO") {
        ... on ProjectV2 {
          fields(first: 20) {
            nodes {
              ... on ProjectV2Field {
                id
                name
                __typename
              }
              ... on ProjectV2SingleSelectField {
                id
                name
                __typename
              }
            }
          }
        }
      }
    }
    ' --jq ".data.node.fields.nodes[] | select(.id == \"$FIELD_ID\") | .__typename" 2>/dev/null)

    if [ "$FIELD_TYPE" = "ProjectV2SingleSelectField" ]; then
        # Get option ID
        OPTION_ID=$(get_option_id "$field_name" "$value")
        if [ -z "$OPTION_ID" ]; then
            print_error "Option '$value' not found in field '$field_name'"
            continue
        fi

        # Set field
        gh api graphql -f query='
        mutation {
          updateProjectV2ItemFieldValue(input: {
            projectId: "PVT_kwHOAAFl8c4BJKHO"
            itemId: "'$PROJECT_ITEM_ID'"
            fieldId: "'$FIELD_ID'"
            value: {singleSelectOptionId: "'$OPTION_ID'"}
          }) {
            clientMutationId
          }
        }
        ' >/dev/null 2>&1

        print_success "Set $field_name to '$value'"

    else
        # Number field
        gh api graphql -f query='
        mutation {
          updateProjectV2ItemFieldValue(input: {
            projectId: "PVT_kwHOAAFl8c4BJKHO"
            itemId: "'$PROJECT_ITEM_ID'"
            fieldId: "'$FIELD_ID'"
            value: {number: '$value'}
          }) {
            clientMutationId
          }
        }
        ' >/dev/null 2>&1

        print_success "Set $field_name to $value"
    fi
done

echo ""
print_success "All fields updated for issue #$ISSUE_NUM"
