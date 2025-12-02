---
title: Backend Repository Split - Step-by-Step Execution Guide
type: note
permalink: deployment/backend-repository-split-step-by-step-execution-guide
tags:
- backend
- repository-split
- execution-guide
- step-by-step
- commands
---

# Backend Repository Split - Step-by-Step Execution Guide

**Created**: 2025-12-02
**Purpose**: Executable step-by-step instructions for splitting backend/ into kinemotion-backend repository
**Estimated Time**: 5-6 hours
**Status**: Ready to execute

## Prerequisites (5 minutes)

### 1. Backup Current Repository

```bash
cd /tmp
git clone --mirror https://github.com/feniix/kinemotion.git kinemotion-backup.git
```

### 2. Create New GitHub Repository

**Via GitHub Web UI:**
1. Go to: https://github.com/new
2. Repository name: `kinemotion-backend`
3. Description: `FastAPI backend for Kinemotion video analysis`
4. Visibility: Choose (Public/Private)
5. **Important**: DO NOT initialize with README, .gitignore, or license
6. Click "Create repository"

---

## Phase 1: Extract Backend with Git History (30 minutes)

### Step 1.1: Clone and Prepare

```bash
cd /tmp
git clone https://github.com/feniix/kinemotion.git kinemotion-backend-extract
cd kinemotion-backend-extract
```

### Step 1.2: Extract Backend Directory

```bash
git subtree split --prefix=backend -b backend-only
```

**Expected output:**
```
Rewrote <commit> (XX/YY) (ZZ seconds)
Created branch 'backend-only'
```

### Step 1.3: Create New Repository

```bash
cd ..
mkdir kinemotion-backend
cd kinemotion-backend
git init
```

### Step 1.4: Pull Extracted History

```bash
git pull ../kinemotion-backend-extract backend-only
```

### Step 1.5: Verify Extraction

```bash
# Check history only shows backend commits
git log --oneline | head -10

# Verify files are present
ls -la
```

**Expected files:**
- src/
- tests/
- Dockerfile
- pyproject.toml
- uv.lock
- README.md
- .dockerignore
- .env.example

### Step 1.6: Push to GitHub

```bash
git remote add origin git@github.com:feniix/kinemotion-backend.git
git branch -M main
git push -u origin main
```

### Step 1.7: Clean Up

```bash
cd ..
rm -rf kinemotion-backend-extract
```

**Checkpoint:** Verify at https://github.com/feniix/kinemotion-backend that commits are visible

---

## Phase 2: Set Up New Backend Repository (2 hours)

### Step 2.1: Create .gitignore

```bash
cd /tmp/kinemotion-backend

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
```

### Step 2.2: Update README.md

```bash
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

## Quick Start

### Installation

```bash
uv sync
```

### Running Locally

```bash
# Development
uv run uvicorn kinemotion_backend.app:app --reload

# Production
uv run uvicorn kinemotion_backend.app:app --host 0.0.0.0 --port 8000
```

Access API at http://localhost:8000

### API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Environment Variables

Create `.env` file:

```bash
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key

# CORS
CORS_ORIGINS=https://kinemotion.vercel.app,http://localhost:3000

# Logging
LOG_LEVEL=INFO
JSON_LOGS=true
```

## Deployment

Deployed to Google Cloud Run via GitHub Actions.

Push to `main` branch triggers deployment.

## Testing

```bash
uv run pytest                    # Run tests
uv run pytest --cov              # With coverage
uv run pyright                   # Type check
uv run ruff check .              # Lint
```

## Related Repositories

- **CLI**: [kinemotion](https://github.com/feniix/kinemotion) - Analysis engine (PyPI)
- **Frontend**: [kinemotion-frontend](https://github.com/feniix/kinemotion-frontend) - React UI

## License

MIT
EOF
```

### Step 2.3: Update pyproject.toml

```bash
# Edit pyproject.toml manually
nano pyproject.toml
```

**Change these lines:**

```toml
[project.urls]
Homepage = "https://github.com/feniix/kinemotion-backend"
Repository = "https://github.com/feniix/kinemotion-backend"
Issues = "https://github.com/feniix/kinemotion-backend/issues"
```

### Step 2.4: Commit Initial Setup

```bash
git add .gitignore README.md pyproject.toml
git commit -m "docs: update repository setup for standalone backend"
git push
```

### Step 2.5: Create GitHub Actions Workflow

```bash
mkdir -p .github/workflows

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
```

### Step 2.6: Commit Workflow

```bash
git add .github/workflows/deploy.yml
git commit -m "ci: add Cloud Run deployment workflow"
git push
```

**Checkpoint:** Verify workflow file at https://github.com/feniix/kinemotion-backend/blob/main/.github/workflows/deploy.yml

---

## Phase 3: Update Workload Identity Federation (30 minutes)

### Step 3.1: Check Current Configuration

```bash
gcloud iam workload-identity-pools providers describe github-provider \
  --location=global \
  --workload-identity-pool=github-pool \
  --project=kinemotion-backend
```

### Step 3.2: Update WIF to Allow New Repository

```bash
gcloud iam workload-identity-pools providers update-oidc github-provider \
  --location=global \
  --workload-identity-pool=github-pool \
  --attribute-condition="assertion.repository_owner=='feniix' && (assertion.repository=='kinemotion' || assertion.repository=='kinemotion-backend')" \
  --project=kinemotion-backend
```

**Note:** This allows BOTH repositories to deploy (temporary during migration).

### Step 3.3: Verify Service Account Bindings

```bash
gcloud iam service-accounts get-iam-policy \
  github-actions-deploy@kinemotion-backend.iam.gserviceaccount.com \
  --project=kinemotion-backend
```

**Expected output should show:** `principalSet` for Workload Identity

---

## Phase 4: Configure GitHub Repository Settings (15 minutes)

### Step 4.1: Branch Protection

**Via GitHub Web UI:**
1. Go to: https://github.com/feniix/kinemotion-backend/settings/branches
2. Click "Add branch protection rule"
3. Branch name pattern: `main`
4. Check:
   - ✅ Require a pull request before merging
   - ✅ Require status checks to pass before merging
   - Select status checks: `Run Tests`, `Build and Push Docker Image to GCR`
5. Click "Create"

### Step 4.2: Create Production Environment

**Via GitHub Web UI:**
1. Go to: https://github.com/feniix/kinemotion-backend/settings/environments
2. Click "New environment"
3. Name: `production`
4. Add deployment protection rules if desired
5. Click "Configure environment"

### Step 4.3: Verify Secrets (None Needed)

**Via GitHub Web UI:**
1. Go to: https://github.com/feniix/kinemotion-backend/settings/secrets/actions
2. **No secrets should be needed** - Workload Identity Federation handles authentication via OIDC
3. Verify no secrets are listed (or only harmless ones)

---

## Phase 5: Test New Backend Repository (1 hour)

### Step 5.1: Test Locally

```bash
cd /tmp/kinemotion-backend

# Install dependencies
uv sync

# Run tests
uv run pytest

# Type checking
uv run pyright

# Linting
uv run ruff check .

# Start server
uv run uvicorn kinemotion_backend.app:app --reload
```

**In another terminal:**

```bash
# Test health endpoint
curl http://localhost:8000/health
```

**Expected response:**
```json
{"status": "healthy", "service": "kinemotion-backend"}
```

### Step 5.2: Test Docker Build

```bash
cd /tmp/kinemotion-backend

docker build -t kinemotion-backend-test .
```

**Expected:** Build completes successfully

### Step 5.3: Test Docker Run

```bash
docker run -p 8080:8080 kinemotion-backend-test
```

**In another terminal:**

```bash
curl http://localhost:8080/health
```

**Expected response:**
```json
{"status": "healthy", "service": "kinemotion-backend"}
```

### Step 5.4: Trigger GitHub Actions Deployment

```bash
cd /tmp/kinemotion-backend

# Make a small change to trigger deployment
echo "" >> README.md
git add README.md
git commit -m "test: trigger deployment"
git push
```

**Monitor at:** https://github.com/feniix/kinemotion-backend/actions

**Wait for:**
- ✅ Run Tests (green)
- ✅ Build and Push Docker Image to GCR (green)
- ✅ Deploy to Google Cloud Run (green)

### Step 5.5: Verify Cloud Run Deployment

```bash
curl https://kinemotion-backend-1008251132682.us-central1.run.app/health
```

**Expected response:**
```json
{"status": "healthy", "service": "kinemotion-backend"}
```

**Checkpoint:** Backend is now deployed and accessible from new repository!

---

## Phase 6: Clean Up Main Repository (1 hour)

### Step 6.1: Create Cleanup Branch

```bash
cd /Users/feniix/src/personal/cursor/dropjump-claude

git checkout main
git pull
git checkout -b chore/remove-backend-directory
```

### Step 6.2: Remove Backend Directory

```bash
git rm -r backend/
```

### Step 6.3: Remove Backend Workflow

```bash
git rm .github/workflows/deploy-backend.yml
```

### Step 6.4: Commit Removal

```bash
git commit -m "chore: move backend to separate repository

Backend has been extracted to:
https://github.com/feniix/kinemotion-backend

The backend continues to use the kinemotion package from PyPI (>=0.30.0)
for video analysis."
```

### Step 6.5: Update CLAUDE.md

```bash
nano CLAUDE.md
```

**Find the "Full-Stack Architecture" section and update to:**

```markdown
## Architecture

### Full-Stack Architecture

The project consists of three separate repositories:

**Repositories:**
- **kinemotion** (this repo): CLI analysis engine (v0.34.0) - Published to PyPI
- **kinemotion-frontend**: React app on Vercel (v0.1.0) - [Repository](https://github.com/feniix/kinemotion-frontend)
- **kinemotion-backend**: FastAPI API on Cloud Run (v0.1.0) - [Repository](https://github.com/feniix/kinemotion-backend)

```text
src/kinemotion/       # CLI analysis engine - v0.34.0
├── cli.py           # Main CLI commands
├── api.py           # Python API (used by backend via PyPI)
├── core/            # Shared: pose, filtering, auto_tuning, video_io
├── dropjump/        # Drop jump: cli, analysis, kinematics, debug_overlay
└── cmj/             # CMJ: cli, analysis, kinematics, joint_angles, debug_overlay

tests/               # 261 comprehensive tests (74.27% coverage)
docs/                # Documentation (Diátaxis framework)
```

**Data Flow:**
```
User uploads video → Frontend (React) → Backend API (FastAPI) → kinemotion CLI (from PyPI) → Results stored in Supabase → Frontend displays results
```

**Deployment:**
- Frontend: Vercel (auto-deploy from kinemotion-frontend repo)
- Backend: Google Cloud Run (GitHub Actions from kinemotion-backend repo)
- CLI: PyPI (v0.34.0, used by backend + standalone usage)

**Backend Dependency:**
The backend imports kinemotion from PyPI:
```python
# backend uses published package
dependencies = ["kinemotion>=0.30.0"]
```
```

### Step 6.6: Update README.md

```bash
nano README.md
```

**Add "Related Repositories" section:**

```markdown
## Related Repositories

This is the **CLI analysis engine** (published to PyPI). For the web platform:

- **Backend API**: [kinemotion-backend](https://github.com/feniix/kinemotion-backend) - FastAPI backend on Cloud Run
- **Frontend**: [kinemotion-frontend](https://github.com/feniix/kinemotion-frontend) - React UI on Vercel

## Installation

```bash
# For CLI usage
pip install kinemotion

# For backend/frontend development, see respective repositories
```
```

### Step 6.7: Commit Documentation Updates

```bash
git add CLAUDE.md README.md
git commit -m "docs: update architecture documentation for backend split"
```

### Step 6.8: Push and Create PR

```bash
git push -u origin chore/remove-backend-directory
```

### Step 6.9: Create Pull Request

**Via GitHub Web UI:**
1. Go to: https://github.com/feniix/kinemotion/pulls
2. Click "New pull request"
3. Base: `main`, Compare: `chore/remove-backend-directory`
4. Title: `chore: move backend to separate repository`
5. Description:
   ```
   Backend has been extracted to: https://github.com/feniix/kinemotion-backend

   Changes:
   - Removed backend/ directory
   - Removed .github/workflows/deploy-backend.yml
   - Updated CLAUDE.md architecture documentation
   - Updated README.md with related repositories

   Backend continues to use kinemotion from PyPI (>=0.30.0).
   ```
6. Click "Create pull request"

### Step 6.10: Review and Merge PR

1. Review changes in PR
2. Ensure CI passes
3. Merge PR
4. Delete branch `chore/remove-backend-directory`

**Checkpoint:** Main repository no longer has backend/

---

## Phase 7: Finalize Workload Identity Federation (15 minutes)

### Step 7.1: Wait for Confirmation

**Verify everything works:**
- [ ] Backend deploys from new repository
- [ ] Frontend can call backend API
- [ ] No issues in production

### Step 7.2: Update WIF to Backend-Only

```bash
gcloud iam workload-identity-pools providers update-oidc github-provider \
  --location=global \
  --workload-identity-pool=github-pool \
  --attribute-condition="assertion.repository_owner=='feniix' && assertion.repository=='kinemotion-backend'" \
  --project=kinemotion-backend
```

**This removes main kinemotion repo from WIF (backend repo only).**

### Step 7.3: Verify Final Configuration

```bash
gcloud iam workload-identity-pools providers describe github-provider \
  --location=global \
  --workload-identity-pool=github-pool \
  --project=kinemotion-backend
```

**Expected:** `attributeCondition` should only mention `kinemotion-backend`

---

## Verification Checklist

### ✅ Backend Repository (kinemotion-backend)

- [ ] Git history preserved: `git log` shows backend commits
- [ ] All files present: src/, tests/, Dockerfile, pyproject.toml
- [ ] Dependencies install: `uv sync` works
- [ ] Tests pass: `uv run pytest` passes
- [ ] Type check passes: `uv run pyright` passes
- [ ] Linting passes: `uv run ruff check .` passes
- [ ] Server runs locally: `uv run uvicorn kinemotion_backend.app:app`
- [ ] Docker builds: `docker build -t test .` succeeds
- [ ] GitHub Actions workflow runs and passes
- [ ] Cloud Run deployment succeeds
- [ ] Health endpoint responds: https://kinemotion-backend-1008251132682.us-central1.run.app/health

### ✅ Main Repository (kinemotion)

- [ ] `backend/` directory removed
- [ ] `.github/workflows/deploy-backend.yml` removed
- [ ] CLAUDE.md updated with new architecture
- [ ] README.md updated with related repositories
- [ ] All CLI tests still pass: `uv run pytest`
- [ ] CLI still works: `uv run kinemotion cmj-analyze video.mp4`

### ✅ Integration

- [ ] Frontend can call backend API
- [ ] Backend can import kinemotion from PyPI
- [ ] Video analysis works end-to-end
- [ ] Authentication works
- [ ] CORS configured correctly

---

## Rollback Plan

### If Something Goes Wrong

**Step 1: Revert PR in Main Repo**

```bash
cd /Users/feniix/src/personal/cursor/dropjump-claude
git checkout main
git pull
git revert <commit-hash-that-removed-backend>
git push
```

**Step 2: Pause New Backend Deployments**

```bash
# Delete or disable workflow in kinemotion-backend
cd /tmp/kinemotion-backend
git rm .github/workflows/deploy.yml
git commit -m "temp: disable deployments"
git push
```

**Step 3: Restore WIF to Original State**

```bash
gcloud iam workload-identity-pools providers update-oidc github-provider \
  --location=global \
  --workload-identity-pool=github-pool \
  --attribute-condition="assertion.repository_owner=='feniix' && assertion.repository=='kinemotion'" \
  --project=kinemotion-backend
```

**Step 4: Restore Backend Workflow in Main Repo**

```bash
cd /Users/feniix/src/personal/cursor/dropjump-claude
git checkout <commit-before-removal>
git checkout .github/workflows/deploy-backend.yml
git add .github/workflows/deploy-backend.yml
git commit -m "restore: backend deployment workflow"
git push
```

---

## Timeline Summary

| Phase | Duration | Description |
|-------|----------|-------------|
| Prerequisites | 5 min | Backup repo, create GitHub repo |
| Phase 1 | 30 min | Extract backend with git subtree |
| Phase 2 | 2 hours | Set up files, workflows, push to GitHub |
| Phase 3 | 30 min | Update Workload Identity Federation |
| Phase 4 | 15 min | Configure GitHub settings |
| Phase 5 | 1 hour | Test locally, Docker, and Cloud Run |
| Phase 6 | 1 hour | Remove backend from main repo |
| Phase 7 | 15 min | Finalize WIF |
| **TOTAL** | **5-6 hours** | |

---

## Quick Reference Commands

### Start Extraction
```bash
cd /tmp
git clone https://github.com/feniix/kinemotion.git kinemotion-backend-extract
cd kinemotion-backend-extract
git subtree split --prefix=backend -b backend-only
```

### Test Backend Locally
```bash
cd /tmp/kinemotion-backend
uv sync
uv run pytest
uv run pyright
uv run ruff check .
uv run uvicorn kinemotion_backend.app:app
```

### Check Cloud Run Health
```bash
curl https://kinemotion-backend-1008251132682.us-central1.run.app/health
```

### Monitor GitHub Actions
```
https://github.com/feniix/kinemotion-backend/actions
```

---

**Status**: Ready to execute
**Last Updated**: 2025-12-02
