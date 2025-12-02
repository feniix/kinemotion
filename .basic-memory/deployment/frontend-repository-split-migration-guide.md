---
title: Frontend Repository Split Migration Guide
type: note
permalink: deployment/frontend-repository-split-migration-guide
tags:
- frontend
- repository-split
- git
- migration
- monorepo
- polyrepo
---

# Frontend Repository Split Migration Guide

**Created**: 2025-12-02
**Purpose**: Detailed guide for extracting frontend/ directory into its own Git repository
**Status**: Planning document

## Overview

This guide outlines the steps to split the `frontend/` directory from the kinemotion monorepo into a separate repository while preserving Git history and updating all references.

**Current State:**
- Frontend lives in `frontend/` within the main kinemotion repository
- Frontend v0.1.0 (React + Vite + TypeScript + Supabase)
- Deployed to Vercel (manual deployment, no CI/CD yet)
- Minimal coupling to monorepo (self-contained with own package.json)

**Target State:**
- Frontend in separate `kinemotion-frontend` repository
- Preserves Git history for frontend/ files
- Independent versioning and deployment
- Updated references in main repository

## Prerequisites

✅ **Before starting:**
- [ ] Backup current repository: `git clone --mirror <repo-url> kinemotion-backup.git`
- [ ] Create new GitHub repository: `kinemotion-frontend` (empty, no README)
- [ ] Communicate with team about repository split
- [ ] Verify Vercel deployment settings
- [ ] Check if there are any open PRs affecting frontend/

## Phase 1: Extract Frontend with Git History

### Option A: Using git subtree split (Recommended)

This preserves the full Git history for frontend files.

```bash
# 1. Clone the main repository (fresh clone recommended)
cd /tmp
git clone https://github.com/feniix/kinemotion.git kinemotion-frontend-extract
cd kinemotion-frontend-extract

# 2. Extract frontend/ directory with history
git subtree split --prefix=frontend -b frontend-only

# 3. Create a new temporary directory for the new repository
cd ..
mkdir kinemotion-frontend
cd kinemotion-frontend
git init

# 4. Pull the frontend-only branch
git pull ../kinemotion-frontend-extract frontend-only

# 5. Review the extracted history
git log --oneline
# Should show only commits that touched frontend/

# 6. Add new remote and push
git remote add origin git@github.com:feniix/kinemotion-frontend.git
git branch -M main
git push -u origin main

# 7. Clean up
cd ..
rm -rf kinemotion-frontend-extract
```

### Option B: Using git filter-repo (Alternative)

More powerful but requires installation of `git-filter-repo`.

```bash
# 1. Install git-filter-repo
pip install git-filter-repo

# 2. Clone and filter
git clone https://github.com/feniix/kinemotion.git kinemotion-frontend
cd kinemotion-frontend

# 3. Filter to keep only frontend/
git filter-repo --path frontend/ --path-rename frontend/:

# 4. Push to new repository
git remote add origin git@github.com:feniix/kinemotion-frontend.git
git push -u origin main
```

## Phase 2: Set Up New Frontend Repository

### 2.1 Add Repository Files

```bash
cd kinemotion-frontend

# Create .gitignore (frontend-specific)
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

# Create README.md (if doesn't exist or needs update)
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

\`\`\`bash
# Install dependencies
yarn install

# Run development server
yarn dev

# Build for production
yarn build

# Preview production build
yarn preview

# Type check
yarn type-check
\`\`\`

## Environment Variables

Create a \`.env.local\` file:

\`\`\`
VITE_SUPABASE_URL=your-supabase-url
VITE_SUPABASE_ANON_KEY=your-supabase-anon-key
VITE_API_URL=https://kinemotion-backend-*.us-central1.run.app
\`\`\`

## Deployment

Deployed to Vercel. Push to \`main\` branch triggers automatic deployment.

## Architecture

\`\`\`
User → Frontend (React) → Backend API (FastAPI) → kinemotion CLI → Supabase
\`\`\`

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) in main repository.

## License

MIT - See [LICENSE](../LICENSE) in main repository.
EOF

# Commit initial setup
git add .gitignore README.md
git commit -m "docs: update repository setup for standalone frontend"
git push
```

### 2.2 Update package.json

Update repository URL in `package.json`:

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
    "url": "https://github.com/feniix/kinemotion/issues"
  }
}
```

### 2.3 Set Up GitHub Repository Settings

1. **Branch Protection** (Settings → Branches):
   - Protect `main` branch
   - Require pull request reviews
   - Require status checks (once CI is set up)

2. **Vercel Integration** (Settings → Integrations):
   - Connect Vercel to new repository
   - Configure build settings:
     - Framework: Vite
     - Build Command: `yarn build`
     - Output Directory: `dist`
     - Install Command: `yarn install`

3. **Environment Variables in Vercel**:
   - `VITE_SUPABASE_URL`
   - `VITE_SUPABASE_ANON_KEY`
   - `VITE_API_URL`

## Phase 3: Clean Up Main Repository

### 3.1 Remove frontend/ Directory

```bash
cd /path/to/kinemotion  # Main repository

# Create a new branch for the cleanup
git checkout -b chore/remove-frontend-directory

# Remove frontend directory
git rm -r frontend/

# Commit
git commit -m "chore: move frontend to separate repository

Frontend has been extracted to:
https://github.com/feniix/kinemotion-frontend

This commit removes the frontend/ directory from the main repository
as it now lives independently."

# Push and create PR
git push -u origin chore/remove-frontend-directory
```

### 3.2 Update Documentation

**CLAUDE.md** - Update architecture section:

```markdown
## Architecture

### Full-Stack Architecture

The project has evolved into a complete platform with three repositories:

**Repositories:**
- **kinemotion** (this repo): CLI analysis engine (v0.34.0)
- **kinemotion-frontend**: React app on Vercel (v0.1.0) - [Repository](https://github.com/feniix/kinemotion-frontend)
- **Backend**: Lives in backend/ directory of this repo (v0.1.0)

\`\`\`text
.
├── backend/              # FastAPI server (Cloud Run) - v0.1.0
│   ├── src/              # Python API endpoints
│   ├── Dockerfile        # Container configuration
│   └── pyproject.toml    # FastAPI, Supabase, structlog
├── src/kinemotion/       # CLI analysis engine - v0.34.0
│   ├── cli.py           # Main CLI commands
│   ├── api.py           # Python API (used by backend)
│   └── [modules]        # Core, dropjump, cmj
└── tests/               # 261 comprehensive tests (74.27% coverage)
\`\`\`

**Data Flow:**
\`\`\`
User uploads video → Frontend (React) → Backend API (FastAPI) → kinemotion CLI → Results stored in Supabase → Frontend displays results
\`\`\`

**Deployment:**
- Frontend: Vercel (auto-deploy from kinemotion-frontend repo)
- Backend: Google Cloud Run (GitHub Actions, Workload Identity Federation)
- CLI: PyPI (v0.34.0, standalone usage + backend integration)
```

**README.md** - Update links:

```markdown
## Related Repositories

- **Frontend**: [kinemotion-frontend](https://github.com/feniix/kinemotion-frontend) - React UI
- **Backend**: Lives in `backend/` directory of this repository
```

### 3.3 Update .gitignore

Remove frontend-specific entries:

```bash
# Remove these lines from .gitignore:
# frontend/.pnp.cjs
# frontend/.pnp.loader.mjs
# frontend/.yarn/install-state.gz
# frontend/.yarn/cache/
# !frontend/package.json
```

### 3.4 Update .pre-commit-config.yaml

Remove frontend exclusions:

```yaml
# Remove or update these exclude patterns:
# - repo: ...
#   hooks:
#     - id: check-yaml
#       exclude: 'frontend/.yarn/releases/yarn-.*\.cjs$'  # REMOVE THIS
```

### 3.5 Update .github/workflows/release.yml

Remove frontend path from exclusions:

```yaml
# In .github/workflows/release.yml
on:
  push:
    branches: [main]
    paths-ignore:
      - 'docs/**'
      - 'backend/**'
      # - 'frontend/**'  # REMOVE THIS LINE
      - '*.md'
      # ...
```

### 3.6 Update Serena Memories

```bash
# Update .serena/memories/current-project-architecture.md
# Update .serena/memories/project_overview.md
# Reflect that frontend is now in separate repository
```

### 3.7 Update Basic-Memory Notes

Update these notes:
- `.basic-memory/project-management/project-state-summary-december-2025.md`
- `.basic-memory/codebase/codebase-architecture-overview.md`

### 3.8 Update .claude/agents/frontend-developer.md

Update the agent description to reference the new repository:

```markdown
## Context

The frontend lives in a separate repository:
https://github.com/feniix/kinemotion-frontend

When working on frontend issues, you should:
1. Work in the kinemotion-frontend repository
2. Reference backend API contracts from the main kinemotion repository
3. ...
```

## Phase 4: Update Vercel Configuration

### 4.1 Reconnect Vercel to New Repository

1. **In Vercel Dashboard**:
   - Go to kinemotion project settings
   - Disconnect current GitHub connection
   - Connect to new `kinemotion-frontend` repository
   - Verify build settings:
     - Root Directory: `.` (since frontend is now at root)
     - Build Command: `yarn build`
     - Output Directory: `dist`

2. **Update Environment Variables** (if needed):
   - Ensure all environment variables are set
   - Test deployment

3. **Test Deployment**:
   - Trigger a manual deploy
   - Verify site works: https://kinemotion.vercel.app

### 4.2 Update vercel.json (if needed)

Since frontend is now at root, `vercel.json` should work as-is. Verify:

```json
{
  "buildCommand": "yarn build",
  "installCommand": "yarn install",
  "outputDirectory": "dist"
}
```

## Phase 5: Optional - Set Up Frontend CI/CD

### 5.1 Create .github/workflows/ci.yml in frontend repo

```yaml
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
```

## Phase 6: Communication and Rollout

### 6.1 Communication Checklist

- [ ] Notify team of repository split
- [ ] Update issue references (close old frontend issues, move to new repo)
- [ ] Update project boards/milestones
- [ ] Update README in both repositories with links
- [ ] Update CONTRIBUTING.md

### 6.2 Post-Migration Verification

**Main Repository:**
- [ ] `frontend/` directory removed
- [ ] Documentation updated (CLAUDE.md, README.md, etc.)
- [ ] CI/CD workflows updated
- [ ] .gitignore cleaned up
- [ ] All tests pass: `uv run pytest`
- [ ] Backend deployment still works

**Frontend Repository:**
- [ ] Git history preserved (check `git log`)
- [ ] All files present
- [ ] Dependencies install: `yarn install`
- [ ] Dev server works: `yarn dev`
- [ ] Build succeeds: `yarn build`
- [ ] Type check passes: `yarn type-check`
- [ ] Vercel deployment works
- [ ] Environment variables configured

**Integration:**
- [ ] Frontend can call backend API
- [ ] Authentication works end-to-end
- [ ] CORS configured correctly

## Rollback Plan

If issues arise, you can rollback:

1. **Revert PR in main repo** that removed frontend/
2. **Delete or archive new frontend repository**
3. **Disconnect Vercel from new repository**
4. **Reconnect Vercel to main repository**
5. **Investigate issues before re-attempting**

## Timeline Estimate

| Phase | Duration | Notes |
|-------|----------|-------|
| Phase 1: Extract | 30 min | Git history extraction |
| Phase 2: Setup new repo | 1 hour | Repository configuration |
| Phase 3: Clean up main | 1 hour | Documentation updates |
| Phase 4: Vercel config | 30 min | Reconnect and test |
| Phase 5: CI/CD setup | 1 hour | Optional but recommended |
| Phase 6: Verification | 1 hour | Testing and validation |
| **Total** | **4-5 hours** | Can be done in stages |

## Benefits of Split

✅ **Pros:**
- Independent versioning and releases
- Clearer ownership boundaries
- Faster CI/CD (frontend doesn't wait for backend tests)
- Simpler repository structure
- Easier for frontend-only contributors
- Independent deployment pipelines

⚠️ **Cons:**
- Two repositories to manage
- Cross-repo communication needed for breaking changes
- More complex for full-stack changes
- Need to sync documentation

## Alternative: Keep Monorepo

If you decide NOT to split:

**Consider instead:**
- Keep current structure but add frontend CI/CD workflow
- Use GitHub CODEOWNERS for clear ownership
- Use path-based triggering in CI/CD (already implemented)
- This is simpler for small teams

## Key Files Affected

### Main Repository (kinemotion)
- `CLAUDE.md` - Architecture documentation
- `README.md` - Links and overview
- `.gitignore` - Remove frontend entries
- `.pre-commit-config.yaml` - Remove frontend exclusions
- `.github/workflows/release.yml` - Remove frontend path
- `.serena/memories/*.md` - Update architecture references
- `.basic-memory/**/*.md` - Update project state
- `.claude/agents/frontend-developer.md` - Update context

### New Frontend Repository
- `README.md` - New standalone docs
- `.gitignore` - Frontend-specific
- `package.json` - Update repository URL
- `.github/workflows/ci.yml` - New CI/CD (optional)
- Vercel configuration

## References

- [Git Subtree Documentation](https://git-scm.com/book/en/v2/Git-Tools-Advanced-Merging)
- [git-filter-repo](https://github.com/newren/git-filter-repo)
- [Vercel Monorepo](https://vercel.com/docs/concepts/git/monorepos)
- [GitHub Repository Split Best Practices](https://docs.github.com/en/repositories)

---

**Status**: Planning document - Ready to execute
**Next Step**: Decision point - confirm split is desired, then execute Phase 1
