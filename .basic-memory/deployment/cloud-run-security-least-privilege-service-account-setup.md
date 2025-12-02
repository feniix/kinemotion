---
title: 'Cloud Run Security: Least-Privilege Service Account Setup'
type: note
permalink: deployment/cloud-run-least-privilege-service-accounts-1
tags:
- deployment
- security
- gcp
- cloud-run
- service-accounts
---

# Cloud Run Security: Least-Privilege Service Account Setup

## Overview

Implemented proper separation of concerns for Cloud Run deployment with dedicated service accounts following the principle of least privilege. Each service account has only the minimum permissions required for its specific role.

## Service Accounts

### 1. Deployment Account
- **Name**: `github-actions-deploy@kinemotion-backend.iam.gserviceaccount.com`
- **Purpose**: GitHub Actions CI/CD pipeline
- **Permissions**:
  - `roles/run.admin` - Deploy to Cloud Run
  - `roles/iam.serviceAccountUser` - Use service accounts
  - `roles/storage.admin` - Push Docker images to GCR
  - `roles/cloudbuild.builds.editor` - Cloud Build operations
  - `roles/artifactregistry.reader` - Read from Artifact Registry
  - `roles/serviceusage.serviceUsageConsumer` - Service usage
  - `roles/cloudbuild.builds.builder` - Build container images
- **Secret Access**: ❌ NONE (not needed for deployment)
- **Authentication**: Workload Identity Federation (OIDC)

### 2. Runtime Account
- **Name**: `kinemotion-backend-runtime@kinemotion-backend.iam.gserviceaccount.com`
- **Purpose**: Cloud Run container execution
- **Permissions**:
  - `roles/secretmanager.secretAccessor` (specific secrets only):
    - `SUPABASE_URL`
    - `SUPABASE_ANON_KEY`
- **Secret Access**: ✅ Only required secrets
- **Configured In**: `.github/workflows/deploy-backend.yml` line 135

## Problem Solved

**Initial Issue**: Default Compute Engine service account (`1008251132682-compute@developer.gserviceaccount.com`) had broad access to all secrets via `roles/secretmanager.secretAccessor`. This violated the principle of least privilege.

**Solution**: Created dedicated runtime account with access only to the two required secrets.

## Files Modified

1. **`.github/workflows/deploy-backend.yml`**
   - Added `--service-account=kinemotion-backend-runtime@kinemotion-backend.iam.gserviceaccount.com` to Cloud Run deployment flags (line 135)

2. **`scripts/setup-github-deploy.sh`**
   - Creates `kinemotion-backend-runtime` service account
   - Grants secret access only to `SUPABASE_URL` and `SUPABASE_ANON_KEY` (per-secret binding)
   - Removes overly-broad permissions from default compute account

## Setup Instructions

Run the setup script to initialize the configuration:
```bash
bash scripts/setup-github-deploy.sh
```

The script is idempotent and safe to run multiple times.

## Verification Commands

```bash
# Check runtime account secret access
gcloud secrets get-iam-policy SUPABASE_URL --project=kinemotion-backend
gcloud secrets get-iam-policy SUPABASE_ANON_KEY --project=kinemotion-backend

# View service account permissions
gcloud projects get-iam-policy kinemotion-backend \
  --flatten="bindings[].members" \
  --filter="bindings.members:kinemotion-backend-runtime*" \
  --format=table
```

## Security Benefits

✅ **Least Privilege**: Each account has only required permissions
✅ **Auditability**: Can track which account accessed which secrets
✅ **Isolation**: Compromise of one service doesn't affect others
✅ **Separation of Concerns**: Deployment logic isolated from runtime logic
✅ **Per-Secret Binding**: Secrets accessed at granular level, not project-wide

## Related Issues

- GitHub Actions deployment failing: #[secret-access-error]
- Service account permission denied on secrets

## Commit

- Commit SHA: `2fdfaad`
- Message: `ci: implement least-privilege service account separation for Cloud Run deployment`
