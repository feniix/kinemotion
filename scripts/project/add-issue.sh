#!/bin/bash
# Create a new issue and add it to the project with custom fields

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/helpers.sh"

if [ $# -lt 2 ]; then
    echo "Usage: $0 <title> <body> [options]"
    echo ""
    echo "Options:"
    echo "  --priority PRIORITY           Critical, High, Medium, Low"
    echo "  --complexity LEVEL            1-5 scale or: Simple, Moderate, Complex, High, Very High"
    echo "  --effort POINTS               Number of story points"
    echo "  --domain DOMAIN               Testing, Documentation, Pose Detection, Performance, CI/CD, Metrics, Refactoring"
    echo "  --coverage IMPACT             High, Medium, Low"
    echo "  --milestone MILESTONE         Milestone name"
    echo ""
    echo "Example:"
    echo "  $0 'New Feature' 'Description here' --priority High --complexity 3 --effort 5 --domain Testing --coverage High"
    exit 1
fi

TITLE="$1"
BODY="$2"
shift 2

# Parse options
declare -A options

while [ $# -gt 0 ]; do
    if [[ "$1" == --* ]]; then
        key="${1#--}"
        shift
        if [ $# -gt 0 ]; then
            options["$key"]="$1"
            shift
        fi
    fi
done

# Build issue creation command
ISSUE_CMD="gh issue create --repo $REPO --title \"$TITLE\" --body \"$BODY\""

if [ -n "${options[milestone]}" ]; then
    ISSUE_CMD="$ISSUE_CMD --milestone \"${options[milestone]}\""
fi

echo "Creating issue..."
ISSUE_URL=$(eval "$ISSUE_CMD")
ISSUE_NUM=$(echo "$ISSUE_URL" | grep -o '[0-9]*$')

if [ -z "$ISSUE_NUM" ]; then
    print_error "Failed to create issue"
    exit 1
fi

print_success "Created issue #$ISSUE_NUM"

# Get issue GitHub ID for project item lookup
sleep 1  # Wait for issue to be fully created
ISSUE_ID=$(gh api repos/$REPO/issues/$ISSUE_NUM --jq '.node_id' 2>/dev/null)

if [ -z "$ISSUE_ID" ]; then
    print_error "Could not fetch issue ID, skipping project fields"
    exit 0
fi

# Add to project
echo "Adding to project..."
gh api graphql -f query='
mutation {
  addProjectV2ItemById(input: {
    projectId: "PVT_kwHOAAFl8c4BJKHO"
    contentId: "'$ISSUE_ID'"
  }) {
    item {
      id
    }
  }
}
' >/dev/null 2>&1

print_success "Added to project"

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
    print_error "Could not get project item ID"
    exit 1
fi

# Set custom fields
echo "Setting custom fields..."

set_field_value() {
    local field_name="$1"
    local value="$2"

    if [ -z "$value" ]; then
        return
    fi

    FIELD_ID=$(get_field_id "$field_name")
    if [ -z "$FIELD_ID" ]; then
        print_error "Field '$field_name' not found"
        return
    fi

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
        OPTION_ID=$(get_option_id "$field_name" "$value")
        if [ -z "$OPTION_ID" ]; then
            print_error "Option '$value' not found in $field_name"
            return
        fi

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
}

[ -n "${options[priority]}" ] && set_field_value "Priority" "${options[priority]}"
[ -n "${options[complexity]}" ] && set_field_value "Complexity" "${options[complexity]}"
[ -n "${options[effort]}" ] && set_field_value "Effort (Story Points)" "${options[effort]}"
[ -n "${options[domain]}" ] && set_field_value "Domain Area" "${options[domain]}"
[ -n "${options[coverage]}" ] && set_field_value "Test Coverage Impact" "${options[coverage]}"

echo ""
print_success "Issue #$ISSUE_NUM fully configured and added to project"
echo "📖 View: $ISSUE_URL"
