---
title: Backend Repository Split Migration Guide
type: note
permalink: deployment/backend-repository-split-migration-guide
tags:
- backend
- repository-split
- git
- migration
- cloud-run
- github-actions
- monorepo
- polyrepo
---

# Backend Repository Split Migration Guide

**Created**: 2025-12-02
**Purpose**: Detailed guide for extracting backend/ directory into its own Git repository
**Status**: Planning document

## Overview

This guide outlines the steps to split the `backend/` directory from the kinemotion monorepo into a separate repository while preserving Git history and maintaining deployment to Google Cloud Run.

**Current State:**
- Backend lives in `backend/` within the main kinemotion repository
- Backend v0.1.0 (FastAPI + Python 3.12 + Supabase)
- Deployed to Google Cloud Run via GitHub Actions
- **Key Insight**: Backend already uses `kinemotion` from PyPI (≥0.30.0), NOT local `src/kinemotion/`
- Minimal coupling to monorepo (already designed for independence!)

**Target State:**
- Backend in separate `kinemotion-backend` repository
- Preserves Git history for backend/ files
- Independent CI/CD with GitHub Actions → Cloud Run
- Continues to use kinemotion from PyPI (no code changes needed!)

## Key Advantage: Already Decoupled! ✅

Unlike the frontend, the backend is **already designed for extraction**:

```python
# backend/pyproject.toml line 35
dependencies = [
    "kinemotion>=0.30.0",  # Uses PyPI package, not local ../src/kinemotion/
    # ...
]

# backend/src/kinemotion_backend/app.py line 7
from kinemotion.api import process_cmj_video, process_dropjump_video
```

**This means:**
- No code changes needed in backend/
- Backend will continue using kinemotion from PyPI
- Clean dependency boundary already exists
- Docker build already self-contained

## Prerequisites

✅ **Before starting:**
- [ ] Backup current repository: `git clone --mirror <repo-url> kinemotion-backup.git`
- [ ] Ensure kinemotion v0.34.0 is published to PyPI (current requirement: ≥0.30.0)
- [ ] Create new GitHub repository: `kinemotion-backend` (empty, no README)
- [ ] Verify Cloud Run service is accessible
- [ ] Check Google Cloud Run permissions and service accounts
- [ ] Verify Workload Identity Federation is configured
- [ ] Communicate with team about repository split

## Phase 1: Extract Backend with Git History

### Option A: Using git subtree split (Recommended)

This preserves the full Git history for backend files.

```bash
# 1. Clone the main repository (fresh clone recommended)
cd /tmp
git clone https://github.com/feniix/kinemotion.git kinemotion-backend-extract
cd kinemotion-backend-extract

# 2. Extract backend/ directory with history
git subtree split --prefix=backend -b backend-only

# 3. Create a new temporary directory for the new repository
cd ..
mkdir kinemotion-backend
cd kinemotion-backend
git init

# 4. Pull the backend-only branch
git pull ../kinemotion-backend-extract backend-only

# 5. Review the extracted history
git log --oneline
# Should show only commits that touched backend/

# 6. Add new remote and push
git remote add origin git@github.com:feniix/kinemotion-backend.git
git branch -M main
git push -u origin main

# 7. Clean up
cd ..
rm -rf kinemotion-backend-extract
```

### Option B: Using git filter-repo (Alternative)

```bash
# 1. Install git-filter-repo
pip install git-filter-repo

# 2. Clone and filter
git clone https://github.com/feniix/kinemotion.git kinemotion-backend
cd kinemotion-backend

# 3. Filter to keep only backend/
git filter-repo --path backend/ --path-rename backend/:

# 4. Push to new repository
git remote add origin git@github.com:feniix/kinemotion-backend.git
git push -u origin main
```

## Phase 2: Set Up New Backend Repository

### 2.1 Add Repository Files

```bash
cd kinemotion-backend

# Create .gitignore (backend-specific)
cat > .gitignore <<'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
dist/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
ENV/
env/
.venv

# uv
.uv/

# Testing
.pytest_cache/
.coverage
.coverage.*
htmlcov/
coverage.xml

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# Logs
*.log
combined.log
error.log

# Environment variables
.env
.env.local
.env.*.local

# OS
.DS_Store
Thumbs.db

# Docker
.dockerignore
EOF

# Create README.md (update from existing)
cat > README.md <<'EOF'
# Kinemotion Backend API

FastAPI backend for Kinemotion video-based kinematic analysis.

## Tech Stack

- **Framework**: FastAPI 0.109.0+
- **Runtime**: Python 3.12
- **Package Manager**: uv
- **Database**: Supabase (PostgreSQL)
- **Storage**: Cloudflare R2 (optional)
- **Deployment**: Google Cloud Run
- **Analysis Engine**: kinemotion CLI (from PyPI)

## Architecture

\`\`\`
Frontend (React) → Backend API (FastAPI) → kinemotion CLI (PyPI) → Results
                  ↓
              Supabase (auth, storage)
\`\`\`

The backend uses the \`kinemotion\` package from PyPI for video analysis:
- Drop Jump: Ground contact time, flight time, RSI
- CMJ: Jump height, countermovement depth, triple extension

## Quick Start

### Installation

\`\`\`bash
# Install dependencies
uv sync

# Or with pip
pip install -e .
\`\`\`

### Running Locally

\`\`\`bash
# Development (with auto-reload)
uv run uvicorn kinemotion_backend.app:app --reload

# Production mode
uv run uvicorn kinemotion_backend.app:app --host 0.0.0.0 --port 8000
\`\`\`

Access API at \`http://localhost:8000\`

### API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Environment Variables

Create a \`.env\` file:

\`\`\`bash
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key

# CORS (comma-separated)
CORS_ORIGINS=https://kinemotion.vercel.app,http://localhost:3000

# Optional: Cloudflare R2 Storage
R2_ACCOUNT_ID=your-account-id
R2_ACCESS_KEY_ID=your-access-key
R2_SECRET_ACCESS_KEY=your-secret-key
R2_BUCKET_NAME=kinemotion

# Logging
LOG_LEVEL=INFO
JSON_LOGS=true
\`\`\`

## Deployment

### Google Cloud Run

The backend is deployed to Google Cloud Run via GitHub Actions.

**Prerequisites:**
- GCP Project: \`kinemotion-backend\`
- Region: \`us-central1\`
- Workload Identity Federation configured
- Service account: \`github-actions-deploy@kinemotion-backend.iam.gserviceaccount.com\`
- Runtime service account: \`kinemotion-backend-runtime@kinemotion-backend.iam.gserviceaccount.com\`

**Deployment Flow:**
1. Push to \`main\` branch triggers GitHub Actions
2. Tests run (pytest, pyright, ruff)
3. Docker image built and pushed to GCR
4. Deployed to Cloud Run with secrets from Secret Manager

**Manual Deployment:**
\`\`\`bash
# Build Docker image
docker build -t gcr.io/kinemotion-backend/kinemotion-backend:latest .

# Push to GCR
docker push gcr.io/kinemotion-backend/kinemotion-backend:latest

# Deploy to Cloud Run
gcloud run deploy kinemotion-backend \\
  --image gcr.io/kinemotion-backend/kinemotion-backend:latest \\
  --region us-central1 \\
  --platform managed \\
  --allow-unauthenticated \\
  --memory 2Gi \\
  --set-env-vars CORS_ORIGINS=https://kinemotion.vercel.app
\`\`\`

## Testing

\`\`\`bash
# Run all tests
uv run pytest

# With coverage
uv run pytest --cov=src/kinemotion_backend

# Type checking
uv run pyright

# Linting
uv run ruff check .

# Format code
uv run ruff format .
\`\`\`

## API Endpoints

### Health Check
\`GET /health\`

### Video Analysis
\`POST /api/analyze\`

**Request:**
- Form data with \`video\` file
- Optional query params: \`jump_type\`, \`quality\`

**Response:**
\`\`\`json
{
  "status": "success",
  "metrics": {
    "jump_height_m": 0.506,
    "flight_time_s": 0.640,
    ...
  }
}
\`\`\`

## Development

### Project Structure

\`\`\`
.
├── src/kinemotion_backend/
│   ├── __init__.py
│   ├── app.py              # FastAPI application
│   ├── auth.py             # Supabase authentication
│   ├── middleware.py       # Request logging, auth
│   └── logging_config.py   # Structured logging
├── tests/
│   └── test_app.py
├── Dockerfile              # Cloud Run optimized
├── pyproject.toml          # Dependencies & config
└── README.md
\`\`\`

### Adding New Endpoints

1. Add endpoint to \`src/kinemotion_backend/app.py\`
2. Add tests to \`tests/\`
3. Update API documentation in README

### Dependencies

The backend depends on:
- **kinemotion** (from PyPI): Core analysis engine
- **FastAPI**: Web framework
- **Supabase**: Authentication and storage
- **structlog**: Structured logging
- **boto3**: Cloudflare R2 storage (optional)

**Important**: The backend uses the published \`kinemotion\` package from PyPI (≥0.30.0), not a local copy. To update:

\`\`\`bash
# Update pyproject.toml
[project]
dependencies = [
    "kinemotion>=0.35.0",  # Update version
    ...
]

# Sync dependencies
uv sync

# Test with new version
uv run pytest
\`\`\`

## Security

- **Authentication**: Supabase JWT tokens
- **CORS**: Configured for production frontend
- **Secrets**: Managed in Google Secret Manager
- **Service Accounts**: Least-privilege separation (CI/CD vs runtime)
- **Rate Limiting**: slowapi middleware (default: 100 requests/minute)

## Related Repositories

- **CLI**: [kinemotion](https://github.com/feniix/kinemotion) - Analysis engine (published to PyPI)
- **Frontend**: [kinemotion-frontend](https://github.com/feniix/kinemotion-frontend) - React UI

## Contributing

See [CONTRIBUTING.md](https://github.com/feniix/kinemotion/blob/main/CONTRIBUTING.md) in main repository.

## License

MIT - See [LICENSE](https://github.com/feniix/kinemotion/blob/main/LICENSE)
EOF

# Commit initial setup
git add .gitignore README.md
git commit -m "docs: update repository setup for standalone backend"
git push
```

### 2.2 Update pyproject.toml

Update repository URL in `pyproject.toml`:

```toml
[project]
name = "kinemotion-backend"
version = "0.1.0"
# ...

[project.urls]
Homepage = "https://github.com/feniix/kinemotion-backend"
Repository = "https://github.com/feniix/kinemotion-backend"
Issues = "https://github.com/feniix/kinemotion-backend/issues"
```

### 2.3 Move GitHub Actions Workflow

Copy `.github/workflows/deploy-backend.yml` from main repo to new repo:

```bash
cd kinemotion-backend
mkdir -p .github/workflows

# Copy workflow file from main repo
# (Manual: copy content from main repo's .github/workflows/deploy-backend.yml)

cat > .github/workflows/deploy.yml <<'EOF'
name: Deploy to Google Cloud Run

on:
  push:
    branches: [main]
  workflow_dispatch:
    inputs:
      reason:
        description: 'Reason for manual deployment'
        required: false
        type: string

env:
  GCP_PROJECT_ID: kinemotion-backend
  GCP_REGION: us-central1
  REGISTRY: gcr.io
  SERVICE_NAME: kinemotion-backend

jobs:
  test:
    name: Run Tests
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.12']
    steps:
      - name: Display deployment reason (if manual trigger)
        if: github.event_name == 'workflow_dispatch'
        run: |
          REASON="${{ github.event.inputs.reason }}"
          if [ -z "$REASON" ]; then
            echo "Manual deployment triggered"
          else
            echo "Manual deployment triggered: $REASON"
          fi

      - uses: actions/checkout@v6

      - name: Set up Python
        uses: actions/setup-python@v6
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install uv
        run: pip install uv

      - name: Install dependencies
        run: uv sync

      - name: Run tests
        run: uv run pytest --tb=short

      - name: Run type checking
        run: uv run pyright

      - name: Run linting
        run: uv run ruff check .

  build:
    name: Build and Push Docker Image to GCR
    needs: test
    runs-on: ubuntu-latest
    permissions:
      contents: read
      id-token: write
    steps:
      - uses: actions/checkout@v6

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Authenticate to Google Cloud
        uses: google-github-actions/auth@v3
        with:
          workload_identity_provider: 'projects/1008251132682/locations/global/workloadIdentityPools/github-pool/providers/github-provider'
          service_account: 'github-actions-deploy@kinemotion-backend.iam.gserviceaccount.com'

      - name: Set up Cloud SDK
        uses: google-github-actions/setup-gcloud@v3

      - name: Configure Docker authentication to GCR
        run: gcloud auth configure-docker ${{ env.REGISTRY }}

      - name: Build and push Docker image to GCR
        uses: docker/build-push-action@v6
        with:
          context: .
          file: ./Dockerfile
          push: true
          tags: ${{ env.REGISTRY }}/${{ env.GCP_PROJECT_ID }}/${{ env.SERVICE_NAME }}:${{ github.sha }},${{ env.REGISTRY }}/${{ env.GCP_PROJECT_ID }}/${{ env.SERVICE_NAME }}:latest
          cache-from: type=registry,ref=${{ env.REGISTRY }}/${{ env.GCP_PROJECT_ID }}/${{ env.SERVICE_NAME }}:buildcache
          cache-to: type=registry,ref=${{ env.REGISTRY }}/${{ env.GCP_PROJECT_ID }}/${{ env.SERVICE_NAME }}:buildcache,mode=max

  deploy:
    name: Deploy to Google Cloud Run
    needs: build
    runs-on: ubuntu-latest
    permissions:
      contents: read
      id-token: write
    environment:
      name: production
      url: https://kinemotion-backend-1008251132682.us-central1.run.app
    steps:
      - uses: actions/checkout@v6

      - name: Authenticate to Google Cloud
        id: auth
        uses: google-github-actions/auth@v3
        with:
          workload_identity_provider: 'projects/1008251132682/locations/global/workloadIdentityPools/github-pool/providers/github-provider'
          service_account: 'github-actions-deploy@kinemotion-backend.iam.gserviceaccount.com'

      - name: Deploy to Cloud Run
        uses: google-github-actions/deploy-cloudrun@v3
        with:
          service: ${{ env.SERVICE_NAME }}
          region: ${{ env.GCP_REGION }}
          image: ${{ env.REGISTRY }}/${{ env.GCP_PROJECT_ID }}/${{ env.SERVICE_NAME }}:${{ github.sha }}
          flags: |
            --memory=2Gi
            --allow-unauthenticated
            --service-account=kinemotion-backend-runtime@${{ env.GCP_PROJECT_ID }}.iam.gserviceaccount.com
            --set-env-vars=CORS_ORIGINS=https://kinemotion.vercel.app,JSON_LOGS=true,LOG_LEVEL=INFO
            --set-secrets=SUPABASE_URL=SUPABASE_URL:latest,SUPABASE_ANON_KEY=SUPABASE_ANON_KEY:latest

      - name: Verify deployment health
        run: |
          sleep 10
          curl -sf https://${{ env.SERVICE_NAME }}-1008251132682.${{ env.GCP_REGION }}.run.app/health || exit 1

      - name: Deployment notification
        if: success()
        run: |
          echo "✅ Successfully deployed ${{ env.SERVICE_NAME }} to Cloud Run"
          echo "API URL: https://${{ env.SERVICE_NAME }}-1008251132682.${{ env.GCP_REGION }}.run.app"
          echo "Health: https://${{ env.SERVICE_NAME }}-1008251132682.${{ env.GCP_REGION }}.run.app/health"

      - name: Deployment failure notification
        if: failure()
        run: |
          echo "❌ Deployment to Cloud Run failed"
          exit 1
EOF

# Commit workflow
git add .github/workflows/deploy.yml
git commit -m "ci: add Cloud Run deployment workflow"
git push
```

### 2.4 Configure GitHub Repository Settings

1. **Workload Identity Federation** (Settings → Secrets and variables → Actions):
   - No secrets needed (uses Workload Identity Federation with OIDC)
   - Verify that GitHub Actions has permission to authenticate with GCP

2. **Branch Protection** (Settings → Branches):
   - Protect `main` branch
   - Require pull request reviews
   - Require status checks to pass (tests, type check, linting)

3. **Environments** (Settings → Environments):
   - Create `production` environment
   - Add protection rules if needed

## Phase 3: Update Workload Identity Federation

The Workload Identity Federation needs to recognize the new repository.

### 3.1 Update Workload Identity Pool Attribute Mapping

```bash
# Get current attribute mapping
gcloud iam workload-identity-pools providers describe github-provider \
  --location=global \
  --workload-identity-pool=github-pool \
  --project=kinemotion-backend

# Update to allow new repository
gcloud iam workload-identity-pools providers update-oidc github-provider \
  --location=global \
  --workload-identity-pool=github-pool \
  --attribute-condition="assertion.repository_owner=='feniix' && (assertion.repository=='kinemotion' || assertion.repository=='kinemotion-backend')" \
  --project=kinemotion-backend
```

**Note**: This allows both repositories to deploy. Remove `kinemotion` from the condition after migration is complete.

### 3.2 Verify Service Account Bindings

```bash
# Verify github-actions-deploy can authenticate
gcloud iam service-accounts get-iam-policy \
  github-actions-deploy@kinemotion-backend.iam.gserviceaccount.com \
  --project=kinemotion-backend

# Should show principalSet for Workload Identity
```

## Phase 4: Clean Up Main Repository

### 4.1 Remove backend/ Directory

```bash
cd /path/to/kinemotion  # Main repository

# Create a new branch for the cleanup
git checkout -b chore/remove-backend-directory

# Remove backend directory
git rm -r backend/

# Commit
git commit -m "chore: move backend to separate repository

Backend has been extracted to:
https://github.com/feniix/kinemotion-backend

This commit removes the backend/ directory from the main repository
as it now lives independently. The backend continues to use the
kinemotion package from PyPI (>=0.30.0) for video analysis."

# Push and create PR
git push -u origin chore/remove-backend-directory
```

### 4.2 Update Documentation

**CLAUDE.md** - Update architecture section:

```markdown
## Architecture

### Full-Stack Architecture

The project consists of three separate repositories:

**Repositories:**
- **kinemotion** (this repo): CLI analysis engine (v0.34.0) - Published to PyPI
- **kinemotion-frontend**: React app on Vercel (v0.1.0) - [Repository](https://github.com/feniix/kinemotion-frontend)
- **kinemotion-backend**: FastAPI API on Cloud Run (v0.1.0) - [Repository](https://github.com/feniix/kinemotion-backend)

\`\`\`text
src/kinemotion/       # CLI analysis engine - v0.34.0
├── cli.py           # Main CLI commands
├── api.py           # Python API (used by backend via PyPI)
├── core/            # Shared: pose, filtering, auto_tuning, video_io
├── dropjump/        # Drop jump: cli, analysis, kinematics, debug_overlay
└── cmj/             # CMJ: cli, analysis, kinematics, joint_angles, debug_overlay

tests/               # 261 comprehensive tests (74.27% coverage)
docs/                # Documentation (Diátaxis framework)
\`\`\`

**Data Flow:**
\`\`\`
User uploads video → Frontend (React) → Backend API (FastAPI) → kinemotion CLI (from PyPI) → Results stored in Supabase → Frontend displays results
\`\`\`

**Deployment:**
- Frontend: Vercel (auto-deploy from kinemotion-frontend repo)
- Backend: Google Cloud Run (GitHub Actions from kinemotion-backend repo)
- CLI: PyPI (v0.34.0, used by backend + standalone usage)

**Backend Dependency:**
The backend imports kinemotion from PyPI:
\`\`\`python
# backend uses published package
dependencies = ["kinemotion>=0.30.0"]
\`\`\`
```

**README.md** - Update links:

```markdown
## Related Repositories

This is the **CLI analysis engine** (published to PyPI). For the web platform:

- **Backend API**: [kinemotion-backend](https://github.com/feniix/kinemotion-backend) - FastAPI backend on Cloud Run
- **Frontend**: [kinemotion-frontend](https://github.com/feniix/kinemotion-frontend) - React UI on Vercel

## Installation

\`\`\`bash
# For CLI usage
pip install kinemotion

# For backend development, see kinemotion-backend repository
\`\`\`
```

### 4.3 Remove .github/workflows/deploy-backend.yml

```bash
git rm .github/workflows/deploy-backend.yml
git commit -m "ci: remove backend deployment workflow

Backend deployment now handled in kinemotion-backend repository"
```

### 4.4 Update Serena Memories

```bash
# Update .serena/memories/current-project-architecture.md
# Update .serena/memories/project_overview.md
# Reflect that backend is now in separate repository
```

### 4.5 Update Basic-Memory Notes

Update these notes:
- `.basic-memory/project-management/project-state-summary-december-2025.md`
- `.basic-memory/codebase/codebase-architecture-overview.md`
- `.basic-memory/deployment/*.md` (add reference to new backend repo)

### 4.6 Update .github/dependabot.yml

Remove backend from dependabot (or keep commented out):

```yaml
# Backend dependencies now managed in kinemotion-backend repository
# - package-ecosystem: 'pip'
#   directory: '/backend'
#   ...
```

## Phase 5: Verification

### 5.1 Backend Repository Verification

**In kinemotion-backend repo:**
- [ ] Git history preserved (check `git log`)
- [ ] All files present
- [ ] Dependencies install: `uv sync`
- [ ] Tests pass: `uv run pytest`
- [ ] Type check passes: `uv run pyright`
- [ ] Linting passes: `uv run ruff check .`
- [ ] Server runs: `uv run uvicorn kinemotion_backend.app:app`
- [ ] Docker builds: `docker build -t test .`
- [ ] GitHub Actions workflow passes
- [ ] Cloud Run deployment succeeds
- [ ] Health endpoint responds: `curl https://kinemotion-backend-*.us-central1.run.app/health`

### 5.2 Main Repository Verification

**In kinemotion repo:**
- [ ] `backend/` directory removed
- [ ] Documentation updated (CLAUDE.md, README.md, etc.)
- [ ] Workflow file removed (.github/workflows/deploy-backend.yml)
- [ ] All tests still pass: `uv run pytest`
- [ ] CLI still works: `uv run kinemotion cmj-analyze video.mp4`
- [ ] PyPI package still publishes correctly

### 5.3 Integration Verification

**End-to-end:**
- [ ] Frontend can call backend API
- [ ] Backend can import kinemotion from PyPI
- [ ] Video analysis works with real metrics
- [ ] Authentication works end-to-end
- [ ] CORS configured correctly
- [ ] Logging works in Cloud Run

## Phase 6: Finalize Workload Identity Federation

After successful migration, update Workload Identity to only allow the backend repo:

```bash
gcloud iam workload-identity-pools providers update-oidc github-provider \
  --location=global \
  --workload-identity-pool=github-pool \
  --attribute-condition="assertion.repository_owner=='feniix' && assertion.repository=='kinemotion-backend'" \
  --project=kinemotion-backend
```

## Rollback Plan

If issues arise:

1. **Revert PR in main repo** that removed backend/
2. **Pause deployments from new backend repository**
3. **Restore old GitHub Actions workflow** in main repo
4. **Revert Workload Identity Federation** changes
5. **Investigate issues before re-attempting**

## Timeline Estimate

| Phase | Duration | Notes |
|-------|----------|-------|
| Phase 1: Extract | 30 min | Git history extraction |
| Phase 2: Setup new repo | 2 hours | Repository + workflow setup |
| Phase 3: WIF update | 30 min | Workload Identity Federation |
| Phase 4: Clean up main | 1 hour | Documentation updates |
| Phase 5: Verification | 1.5 hours | Testing and validation |
| Phase 6: Finalize | 15 min | Final WIF update |
| **Total** | **5-6 hours** | Can be done in stages |

## Benefits of Split

✅ **Pros:**
- Independent versioning and releases
- Clearer ownership boundaries
- Faster CI/CD (backend doesn't wait for CLI tests)
- Backend already decoupled via PyPI dependency
- Simpler testing (backend tests don't run on CLI changes)
- Independent deployment pipelines
- Easier for backend-only contributors

⚠️ **Cons:**
- Three repositories to manage (CLI, backend, frontend)
- Need to publish CLI to PyPI before backend can use new features
- Cross-repo coordination for breaking API changes
- More complex for full-stack changes
- Need to sync documentation

## Key Difference: Backend vs Frontend Split

**Backend is easier to split because:**
- Already uses kinemotion from PyPI (not local dependency)
- Self-contained Docker build
- Existing GitHub Actions workflow (just needs moving)
- Clean API boundary

**Main consideration:**
- Backend must wait for kinemotion to be published to PyPI
- When making breaking changes to CLI API, coordinate backend updates

## Alternative: Keep Backend in Monorepo

If you decide NOT to split backend:

**Consider:**
- Backend benefits less from split than frontend
- Backend and CLI are more tightly coupled (API changes)
- Current monorepo structure works well for coordinated changes
- Easier to make breaking changes to kinemotion.api

**Recommendation**: Split frontend first, evaluate backend split later.

## Key Files Affected

### Main Repository (kinemotion)
- `CLAUDE.md` - Architecture documentation
- `README.md` - Links and overview
- `.github/workflows/deploy-backend.yml` - REMOVE
- `.serena/memories/*.md` - Update architecture references
- `.basic-memory/**/*.md` - Update project state
- `.github/dependabot.yml` - Remove backend section

### New Backend Repository
- `README.md` - New standalone docs
- `.gitignore` - Backend-specific
- `pyproject.toml` - Update repository URL
- `.github/workflows/deploy.yml` - Moved from main repo
- Dockerfile - No changes needed
- All source code - No changes needed

## Critical Success Factors

1. ✅ **Backend already uses PyPI**: No code changes needed
2. ✅ **Workload Identity Federation**: Must be updated to allow new repo
3. ✅ **Docker build**: Already self-contained in backend/
4. ✅ **Secrets**: Already in Google Secret Manager (no changes needed)
5. ⚠️ **CLI releases**: Backend depends on kinemotion ≥0.30.0 from PyPI

## Important URLs

- **Backend Production**: `https://kinemotion-backend-1008251132682.us-central1.run.app`
- **Backend Health**: `https://kinemotion-backend-1008251132682.us-central1.run.app/health`
- **GCP Console**: https://console.cloud.google.com/run?project=kinemotion-backend
- **GitHub Actions**: https://github.com/feniix/kinemotion-backend/actions (after creation)

---

**Status**: Planning document - Ready to execute
**Next Step**: Decision point - confirm split is desired, then execute Phase 1

**Recommendation**: Consider splitting frontend first, then backend. Backend and CLI are more tightly coupled and may benefit from staying together longer.
