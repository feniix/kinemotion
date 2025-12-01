---
title: Backend SonarCloud Integration Status
type: note
permalink: development/backend-sonar-cloud-integration-status-1
---

# Backend SonarCloud Integration Status

**Date:** December 1, 2025
**Status:** ❌ Backend NOT currently tracked by SonarCloud

## Current Situation

### SonarCloud Configuration
The project's `sonar-project.properties` at the repository root configures:
- **Sources:** `src/kinemotion` (main Python package only)
- **Tests:** `tests` (main project tests only)
- **Coverage:** `coverage.xml` (main project coverage only)

**Backend directory (`backend/`) is excluded from SonarCloud analysis.**

### Why Backend Isn't Tracked
1. The backend is a separate FastAPI application in its own subdirectory
2. It has its own `pyproject.toml`, dependencies, and test suite
3. The main SonarCloud configuration doesn't include `backend/src` in sources
4. GitHub Actions workflow uploads only main project coverage to SonarCloud

### Verification Method Used
Since backend isn't in SonarCloud, **local analysis with jscpd is authoritative**:
- Tool: jscpd v4.0.5
- Date: December 1, 2025
- Result: 0% source duplication, 2.28% test duplication (well below 3%)

## Options for SonarCloud Integration

### Option 1: Add Backend to Main Project Analysis
Update `/sonar-project.properties`:
```properties
# Multi-module sources
sonar.sources=src/kinemotion,backend/src/kinemotion_backend
sonar.tests=tests,backend/tests

# Multi-module coverage
sonar.python.coverage.reportPaths=coverage.xml,backend/coverage.xml
```

**Pros:**
- Single SonarCloud project
- Unified metrics dashboard
- Simpler CI/CD configuration

**Cons:**
- Backend metrics mixed with main package metrics
- May need to adjust quality gates for different codebases

### Option 2: Create Separate SonarCloud Project for Backend
Create `backend/sonar-project.properties`:
```properties
sonar.projectKey=feniix_kinemotion_backend
sonar.projectName=Kinemotion Backend
sonar.organization=feniix
sonar.sources=src/kinemotion_backend
sonar.tests=tests
sonar.python.coverage.reportPaths=coverage.xml
```

Add separate GitHub Actions job:
```yaml
backend-sonarqube:
  name: Backend SonarQube Scan
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - name: Run backend tests
      working-directory: backend
      run: uv run pytest --cov --cov-report=xml
    - name: SonarQube Scan
      working-directory: backend
      uses: SonarSource/sonarqube-scan-action@v6
```

**Pros:**
- Separate metrics for backend
- Independent quality gates
- Clear separation of concerns

**Cons:**
- More complex CI/CD setup
- Two SonarCloud projects to manage
- Separate quality gate configurations

### Option 3: Keep Local Verification Only
Continue using jscpd for duplication checks:
```bash
# In CI/CD
npx jscpd backend/src/kinemotion_backend --threshold 3 --exitCode 1
```

**Pros:**
- Simple, works today
- No SonarCloud configuration needed
- Fast feedback in CI

**Cons:**
- No historical tracking
- Manual verification required
- No centralized dashboard

## Recommendation

**For now: Option 3 (Local verification with jscpd)**

Reasons:
1. Backend is small (676 LOC) - local tools are sufficient
2. 0% duplication already verified
3. Avoids CI/CD complexity
4. Can integrate with SonarCloud later if backend grows

**If backend grows >2000 LOC: Switch to Option 1**

At that point, unified SonarCloud tracking becomes more valuable for:
- Historical trend analysis
- Quality gate enforcement
- Team visibility
- PR quality checks

## Current Status Summary

| Metric | Local Verification | SonarCloud Status |
|--------|-------------------|-------------------|
| Backend duplication | ✅ 0% (jscpd) | ❌ Not tracked |
| Backend coverage | ✅ 61-85% (pytest) | ❌ Not tracked |
| Backend quality | ✅ Verified locally | ❌ Not tracked |
| Main project | N/A | ✅ Tracked |

## Access SonarCloud Dashboard

To view main project metrics (not backend):
1. Visit: https://sonarcloud.io/project/overview?id=feniix_kinemotion
2. Navigate to: Summary > Measures > Duplications
3. Check: "Overall Code" and "New Code" tabs

**Note:** Backend metrics will not appear unless configuration is updated per Option 1 or 2 above.

## Related Documentation

- Local duplication analysis: `development/backend-code-duplication-analysis.md`
- Local coverage analysis: `development/backend-code-coverage-analysis.md`
- Main project SonarCloud: https://sonarcloud.io/project/overview?id=feniix_kinemotion
