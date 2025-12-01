---
title: Automated Deployment Setup - GitHub Actions with Workload Identity Federation
type: note
permalink: deployment/automated-deployment-setup-git-hub-actions-with-workload-identity-federation-1
tags:
- ci-cd
- github-actions
- workload-identity
- automation
- deployment
---

# Automated Deployment Setup - GitHub Actions with Workload Identity Federation

## Overview

Automated deployment is configured using **Workload Identity Federation** (keyless authentication):
- ✅ No static service account keys
- ✅ Short-lived tokens (auto-expire)
- ✅ Repository-scoped access
- ✅ Complete audit trail

## Current Configuration

**Workflow:** `.github/workflows/deploy-backend.yml`
**Setup Script:** `scripts/setup-github-deploy.sh`

**Workload Identity Provider:**
```
projects/1008251132682/locations/global/workloadIdentityPools/github-pool/providers/github-provider
```

**Service Account:**
```
github-actions-deploy@kinemotion-backend.iam.gserviceaccount.com
```

**Permissions Granted:**
- `roles/run.admin` - Deploy Cloud Run services
- `roles/iam.serviceAccountUser` - Required for Cloud Run
- `roles/storage.admin` - Build and upload containers
- `roles/cloudbuild.builds.editor` - Source-based deployments

## How Auto-Deployment Works

**Trigger:** Push to `main` branch with changes to:
- `backend/**`
- `src/kinemotion/**`
- `.github/workflows/deploy-backend.yml`

**Workflow Steps:**
1. **Test** - Run pytest, pyright, ruff
2. **Build** - Build Docker image, run Trivy security scan
3. **Deploy** - Deploy to Cloud Run with 2Gi memory + CORS env var
4. **Verify** - Health check at `/health` endpoint

**Deployment Command Used:**
```yaml
- uses: google-github-actions/deploy-cloudrun@v2
  with:
    service: kinemotion-backend
    region: us-central1
    source: ./backend
    flags: |
      --memory=2Gi
      --allow-unauthenticated
      --set-env-vars=CORS_ORIGINS=https://kinemotion.vercel.app
```

## Frontend Auto-Deployment

**Already configured!** Vercel has GitHub integration enabled:
- Push to `main` → Vercel automatically builds and deploys
- No additional setup needed
- Environment variable `VITE_API_URL` is set in Vercel project settings

## Testing the Setup

**Manual test:**
```bash
# Make a small change
echo "# Test deployment" >> backend/README.md
git add backend/README.md
git commit -m "test: trigger automated deployment"
git push origin main

# Watch the workflow
open https://github.com/feniix/kinemotion/actions
```

**Expected result:**
- Workflow runs automatically
- Tests pass → Build passes → Deploy succeeds
- New revision deployed to Cloud Run
- Health check passes

## Re-running Setup

The setup script is **idempotent** - safe to run multiple times:

```bash
./scripts/setup-github-deploy.sh
```

**What it does:**
- ✓ Checks if resources exist before creating
- ✓ Enables required APIs
- ✓ Creates workload identity pool + provider
- ✓ Creates service account with all permissions
- ✓ Binds GitHub repo to service account
- ✓ Outputs values for workflow file

**When to re-run:**
- Moving to a new Google Cloud project
- Setting up in a different repository
- Troubleshooting permission issues
- Verifying the configuration

## Security Benefits

**Traditional Approach (insecure):**
```
GitHub Secrets → Static JSON key → Can be stolen, must rotate, never expires
```

**Workload Identity Federation (secure):**
```
GitHub OIDC token → Google verifies repository → Temporary credentials (1 hour) → Auto-expires
```

**Access control:**
- Only `feniix/kinemotion` repository can use this identity
- Repository owner verified: `assertion.repository_owner=='feniix'`
- Tokens expire automatically
- No credentials in repository or secrets

## Monitoring Deployments

**GitHub Actions:**
- https://github.com/feniix/kinemotion/actions
- Shows all workflow runs, logs, and status

**Cloud Run Revisions:**
```bash
# List recent deployments
gcloud run revisions list \
  --service kinemotion-backend \
  --region us-central1 \
  --limit 10

# Check current traffic routing
gcloud run services describe kinemotion-backend \
  --region us-central1 \
  --format='value(status.traffic)'
```

## Rollback Procedure

**If deployment breaks production:**

1. **Check workflow logs:**
   - https://github.com/feniix/kinemotion/actions
   - Click failed workflow → View logs

2. **Rollback to previous revision:**
   ```bash
   # List revisions
   gcloud run revisions list --service kinemotion-backend --region us-central1

   # Route 100% traffic to previous good revision
   gcloud run services update-traffic kinemotion-backend \
     --region us-central1 \
     --to-revisions kinemotion-backend-00013-abc=100
   ```

3. **Or rollback via Console:**
   - Cloud Run → kinemotion-backend → Revisions tab
   - Click previous revision → Manage Traffic → 100%

## Workflow Customization

**Add environment variables:**

Edit `.github/workflows/deploy-backend.yml`:
```yaml
flags: |
  --memory=2Gi
  --allow-unauthenticated
  --set-env-vars=CORS_ORIGINS=https://kinemotion.vercel.app,NEW_VAR=value
```

**Change memory/CPU:**
```yaml
flags: |
  --memory=4Gi
  --cpu=2
```

**Add secrets from GitHub:**
```yaml
flags: |
  --set-env-vars=API_KEY=${{ secrets.API_KEY }}
```

## Troubleshooting

### Workflow fails with "permission denied"

**Check service account has all required roles:**
```bash
gcloud projects get-iam-policy kinemotion-backend \
  --flatten="bindings[].members" \
  --filter="bindings.members:github-actions-deploy@kinemotion-backend.iam.gserviceaccount.com" \
  --format="table(bindings.role)"
```

**Should show:**
- roles/run.admin
- roles/iam.serviceAccountUser
- roles/storage.admin
- roles/cloudbuild.builds.editor

### Workflow fails with "workload identity pool not found"

**Verify pool exists:**
```bash
gcloud iam workload-identity-pools describe github-pool \
  --location="global" \
  --project=kinemotion-backend
```

**If not found, re-run setup script.**

### Deployment succeeds but app doesn't work

**Check Cloud Run logs immediately:**
```bash
gcloud logging read \
  "resource.labels.service_name=kinemotion-backend" \
  --limit 50 \
  --freshness=5m
```

**Common issues:**
- Memory still set to 512Mi (should be 2Gi)
- CORS_ORIGINS not set correctly
- Container crashes on startup

## Cost Impact

**GitHub Actions:**
- Free for public repositories
- 2,000 minutes/month for private repos

**Typical workflow runtime:**
- Tests: ~2 minutes
- Build: ~3 minutes
- Deploy: ~4 minutes
- **Total: ~9 minutes per deployment**

**With 10 deployments/month:** 90 minutes used (well within free tier)

## Related Documentation

- [Production Deployment Guide](memory://deployment/production-deployment-guide-vercel-google-cloud-run)
- [Quick Deployment Commands](memory://deployment/quick-deployment-commands-vercel-and-cloud-run)
- [Backend CORS Configuration](memory://backend-cors-fastapi-middleware-order)
