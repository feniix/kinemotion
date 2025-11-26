#!/bin/bash
# Set a custom field value on a project item

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/helpers.sh"

if [ $# -lt 3 ]; then
    echo "Usage: $0 <issue-number> <field-name> <value>"
    echo ""
    echo "Examples:"
    echo "  $0 5 Priority High"
    echo "  $0 5 'Test Coverage Impact' Medium"
    echo "  $0 5 'Effort (Story Points)' 5"
    exit 1
fi

ISSUE_NUM="$1"
FIELD_NAME="$2"
VALUE="$3"

# Get field ID
FIELD_ID=$(get_field_id "$FIELD_NAME")
if [ -z "$FIELD_ID" ]; then
    print_error "Field '$FIELD_NAME' not found"
    exit 1
fi

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

# Determine field type and set value accordingly
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
    # Get option ID for single select fields
    OPTION_ID=$(get_option_id "$FIELD_NAME" "$VALUE")
    if [ -z "$OPTION_ID" ]; then
        print_error "Option '$VALUE' not found in field '$FIELD_NAME'"
        exit 1
    fi

    # Set single select field
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

    print_success "Set $FIELD_NAME to '$VALUE' for issue #$ISSUE_NUM"

elif [ "$FIELD_TYPE" = "ProjectV2Field" ]; then
    # Handle number or text fields
    gh api graphql -f query='
    mutation {
      updateProjectV2ItemFieldValue(input: {
        projectId: "PVT_kwHOAAFl8c4BJKHO"
        itemId: "'$PROJECT_ITEM_ID'"
        fieldId: "'$FIELD_ID'"
        value: {number: '$VALUE'}
      }) {
        clientMutationId
      }
    }
    ' >/dev/null 2>&1

    print_success "Set $FIELD_NAME to $VALUE for issue #$ISSUE_NUM"
else
    print_error "Unknown field type: $FIELD_TYPE"
    exit 1
fi
