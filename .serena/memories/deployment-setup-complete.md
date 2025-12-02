## Cloud Run Deployment Security - COMPLETED

### Status
✅ Least-privilege service account separation implemented and tested

### Changes Made
1. Created dedicated runtime service account: `kinemotion-backend-runtime@kinemotion-backend.iam.gserviceaccount.com`
2. Granted per-secret access (SUPABASE_URL, SUPABASE_ANON_KEY) to runtime account only
3. Removed overly-broad permissions from default compute service account
4. Updated workflow to use runtime service account
5. Updated setup script to create and configure runtime account

### Files Modified
- `.github/workflows/deploy-backend.yml` - Added service account flag to deploy step
- `scripts/setup-github-deploy.sh` - Creates runtime account and grants secret access

### Security Model
| Account | Role | Secret Access |
|---------|------|---|
| github-actions-deploy | CI/CD Deployment | ❌ None |
| kinemotion-backend-runtime | Cloud Run Runtime | ✅ SUPABASE_URL, SUPABASE_ANON_KEY |
| 1008251132682-compute | Default (Removed) | ❌ None |

### Setup Verification
- Run: `bash scripts/setup-github-deploy.sh`
- Verify: `gcloud secrets get-iam-policy SUPABASE_URL --project=kinemotion-backend`
- Both secrets should show only `kinemotion-backend-runtime` has accessor role

### Next Steps
1. ✅ Commit changes (2fdfaad)
2. ⏳ Push to main
3. ⏳ Run deployment workflow to verify success
4. ✅ Monitor for any permission issues

### Related
- Deployment workflow: `.github/workflows/deploy-backend.yml`
- Setup automation: `scripts/setup-github-deploy.sh`
- Detailed guide: `deployment/cloud-run-least-privilege-service-accounts` (basic-memory)
