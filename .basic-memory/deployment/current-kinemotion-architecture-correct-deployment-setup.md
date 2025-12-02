---
title: Current Kinemotion Architecture - Correct Deployment Setup
type: note
permalink: deployment/current-kinemotion-architecture-correct-deployment-setup-1
---

# Current Kinemotion Architecture - Correct Deployment Setup

## Production Architecture (December 2025)

### Frontend
- **Platform:** Vercel
- **URL:** https://kinemotion.vercel.app
- **Framework:** React + Vite + TypeScript
- **Auto-deploy:** GitHub integration (push to `main` triggers deploy)

### Backend
- **Platform:** Google Cloud Run (NOT Fly.io)
- **URL:** https://kinemotion-backend-1008251132682.us-central1.run.app
- **Framework:** FastAPI + Python 3.12
- **Region:** us-central1
- **Memory:** 2Gi
- **Access:** Public (--allow-unauthenticated)
- **Auto-deploy:** GitHub Actions workflow on push to `main`

### Deployment Flow
```
GitHub Push (main branch)
    ↓
GitHub Actions (.github/workflows/deploy-backend.yml)
    ↓
1. Run tests (pytest, pyright, ruff)
2. Build Docker image → Push to GCR
3. Deploy to Cloud Run with 2Gi memory
4. Health check verification
    ↓
Backend deployed at Cloud Run URL
```

### Authentication Configuration
- **Workload Identity Federation** (keyless auth)
- Service Account: `github-actions-deploy@kinemotion-backend.iam.gserviceaccount.com`
- No static credentials stored

### CORS Configuration
Backend allows frontend origin via environment variable:
```
CORS_ORIGINS=https://kinemotion.vercel.app
```

## Important Note
**The fly.toml file exists but is NOT used.** The actual deployment is on Google Cloud Run, not Fly.io.

## Vercel Authentication Status

### Current User Authentication
**Status:** ❌ No user authentication system exists

### What IS Configured
- Vercel Deployment Protection (optional) - protects preview deployments
- Referer validation in backend - checks requests come from allowed origins
- Test password bypass for debugging

### What Is NOT Available
- No user accounts
- No user IDs
- No authentication tokens from Vercel to backend
- Vercel Deployment Protection does NOT expose user identity to backend

### Options for Adding User Authentication

Since backend runs on **Google Cloud Run** (not Fly.io), all authentication options are available:

#### Option A: Sign in with Vercel (OAuth)
- ✅ Works with Cloud Run backend
- ✅ Vercel users only
- Setup: OAuth app in Vercel dashboard

#### Option B: Third-Party Auth (Clerk, Auth0, Supabase)
- ✅ Works with Cloud Run backend
- ✅ Full user management
- Setup: Install SDK, configure provider

#### Option C: Custom JWT Auth
- ✅ Works with Cloud Run backend
- ✅ Full control
- Setup: Implement token generation/validation

**All options work identically regardless of where backend is hosted.**

## Cost Analysis (MVP)
- Cloud Run: ~$0-5/month (100 videos/day)
- Vercel: Free (frontend hosting)
- GitHub Actions: Free (2000 min/month)

**Total: ~$0-5/month**

## Related Documentation
- GitHub Workflow: `.github/workflows/deploy-backend.yml`
- Service Setup: `scripts/setup-github-deploy.sh`
- Deployment Guide: `.basic-memory/deployment/production-deployment-guide-vercel-google-cloud-run.md`
- Quick Commands: `.basic-memory/deployment/quick-deployment-commands-vercel-and-cloud-run.md`
