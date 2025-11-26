# Kinemotion GitHub Project Management Scripts

Shell scripts for managing the Kinemotion GitHub Project using `gh` CLI.

## Scripts

### add-issue.sh

Create a new issue and add it to the project with custom fields.

```bash
./add-issue.sh "Issue Title" "Issue body" --priority High --complexity 3 --effort 5 --domain Testing --coverage High --milestone "Q1 2025: Core Stability"
```

### set-field.sh

Set a custom field value on a project item.

```bash
./set-field.sh <issue-number> <field-name> <value>
./set-field.sh 5 Priority High
./set-field.sh 5 "Test Coverage Impact" Medium
```

### set-status.sh

Update the status of a project item.

```bash
./set-status.sh <issue-number> <status>
./set-status.sh 5 "In Progress"
```

### list.sh

List project items with optional filtering.

```bash
# List all items
./list.sh

# Filter by status
./list.sh --status "In Progress"

# Filter by priority
./list.sh --priority High

# Filter by domain
./list.sh --domain Testing

# Multiple filters
./list.sh --status Todo --domain Documentation
```

### summary.sh

Show project overview and statistics.

```bash
./summary.sh
```

### batch-set-fields.sh

Set multiple fields on an issue at once.

```bash
./batch-set-fields.sh 5 --priority High --complexity 3 --effort 5 --domain Testing --coverage High --status Backlog
```

## Field Values

### Priority

- Critical
- High
- Medium
- Low

### Complexity

- 1 - Simple
- 2 - Moderate
- 3 - Complex
- 4 - High
- 5 - Very High

### Domain Area

- Testing
- Documentation
- Pose Detection
- Performance
- CI/CD
- Metrics
- Refactoring

### Test Coverage Impact

- High
- Medium
- Low

### Status

- Backlog (or Todo)
- In Progress
- In Review
- Done

## Examples

### Create a new issue with all fields

```bash
./add-issue.sh \
  "Improve pose detection occlusion handling" \
  "Enhance MediaPipe robustness for arm occlusion and lighting changes" \
  --priority High \
  --complexity 3 \
  --effort 5 \
  --domain "Pose Detection" \
  --coverage Medium \
  --milestone "Q2 2025: Performance & Optimization"
```

### Move an issue to in progress and set complexity

```bash
./batch-set-fields.sh 10 \
  --status "In Progress" \
  --complexity 3 \
  --effort 8
```

### List all high-priority testing issues

```bash
./list.sh --priority High --domain Testing
```

## Notes

- Project ID is hardcoded as: `PVT_kwHOAAFl8c4BJKHO`
- Repository is: `feniix/kinemotion`
- These scripts use the GitHub GraphQL API via `gh api graphql`
- Requires `gh` CLI with proper authentication (including `project` scope)
