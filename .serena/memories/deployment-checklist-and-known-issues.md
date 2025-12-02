## Deployment Checklist & Known Issues

### Pre-Deployment Checklist
- [ ] Run tests: `uv run pytest` (CLI should have 74% coverage)
- [ ] Type check: `uv run pyright` (should be 0 errors)
- [ ] Lint: `uv run ruff check --fix`
- [ ] Backend tests pass (if backend code changed)
- [ ] Verify Cloud Run service account has secrets access
- [ ] Verify Supabase credentials set in Secret Manager
- [ ] Verify frontend environment variables correct

### Deployment Steps

**Backend Deployment (Automatic)**
1. Push to main with changes in `backend/`, `src/kinemotion/`, or `.github/workflows/deploy-backend.yml`
2. GitHub Actions triggers → runs tests → builds Docker → deploys to Cloud Run
3. Health check: `curl https://kinemotion-backend-1008251132682.us-central1.run.app/health`

**Frontend Deployment (Manual)**
1. Push to main with changes in `frontend/`
2. Go to Vercel dashboard → trigger manual deploy
3. Or connect Vercel to GitHub for auto-deploy

**CLI Release (Manual)**
1. Bump version in `src/kinemotion/__init__.py` or `pyproject.toml`
2. Create GitHub release
3. Automated release workflow publishes to PyPI

### Known Issues

#### ✅ FIXED (Dec 2, 2025)
- **Cloud Run Secret Access**: Default compute service account couldn't access secrets
  - Fix: Created dedicated runtime service account with per-secret access
  - Status: ✅ Deployed and tested

#### ⏳ OPEN
- **Frontend → Backend Integration**: Video upload pipeline not fully tested
  - Impact: Cannot upload videos from UI yet
  - Owner: Need end-to-end test

- **Frontend Deployment Automation**: Manual Vercel deploys
  - Impact: Frontend deploys slower than backend
  - Effort: Create GitHub Actions workflow for Vercel
  - Blocker: None (low priority MVP task)

- **API Documentation**: Backend endpoints not documented
  - Impact: Frontend devs unsure what endpoints exist
  - Solution: Add OpenAPI/Swagger docs to FastAPI

- **Error Handling**: Inconsistent error messages
  - Impact: Poor UX when things break
  - Solution: Standardize error responses across stack

#### ℹ️ EXPECTED LIMITATIONS
- Real-time analysis not supported (Phase 2 feature)
- Batch processing only via CLI, not web UI
- Video size limits (Cloud Run memory limits)
- Single user (no multi-tenant yet)

### Rollback Procedures

**Backend Rollback**
1. Revert commit that broke deployment
2. Push to main - GitHub Actions auto-redeploys previous version
3. Or manually redeploy via `gcloud run deploy` with old image

**Frontend Rollback**
1. Vercel dashboard → deployments → select previous and promote
2. Or revert in GitHub and redeploy manually

### Monitoring & Health Checks

- Backend health: `https://kinemotion-backend-1008251132682.us-central1.run.app/health`
- Frontend status: Check Vercel dashboard
- Logs:
  - Backend: GCP Cloud Run console
  - Frontend: Vercel dashboard
- Errors: Set up alerts in Vercel + GCP console

### Service Account Cleanup (if needed)
```bash
# View all service accounts
gcloud iam service-accounts list --project=kinemotion-backend

# View permissions for deployment account
gcloud projects get-iam-policy kinemotion-backend \
  --flatten="bindings[].members" \
  --filter="bindings.members:github-actions-deploy*"

# View runtime account secret access
gcloud secrets get-iam-policy SUPABASE_URL --project=kinemotion-backend
gcloud secrets get-iam-policy SUPABASE_ANON_KEY --project=kinemotion-backend
```

### Disaster Recovery

**If backend stops responding:**
1. Check Cloud Run logs: GCP Console → Cloud Run → kinemotion-backend → Logs
2. Check recent deploys: GitHub Actions page
3. If deployment failed, check pre-deployment checklist
4. Last-resort rollback: Manually deploy previous working commit

**If Supabase connection fails:**
1. Verify secrets in GCP Secret Manager are correct
2. Verify Supabase project is running
3. Check Supabase connection string format
4. Verify runtime service account has secret access

**If frontend can't reach backend:**
1. Verify backend is running: curl health check URL
2. Verify CORS settings in FastAPI
3. Check frontend environment variables (API URL correct?)
4. Check browser console for specific error

### Performance Baselines (for regression detection)
- Backend cold start: ~5-10s
- Video analysis: Depends on video length
- Frontend load: <2s initial page load

### Testing Endpoints

**Backend**
- Health: GET `https://kinemotion-backend-1008251132682.us-central1.run.app/health`
- API docs: GET `https://kinemotion-backend-1008251132682.us-central1.run.app/docs` (if Swagger enabled)

**Frontend**
- URL: `https://kinemotion.vercel.app`
- Auth flow: Try Google OAuth or email login

### Secrets Management
- Location: GCP Secret Manager (kinemotion-backend project)
- Access: Via Cloud Run service accounts only
- Rotation: Manual (update in Secret Manager, redeploy Cloud Run)
- Backup: Stored in Supabase dashboard (do NOT commit to git)

---
**Last Updated**: 2025-12-02
**Maintained By**: DevOps/Platform team
