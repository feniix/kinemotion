## Current Project Architecture - December 2025

### Stack
- **Frontend**: React (v0.1.0) on Vercel - TypeScript
- **Backend**: FastAPI (v0.1.0) on Cloud Run - Python 3.12
- **Analysis Engine**: kinemotion CLI (v0.34.0) - Python
- **Database/Auth**: Supabase (PostgreSQL + Auth)
- **Infrastructure**: GCP (Cloud Run, Secret Manager, Container Registry)

### Directory Structure
```
.
├── frontend/              # React app (Vercel)
│   ├── src/
│   ├── package.json
│   └── ... (TypeScript/React setup)
├── backend/              # FastAPI server (Cloud Run)
│   ├── app/
│   ├── pyproject.toml
│   ├── Dockerfile
│   └── ... (Python/FastAPI setup)
├── src/kinemotion/       # CLI analysis engine (v0.34.0)
│   ├── cli.py
│   ├── api.py
│   ├── core/             # Shared: pose, smoothing, filtering
│   ├── dropjump/         # Drop jump analysis
│   └── cmj/              # CMJ analysis
├── tests/                # 261 tests, 74% coverage
├── scripts/              # Setup scripts
│   ├── setup-github-deploy.sh      # GitHub Actions + Cloud Run setup
│   ├── setup-google-oauth.sh       # Google OAuth setup
│   └── ... (other setup scripts)
└── .github/workflows/    # CI/CD
    ├── deploy-backend.yml          # Backend deployment
    ├── test.yml                    # CLI tests + SonarQube
    └── ... (other workflows)
```

### Deployment Flow
```
GitHub Push (main) → GitHub Actions Workflow
  ├── [backend/**] → Build Docker → Push to GCR → Deploy to Cloud Run
  ├── [frontend/**] → Manual deploy via Vercel dashboard (no auto-workflow)
  └── [src/kinemotion/**] → Run CLI tests → Publish to PyPI (release only)
```

### Service Accounts & Security
- **github-actions-deploy**: CI/CD only (deploys to Cloud Run, builds Docker)
  - NO secret access (least privilege)
- **kinemotion-backend-runtime**: Cloud Run runtime
  - Access to: SUPABASE_URL, SUPABASE_ANON_KEY (per-secret binding)
- Authentication: Workload Identity Federation (OIDC, no service account keys)

### Key Files to Know
- `.github/workflows/deploy-backend.yml` - Backend deployment
- `backend/Dockerfile` - Container image definition
- `scripts/setup-github-deploy.sh` - Initializes GitHub Actions + Cloud Run
- `src/kinemotion/api.py` - Python API (called by backend)
- `frontend/src/` - React components

### Configuration
- GCP Project: kinemotion-backend (us-central1)
- Supabase: Project ID from environment
- Vercel: Connected to GitHub (auto-deploys on push to frontend/)
- Secrets: SUPABASE_URL, SUPABASE_ANON_KEY (managed in Secret Manager)

### Recent Security Update (Dec 2, 2025)
- Implemented least-privilege service account separation
- Removed default compute account from secrets
- Created dedicated runtime account for Cloud Run
- Per-secret IAM bindings (not project-wide)
- See: deployment/cloud-run-least-privilege-service-accounts

### Integration Points
1. Frontend (React) → Backend API (FastAPI) → kinemotion CLI
2. Frontend uploads video to backend → backend processes with CLI → results stored in Supabase
3. Auth: Supabase handles both frontend login and backend API auth

### Testing
- CLI: 261 tests, 74% coverage (run with `uv run pytest`)
- Backend: Tests exist in backend/ (need assessment)
- Frontend: Tests exist in frontend/ (need assessment)
- CI: Runs on every push + PR

### Known Gaps
- Frontend deployment not automated (Vercel manual)
- Backend API endpoints not fully integrated with frontend
- End-to-end tests missing
- Real-time analysis not implemented (MVP scope)

### To Get Up to Speed
1. Read: `.basic-memory/project-management/project-state-summary-december-2025`
2. Check: `.github/workflows/deploy-backend.yml` for deployment logic
3. Review: `scripts/setup-github-deploy.sh` for infrastructure setup
4. Understand: Least-privilege service accounts (deployment/cloud-run-least-privilege-service-accounts)
