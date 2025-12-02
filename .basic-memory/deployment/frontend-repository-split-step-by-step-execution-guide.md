---
title: Frontend Repository Split - Step-by-Step Execution Guide
type: note
permalink: deployment/frontend-repository-split-step-by-step-execution-guide
tags:
- frontend
- repository-split
- execution-guide
- step-by-step
- commands
- vercel
---

# Frontend Repository Split - Step-by-Step Execution Guide

**Created**: 2025-12-02
**Purpose**: Executable step-by-step instructions for splitting frontend/ into kinemotion-frontend repository
**Estimated Time**: 4-5 hours
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
2. Repository name: `kinemotion-frontend`
3. Description: `React frontend for Kinemotion video analysis`
4. Visibility: Choose (Public/Private)
5. **Important**: DO NOT initialize with README, .gitignore, or license
6. Click "Create repository"

---

## Phase 1: Extract Frontend with Git History (30 minutes)

### Step 1.1: Clone and Prepare

```bash
cd /tmp
git clone https://github.com/feniix/kinemotion.git kinemotion-frontend-extract
cd kinemotion-frontend-extract
```

### Step 1.2: Extract Frontend Directory

```bash
git subtree split --prefix=frontend -b frontend-only
```

**Expected output:**
```
Rewrote <commit> (XX/YY) (ZZ seconds)
Created branch 'frontend-only'
```

### Step 1.3: Create New Repository

```bash
cd ..
mkdir kinemotion-frontend
cd kinemotion-frontend
git init
```

### Step 1.4: Pull Extracted History

```bash
git pull ../kinemotion-frontend-extract frontend-only
```

### Step 1.5: Verify Extraction

```bash
# Check history only shows frontend commits
git log --oneline | head -10

# Verify files are present
ls -la
```

**Expected files:**
- src/
- public/
- package.json
- tsconfig.json
- vite.config.ts
- index.html
- .yarn/
- yarn.lock

### Step 1.6: Push to GitHub

```bash
git remote add origin git@github.com:feniix/kinemotion-frontend.git
git branch -M main
git push -u origin main
```

### Step 1.7: Clean Up

```bash
cd ..
rm -rf kinemotion-frontend-extract
```

**Checkpoint:** Verify at https://github.com/feniix/kinemotion-frontend that commits are visible

---

## Phase 2: Set Up New Frontend Repository (1.5 hours)

### Step 2.1: Create .gitignore

```bash
cd /tmp/kinemotion-frontend

cat > .gitignore <<'EOF'
# Dependencies
node_modules/
.pnp
.pnp.js

# Yarn
.yarn/*
!.yarn/patches
!.yarn/plugins
!.yarn/releases
!.yarn/sdks
!.yarn/versions
.yarn/install-state.gz
.yarn/cache

# Testing
/coverage

# Production
/dist
/build

# Misc
.DS_Store
*.pem
.env.local
.env.development.local
.env.test.local
.env.production.local

# Logs
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# IDEs
.vscode/
.idea/
*.swp
*.swo

# Vercel
.vercel
EOF
```

### Step 2.2: Update README.md

```bash
cat > README.md <<'EOF'
# Kinemotion Frontend

React frontend for Kinemotion video-based kinematic analysis.

## Tech Stack

- **Framework**: React 19.2.0
- **Build Tool**: Vite 7.2.4
- **Language**: TypeScript 5.9.3
- **Package Manager**: Yarn 4.12.0
- **Auth**: Supabase
- **Deployment**: Vercel

## Quick Start

### Installation

```bash
yarn install
```

### Running Locally

```bash
# Development server
yarn dev

# Production build
yarn build

# Preview production build
yarn preview

# Type check
yarn type-check
```

Access app at http://localhost:3000

## Environment Variables

Create a `.env.local` file:

```bash
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
VITE_API_URL=https://kinemotion-backend-1008251132682.us-central1.run.app
```

## Deployment

Deployed to Vercel. Push to `main` branch triggers automatic deployment.

## Architecture

```
User → Frontend (React) → Backend API (FastAPI) → kinemotion CLI → Supabase
```

## Related Repositories

- **CLI**: [kinemotion](https://github.com/feniix/kinemotion) - Analysis engine (PyPI)
- **Backend**: [kinemotion-backend](https://github.com/feniix/kinemotion-backend) - FastAPI API

## Development

```bash
# Install dependencies
yarn install

# Run dev server
yarn dev

# Type check
yarn type-check

# Build for production
yarn build
```

## License

MIT
EOF
```

### Step 2.3: Update package.json

```bash
# Edit package.json manually
nano package.json
```

**Update these fields:**

```json
{
  "name": "kinemotion-frontend",
  "version": "0.1.0",
  "repository": {
    "type": "git",
    "url": "https://github.com/feniix/kinemotion-frontend.git"
  },
  "homepage": "https://kinemotion.vercel.app",
  "bugs": {
    "url": "https://github.com/feniix/kinemotion-frontend/issues"
  }
}
```

### Step 2.4: Commit Initial Setup

```bash
git add .gitignore README.md package.json
git commit -m "docs: update repository setup for standalone frontend"
git push
```

### Step 2.5: Create GitHub Actions Workflow (Optional)

```bash
mkdir -p .github/workflows

cat > .github/workflows/ci.yml <<'EOF'
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    name: Type Check and Build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6

      - name: Setup Node.js
        uses: actions/setup-node@v6
        with:
          node-version: '20'
          cache: 'yarn'

      - name: Install dependencies
        run: yarn install --immutable

      - name: Type check
        run: yarn type-check

      - name: Build
        run: yarn build
        env:
          VITE_SUPABASE_URL: ${{ secrets.VITE_SUPABASE_URL }}
          VITE_SUPABASE_ANON_KEY: ${{ secrets.VITE_SUPABASE_ANON_KEY }}
          VITE_API_URL: https://kinemotion-backend-1008251132682.us-central1.run.app
EOF
```

### Step 2.6: Commit Workflow (Optional)

```bash
git add .github/workflows/ci.yml
git commit -m "ci: add type check and build workflow"
git push
```

**Checkpoint:** Verify workflow file at https://github.com/feniix/kinemotion-frontend/blob/main/.github/workflows/ci.yml

---

## Phase 3: Configure GitHub Repository Settings (30 minutes)

### Step 3.1: Branch Protection

**Via GitHub Web UI:**
1. Go to: https://github.com/feniix/kinemotion-frontend/settings/branches
2. Click "Add branch protection rule"
3. Branch name pattern: `main`
4. Check:
   - ✅ Require a pull request before merging
   - ✅ Require status checks to pass before merging (if CI is set up)
   - Select status checks: `Type Check and Build` (if workflow added)
5. Click "Create"

### Step 3.2: Configure GitHub Secrets (If CI Workflow Added)

**Via GitHub Web UI:**
1. Go to: https://github.com/feniix/kinemotion-frontend/settings/secrets/actions
2. Click "New repository secret"
3. Add the following secrets:
   - Name: `VITE_SUPABASE_URL`, Value: Your Supabase URL
   - Name: `VITE_SUPABASE_ANON_KEY`, Value: Your Supabase anon key

---

## Phase 4: Update Vercel Configuration (1 hour)

### Step 4.1: Disconnect Current Vercel Connection

**Via Vercel Dashboard:**
1. Go to: https://vercel.com/dashboard
2. Find your `kinemotion` project
3. Click on the project
4. Go to "Settings" → "Git"
5. Scroll to "Disconnect Git Repository"
6. Click "Disconnect"

### Step 4.2: Connect to New Repository

**Via Vercel Dashboard:**
1. Go to: https://vercel.com/new
2. Select "Import Git Repository"
3. Choose `feniix/kinemotion-frontend`
4. Configure project:
   - **Framework Preset**: Vite
   - **Root Directory**: `.` (leave empty or set to `/`)
   - **Build Command**: `yarn build`
   - **Output Directory**: `dist`
   - **Install Command**: `yarn install`
5. Click "Deploy"

### Step 4.3: Configure Environment Variables in Vercel

**Via Vercel Dashboard:**
1. Go to project settings
2. Navigate to "Environment Variables"
3. Add the following variables:
   - `VITE_SUPABASE_URL`: Your Supabase URL
   - `VITE_SUPABASE_ANON_KEY`: Your Supabase anon key
   - `VITE_API_URL`: `https://kinemotion-backend-1008251132682.us-central1.run.app`
4. Apply to: Production, Preview, Development
5. Click "Save"

### Step 4.4: Trigger Manual Deployment

**Via Vercel Dashboard:**
1. Go to "Deployments" tab
2. Click "Redeploy" on the latest deployment
3. Wait for deployment to complete

### Step 4.5: Verify Deployment

```bash
curl https://kinemotion.vercel.app
```

**Expected:** HTML response from React app

**Manual test:** Visit https://kinemotion.vercel.app in browser

**Checkpoint:** Frontend is now deployed from new repository!

---

## Phase 5: Test New Frontend Repository (30 minutes)

### Step 5.1: Test Locally

```bash
cd /tmp/kinemotion-frontend

# Install dependencies
yarn install

# Type check
yarn type-check

# Build
yarn build

# Start dev server
yarn dev
```

**Expected:** Dev server starts on http://localhost:5173

**In browser:**
1. Visit http://localhost:5173
2. Try logging in
3. Try uploading a video (if backend is available)

### Step 5.2: Test Production Build

```bash
cd /tmp/kinemotion-frontend

# Build for production
yarn build

# Preview production build
yarn preview
```

**Expected:** Production build succeeds and preview server starts

### Step 5.3: Verify Vercel Deployment

**Via browser:**
1. Visit: https://kinemotion.vercel.app
2. Test authentication
3. Test video upload (if backend available)
4. Check console for errors

**Checkpoint:** Frontend works correctly from new repository!

---

## Phase 6: Clean Up Main Repository (1 hour)

### Step 6.1: Create Cleanup Branch

```bash
cd /Users/feniix/src/personal/cursor/dropjump-claude

git checkout main
git pull
git checkout -b chore/remove-frontend-directory
```

### Step 6.2: Remove Frontend Directory

```bash
git rm -r frontend/
```

### Step 6.3: Update .gitignore

```bash
nano .gitignore
```

**Remove these lines:**
```
# Frontend-specific entries (if any)
frontend/.pnp.cjs
frontend/.pnp.loader.mjs
frontend/.yarn/install-state.gz
frontend/.yarn/cache/
!frontend/package.json
```

### Step 6.4: Update .pre-commit-config.yaml

```bash
nano .pre-commit-config.yaml
```

**Find and remove frontend exclusions:**
```yaml
# Remove this line:
exclude: 'frontend/.yarn/releases/yarn-.*\.cjs$'
```

### Step 6.5: Update .github/workflows/release.yml

```bash
nano .github/workflows/release.yml
```

**Remove frontend path from paths-ignore:**
```yaml
on:
  push:
    branches: [main]
    paths-ignore:
      - 'docs/**'
      - 'backend/**'
      # - 'frontend/**'  # REMOVE THIS LINE
      - '*.md'
```

### Step 6.6: Commit Removal

```bash
git add .gitignore .pre-commit-config.yaml .github/workflows/release.yml
git commit -m "chore: move frontend to separate repository

Frontend has been extracted to:
https://github.com/feniix/kinemotion-frontend

This commit removes the frontend/ directory and cleans up
frontend-specific configuration from the main repository."
```

### Step 6.7: Update CLAUDE.md

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
```

### Step 6.8: Update README.md

```bash
nano README.md
```

**Add "Related Repositories" section:**

```markdown
## Related Repositories

This is the **CLI analysis engine** (published to PyPI). For the web platform:

- **Frontend**: [kinemotion-frontend](https://github.com/feniix/kinemotion-frontend) - React UI on Vercel
- **Backend API**: [kinemotion-backend](https://github.com/feniix/kinemotion-backend) - FastAPI backend on Cloud Run

## Installation

```bash
# For CLI usage
pip install kinemotion

# For backend/frontend development, see respective repositories
```
```

### Step 6.9: Update .claude/agents/frontend-developer.md

```bash
nano .claude/agents/frontend-developer.md
```

**Update the "Context" section:**

```markdown
## Context

The frontend lives in a separate repository:
https://github.com/feniix/kinemotion-frontend

When working on frontend issues, you should:
1. Work in the kinemotion-frontend repository
2. Reference backend API contracts from the main kinemotion repository
3. Test integration with the deployed backend API
```

### Step 6.10: Update Basic-Memory Notes

```bash
# Update project architecture notes
nano .basic-memory/codebase/codebase-architecture-overview.md
nano .basic-memory/project-management/project-state-summary-december-2025.md
```

**Update to reflect frontend is in separate repository**

### Step 6.11: Commit Documentation Updates

```bash
git add CLAUDE.md README.md .claude/agents/frontend-developer.md .basic-memory/
git commit -m "docs: update architecture documentation for frontend split"
```

### Step 6.12: Push and Create PR

```bash
git push -u origin chore/remove-frontend-directory
```

### Step 6.13: Create Pull Request

**Via GitHub Web UI:**
1. Go to: https://github.com/feniix/kinemotion/pulls
2. Click "New pull request"
3. Base: `main`, Compare: `chore/remove-frontend-directory`
4. Title: `chore: move frontend to separate repository`
5. Description:
   ```
   Frontend has been extracted to: https://github.com/feniix/kinemotion-frontend

   Changes:
   - Removed frontend/ directory
   - Cleaned up .gitignore, .pre-commit-config.yaml
   - Updated .github/workflows/release.yml
   - Updated CLAUDE.md architecture documentation
   - Updated README.md with related repositories
   - Updated frontend-developer agent context
   - Updated basic-memory notes
   ```
6. Click "Create pull request"

### Step 6.14: Review and Merge PR

1. Review changes in PR
2. Ensure CI passes
3. Merge PR
4. Delete branch `chore/remove-frontend-directory`

**Checkpoint:** Main repository no longer has frontend/

---

## Verification Checklist

### ✅ Frontend Repository (kinemotion-frontend)

- [ ] Git history preserved: `git log` shows frontend commits
- [ ] All files present: src/, public/, package.json, vite.config.ts
- [ ] Dependencies install: `yarn install` works
- [ ] Type check passes: `yarn type-check` passes
- [ ] Build succeeds: `yarn build` succeeds
- [ ] Dev server runs: `yarn dev` starts successfully
- [ ] Vercel deployment succeeds
- [ ] Vercel environment variables configured
- [ ] Site accessible: https://kinemotion.vercel.app

### ✅ Main Repository (kinemotion)

- [ ] `frontend/` directory removed
- [ ] `.gitignore` cleaned up
- [ ] `.pre-commit-config.yaml` updated
- [ ] `.github/workflows/release.yml` updated
- [ ] CLAUDE.md updated with new architecture
- [ ] README.md updated with related repositories
- [ ] `.claude/agents/frontend-developer.md` updated
- [ ] Basic-memory notes updated
- [ ] All CLI tests still pass: `uv run pytest`
- [ ] CLI still works: `uv run kinemotion cmj-analyze video.mp4`

### ✅ Integration

- [ ] Frontend can call backend API
- [ ] Authentication works end-to-end
- [ ] Video upload and analysis works
- [ ] CORS configured correctly
- [ ] No console errors in browser

---

## Rollback Plan

### If Something Goes Wrong

**Step 1: Revert PR in Main Repo**

```bash
cd /Users/feniix/src/personal/cursor/dropjump-claude
git checkout main
git pull
git revert <commit-hash-that-removed-frontend>
git push
```

**Step 2: Disconnect Vercel from New Repository**

**Via Vercel Dashboard:**
1. Go to project settings
2. Disconnect from kinemotion-frontend repository

**Step 3: Reconnect Vercel to Main Repository**

**Via Vercel Dashboard:**
1. Connect to `feniix/kinemotion` repository
2. Set root directory to `frontend/`
3. Reconfigure build settings:
   - Build Command: `yarn build`
   - Output Directory: `dist`
   - Install Command: `yarn install`
4. Redeploy

**Step 4: Archive or Delete New Frontend Repository (Optional)**

```bash
# Archive on GitHub via Settings → General → Archive this repository
```

---

## Timeline Summary

| Phase | Duration | Description |
|-------|----------|-------------|
| Prerequisites | 5 min | Backup repo, create GitHub repo |
| Phase 1 | 30 min | Extract frontend with git subtree |
| Phase 2 | 1.5 hours | Set up files, workflows, push to GitHub |
| Phase 3 | 30 min | Configure GitHub settings |
| Phase 4 | 1 hour | Reconnect Vercel, configure env vars |
| Phase 5 | 30 min | Test locally and in production |
| Phase 6 | 1 hour | Remove frontend from main repo |
| **TOTAL** | **4-5 hours** | |

---

## Quick Reference Commands

### Start Extraction
```bash
cd /tmp
git clone https://github.com/feniix/kinemotion.git kinemotion-frontend-extract
cd kinemotion-frontend-extract
git subtree split --prefix=frontend -b frontend-only
```

### Test Frontend Locally
```bash
cd /tmp/kinemotion-frontend
yarn install
yarn type-check
yarn build
yarn dev
```

### Check Vercel Deployment
```bash
curl https://kinemotion.vercel.app
```

### Monitor GitHub Actions (If CI Added)
```
https://github.com/feniix/kinemotion-frontend/actions
```

---

## Post-Migration Tasks

### Update Documentation in New Frontend Repo

1. Add CONTRIBUTING.md (link to main repo)
2. Add architecture diagrams
3. Document API integration points
4. Add development setup guide

### Optional Enhancements

1. Add Playwright/Cypress for E2E testing
2. Add Storybook for component development
3. Set up Sentry for error tracking
4. Configure preview deployments for PRs
5. Add bundle size monitoring

---

**Status**: Ready to execute
**Last Updated**: 2025-12-02
