#!/bin/bash
# Common helper functions for project management scripts

PROJECT_ID="PVT_kwHOAAFl8c4BJKHO"
REPO="feniix/kinemotion"

# Map field names to their GraphQL identifiers
declare -A FIELD_IDS

# Function to get all project field IDs (cached)
get_field_ids() {
    if [ ${#FIELD_IDS[@]} -eq 0 ]; then
        # Query for all fields in the project
        gh api graphql -f query='
        query {
          node(id: "PVT_kwHOAAFl8c4BJKHO") {
            ... on ProjectV2 {
              fields(first: 20) {
                nodes {
                  ... on ProjectV2Field {
                    id
                    name
                  }
                  ... on ProjectV2SingleSelectField {
                    id
                    name
                  }
                  ... on ProjectV2IterationField {
                    id
                    name
                  }
                }
              }
            }
          }
        }
        ' | jq -r '.data.node.fields.nodes[] | "\(.name)|\(.id)"' | while IFS='|' read name id; do
            FIELD_IDS["$name"]="$id"
        done
    fi
}

# Function to get field ID by name
get_field_id() {
    local field_name="$1"

    gh api graphql -f query='
    query {
      node(id: "PVT_kwHOAAFl8c4BJKHO") {
        ... on ProjectV2 {
          fields(first: 20) {
            nodes {
              ... on ProjectV2Field {
                id
                name
              }
              ... on ProjectV2SingleSelectField {
                id
                name
              }
            }
          }
        }
      }
    }
    ' --jq ".data.node.fields.nodes[] | select(.name == \"$field_name\") | .id" 2>/dev/null
}

# Function to get single select option ID
get_option_id() {
    local field_name="$1"
    local option_name="$2"

    gh api graphql -f query='
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
    ' --jq ".data.node.fields.nodes[] | select(.name == \"$field_name\") | .options[] | select(.name == \"$option_name\") | .id" 2>/dev/null
}

# Function to get project item ID by issue number
get_project_item_id() {
    local issue_num="$1"

    gh api graphql -f query='
    query {
      repository(owner: "feniix", name: "kinemotion") {
        issue(number: '$issue_num') {
          id
        }
      }
    }
    ' --jq '.data.repository.issue.id' 2>/dev/null
}

# Function to get item details from project
get_project_item() {
    local issue_num="$1"

    gh api graphql -f query='
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
                  body
                }
              }
              fieldValues(first: 20) {
                nodes {
                  ... on ProjectV2ItemFieldValueCommon {
                    field {
                      ... on ProjectV2Field {
                        name
                      }
                    }
                  }
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
    ' --jq ".data.node.items.nodes[] | select(.content.number == $issue_num)" 2>/dev/null
}

# Function to list all project items
list_project_items() {
    gh api graphql -f query='
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
    ' 2>/dev/null
}

# Function to format issue URL
format_issue_url() {
    local issue_num="$1"
    echo "https://github.com/$REPO/issues/$issue_num"
}

# Function to print success message
print_success() {
    echo "✅ $1"
}

# Function to print error message
print_error() {
    echo "❌ $1" >&2
}

# Function to check if field exists
field_exists() {
    local field_name="$1"
    local field_id=$(get_field_id "$field_name")
    [ -n "$field_id" ]
}

# Function to check if option exists in a field
option_exists() {
    local field_name="$1"
    local option_name="$2"
    local option_id=$(get_option_id "$field_name" "$option_name")
    [ -n "$option_id" ]
}

export -f get_field_id
export -f get_option_id
export -f get_project_item_id
export -f get_project_item
export -f list_project_items
export -f format_issue_url
export -f print_success
export -f print_error
export -f field_exists
export -f option_exists
