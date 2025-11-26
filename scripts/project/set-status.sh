#!/bin/bash
# Set the status of a project item

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/helpers.sh"

if [ $# -lt 2 ]; then
    echo "Usage: $0 <issue-number> <status>"
    echo ""
    echo "Valid statuses:"
    echo "  Backlog"
    echo "  In Progress"
    echo "  In Review"
    echo "  Done"
    exit 1
fi

ISSUE_NUM="$1"
STATUS="$2"

# Validate status
case "$STATUS" in
    "Backlog"|"Todo"|"In Progress"|"In Review"|"Done")
        # Valid status
        ;;
    *)
        print_error "Invalid status: $STATUS"
        exit 1
        ;;
esac

# Normalize "Todo" to "Backlog"
if [ "$STATUS" = "Todo" ]; then
    STATUS="Backlog"
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

# GitHub uses "Status" as the field name (built-in)
STATUS_FIELD_ID=$(gh api graphql -f query='
query {
  node(id: "PVT_kwHOAAFl8c4BJKHO") {
    ... on ProjectV2 {
      fields(first: 20) {
        nodes {
          ... on ProjectV2SingleSelectField {
            id
            name
          }
        }
      }
    }
  }
}
' --jq ".data.node.fields.nodes[] | select(.name == \"Status\") | .id" 2>/dev/null)

if [ -z "$STATUS_FIELD_ID" ]; then
    # GitHub projects have Status built-in, try different approach
    print_error "Status field not found in project"
    exit 1
fi

# Get status option ID
STATUS_OPTION_ID=$(gh api graphql -f query='
query {
  node(id: "PVT_kwHOAAFl8c4BJKHO") {
    ... on ProjectV2 {
      fields(first: 20) {
        nodes {
          ... on ProjectV2SingleSelectField {
            name
            options {
              id
              name
            }
          }
        }
      }
    }
  }
}
' --jq ".data.node.fields.nodes[] | select(.name == \"Status\") | .options[] | select(.name == \"$STATUS\") | .id" 2>/dev/null)

if [ -z "$STATUS_OPTION_ID" ]; then
    print_error "Status option '$STATUS' not found"
    exit 1
fi

# Update status
gh api graphql -f query='
mutation {
  updateProjectV2ItemFieldValue(input: {
    projectId: "PVT_kwHOAAFl8c4BJKHO"
    itemId: "'$PROJECT_ITEM_ID'"
    fieldId: "'$STATUS_FIELD_ID'"
    value: {singleSelectOptionId: "'$STATUS_OPTION_ID'"}
  }) {
    clientMutationId
  }
}
' >/dev/null 2>&1

print_success "Set status to '$STATUS' for issue #$ISSUE_NUM"
