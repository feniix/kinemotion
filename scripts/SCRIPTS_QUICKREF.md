# Project Management Scripts Quick Reference

**Location:** `scripts/project.sh` (main wrapper) + `scripts/project/` (individual scripts)

## Quick Start

```bash
# Show help
./scripts/project.sh

# View project summary
./scripts/project.sh summary

# List all issues
./scripts/project.sh list

# Set a field
./scripts/project.sh set-field 5 Priority High

# Set multiple fields at once
./scripts/project.sh batch-set 5 --priority High --complexity 3 --effort 5

# Update status
./scripts/project.sh set-status 5 "In Progress"

# Create new issue with all fields
./scripts/project.sh add "Issue Title" "Description" \
  --priority High \
  --complexity 3 \
  --effort 5 \
  --domain Testing \
  --coverage High \
  --milestone "Q1 2025: Core Stability"
```

## Available Commands

### summary

Show project overview with counts by status, priority, domain, and complexity.

```bash
./scripts/project.sh summary
```

### list

List all project items with optional filtering.

```bash
./scripts/project.sh list                           # All items
./scripts/project.sh list --status "In Progress"   # By status
./scripts/project.sh list --priority High          # By priority
./scripts/project.sh list --domain Testing         # By domain
```

### set-field

Set a single custom field on an issue.

```bash
./scripts/project.sh set-field <issue-num> <field> <value>

# Examples
./scripts/project.sh set-field 5 Priority High
./scripts/project.sh set-field 5 Complexity "3 - Complex"
./scripts/project.sh set-field 5 "Effort (Story Points)" 5
./scripts/project.sh set-field 5 "Domain Area" Testing
./scripts/project.sh set-field 5 "Test Coverage Impact" High
```

### set-status

Update the status of an issue (Backlog, In Progress, In Review, Done).

```bash
./scripts/project.sh set-status <issue-num> <status>

# Examples
./scripts/project.sh set-status 5 "In Progress"
./scripts/project.sh set-status 5 Done
```

### batch-set

Set multiple fields on an issue at once (faster than multiple set-field calls).

```bash
./scripts/project.sh batch-set <issue-num> --field value [--field value ...]

# Examples
./scripts/project.sh batch-set 5 --priority High --complexity 3 --effort 8
./scripts/project.sh batch-set 5 --status "In Progress" --domain "Pose Detection"
```

### add

Create a new issue and add it to the project with custom fields.

```bash
./scripts/project.sh add <title> <body> [--field value ...]

# Examples
./scripts/project.sh add \
  "Improve pose detection occlusion handling" \
  "Enhance MediaPipe robustness for arm occlusion and lighting changes" \
  --priority High \
  --complexity 3 \
  --effort 5 \
  --domain "Pose Detection" \
  --coverage Medium \
  --milestone "Q2 2025: Performance & Optimization"
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

## Common Workflows

### Start working on an issue

```bash
./scripts/project.sh set-status 5 "In Progress"
./scripts/project.sh set-field 5 "Effort (Story Points)" 8
```

### Mark issue as done

```bash
./scripts/project.sh set-status 5 Done
```

### Batch configure new issues

```bash
# Create multiple issues with full configuration
./scripts/project.sh add "Drop Jump Edge Cases" "Test low boxes, high velocity, etc" \
  --priority High --complexity 3 --effort 5 --domain Testing --coverage High

./scripts/project.sh add "CMJ Biomechanics Guide" "Create comprehensive guide" \
  --priority High --complexity 2 --effort 3 --domain Documentation --coverage Low
```

### Filter and review work

```bash
# View all high-priority items in progress
./scripts/project.sh list --priority High --status "In Progress"

# View all testing work
./scripts/project.sh list --domain Testing

# Project status overview
./scripts/project.sh summary
```

## Notes

- All scripts use the `gh` CLI with GraphQL API
- Project ID: `PVT_kwHOAAFl8c4BJKHO`
- Repository: `feniix/kinemotion`
- Requires `gh` authentication with `project` scope
- Scripts handle errors gracefully and provide clear feedback
- Helper functions in `scripts/project/helpers.sh` can be sourced for custom scripts

## Troubleshooting

**"Field not found"**: Check capitalization of field names (e.g., "Domain Area" not "domain area")

**"Option not found"**: Verify the option exists (e.g., "High" not "high", "3 - Complex" not "3")

**Authentication errors**: Run `gh auth status` to verify scopes, use `gh auth refresh -s project` if needed

**API errors**: The scripts use GraphQL which can have rate limits; wait a moment and retry
