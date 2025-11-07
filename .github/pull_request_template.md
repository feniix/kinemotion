## Description

<!-- Provide a brief description of the changes in this PR -->

## Type of Change

<!-- Mark the relevant option with an "x" -->

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Code refactoring (no functional changes)
- [ ] Performance improvement
- [ ] Test coverage improvement

## Related Issues

<!-- Link to related issues using #issue_number -->

Closes #
Related to #

## Changes Made

<!-- Describe the changes in detail -->

-
-
-

## Testing

<!-- Describe the testing you've done -->

### Test Environment

- OS: <!-- e.g., macOS 14.0, Ubuntu 22.04 -->
- Python version: <!-- e.g., 3.12.7 -->
- Video specs tested: <!-- e.g., 1920x1080 30fps MP4 -->

### Test Cases

<!-- Describe what you tested -->

- [ ] Tested with sample videos
- [ ] Added/updated unit tests
- [ ] All existing tests pass
- [ ] Tested edge cases

### Commands Run

```bash
# Example test commands
uv run kinemotion dropjump-analyze test_video.mp4
uv run kinemotion cmj-analyze test_video.mp4
```

## Code Quality Checklist

<!-- Confirm all checks pass -->

- [ ] Code follows the project's style guidelines
- [ ] Code is formatted with Black: `uv run black src/`
- [ ] Linting passes: `uv run ruff check`
- [ ] Type checking passes: `uv run mypy src/kinemotion`
- [ ] All tests pass: `uv run pytest`
- [ ] Added type annotations to all new functions
- [ ] Added docstrings to public functions/classes
- [ ] No new linting warnings introduced

## Documentation

<!-- Update documentation as needed -->

- [ ] Updated README.md (if needed)
- [ ] Updated CLAUDE.md (if needed)
- [ ] Updated docs/PARAMETERS.md (if adding/changing parameters)
- [ ] Added/updated code comments
- [ ] Added docstrings

## Screenshots / Videos

<!-- If applicable, add screenshots or demo videos -->

## Breaking Changes

<!-- If this PR introduces breaking changes, describe them and migration steps -->

## Additional Notes

<!-- Any additional information reviewers should know -->

## Reviewer Checklist

<!-- For reviewers -->

- [ ] Code quality meets project standards
- [ ] Tests are comprehensive and pass
- [ ] Documentation is clear and complete
- [ ] No security concerns
- [ ] Performance impact is acceptable
- [ ] Breaking changes are justified and documented
