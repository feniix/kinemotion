---
title: Production Deployment Guide - Vercel + Google Cloud Run
type: note
permalink: deployment/production-deployment-guide-vercel-google-cloud-run-1
tags:
- deployment
- vercel
- google-cloud-run
- production
- cors
- troubleshooting
---

# Production Deployment Guide - Vercel + Google Cloud Run

## Current Production Setup

**Frontend:** https://kinemotion.vercel.app/ (Vercel)
**Backend:** https://kinemotion-backend-1008251132682.us-central1.run.app (Google Cloud Run)

## Architecture

```
User Browser
    ↓
Vercel (Static React App)
    ↓ POST /api/analyze
Google Cloud Run (FastAPI Backend)
    ↓
MediaPipe Video Analysis
```

---

## Backend Deployment (Google Cloud Run)

### Prerequisites
- Google Cloud CLI installed: `gcloud --version`
- Authenticated: `gcloud auth login`
- Project set: `gcloud config set project kinemotion-backend`

### Initial Deployment

```bash
cd backend

# Deploy with source (builds Docker automatically)
gcloud run deploy kinemotion-backend \
  --source . \
  --region us-central1 \
  --memory 2Gi \
  --set-env-vars CORS_ORIGINS=https://kinemotion.vercel.app \
  --allow-unauthenticated
```

**Key Configuration:**
- **Memory:** 2Gi (MediaPipe requires 1.5GB+, 512MB default causes OOM crashes)
- **Region:** us-central1 (Tier 1 pricing)
- **CORS_ORIGINS:** Comma-separated frontend URLs (no spaces!)
- **Timeout:** Default 300s (sufficient for video processing)

### Updating Configuration

**Add environment variables** (when commas cause parsing issues):

```bash
# Create env.yaml file
cat > env.yaml <<EOF
CORS_ORIGINS: "https://kinemotion.vercel.app,https://other-domain.com"
EOF

# Deploy with env file
gcloud run deploy kinemotion-backend \
  --source . \
  --region us-central1 \
  --env-vars-file env.yaml
```

**Update memory only:**

```bash
gcloud run services update kinemotion-backend \
  --region us-central1 \
  --memory 2Gi
```

### Verify Deployment

```bash
# Check service status
gcloud run services describe kinemotion-backend \
  --region us-central1 \
  --format='value(status.url)'

# Test health endpoint
curl https://kinemotion-backend-1008251132682.us-central1.run.app/health

# Check environment variables
gcloud run services describe kinemotion-backend \
  --region us-central1 \
  --format=yaml | grep -A5 "env:"
```

### View Logs

```bash
# Real-time logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=kinemotion-backend" \
  --limit 50 \
  --format json \
  --freshness=5m

# Or use Cloud Console
# Cloud Run > kinemotion-backend > Logs tab
```

---

## Frontend Deployment (Vercel)

### Prerequisites
- Vercel CLI installed: `npm i -g vercel`
- Authenticated: `vercel login`
- GitHub repo connected to Vercel

### Initial Setup (One-Time)

**Option 1: Vercel Dashboard (Recommended)**

1. Go to https://vercel.com/new
2. Import GitHub repo: `feniix/kinemotion`
3. Configure project:
   - **Project Name:** `kinemotion`
   - **Framework:** Vite (auto-detected)
   - **Root Directory:** `frontend`
   - **Build Command:** `yarn build` (auto-detected)
   - **Output Directory:** `dist` (auto-detected)
4. Add environment variable:
   - **Key:** `VITE_API_URL`
   - **Value:** `https://kinemotion-backend-1008251132682.us-central1.run.app`
   - **Environments:** Production
5. Click **Deploy**

**Option 2: Vercel CLI**

```bash
cd frontend

# Deploy to production with environment variable
vercel --prod -e VITE_API_URL=https://kinemotion-backend-1008251132682.us-central1.run.app
```

**Note:** The `-e` flag sets the env var for that deployment only. For persistent env vars, use the Dashboard or:

```bash
# Add environment variable (will prompt for value)
vercel env add VITE_API_URL production

# Then redeploy
vercel --prod
```

### Redeploy After Code Changes

```bash
# From repository root
git push origin main

# Vercel auto-deploys on push (if GitHub integration is set up)
```

Or manual CLI deployment:

```bash
cd frontend
vercel --prod
```

### Set Custom Domain

**In Vercel Dashboard:**
1. Project → Settings → Domains
2. Add: `kinemotion.vercel.app`
3. Vercel automatically configures DNS

### Verify Deployment

```bash
# Check if backend URL is embedded in JS bundle
curl -s https://kinemotion.vercel.app/ | grep -o 'kinemotion-backend'

# List recent deployments
vercel ls

# Check environment variables
vercel env ls
```

### Disable Deployment Protection (for public access)

1. Vercel Dashboard → Project → Settings → Deployment Protection
2. Set to **"Preview Only"** (production is public)
3. Or turn OFF "Vercel Authentication"

---

## Common Issues & Solutions

### Issue 1: CORS Error + 503 Status

**Symptom:**
```
Access to XMLHttpRequest blocked by CORS policy:
No 'Access-Control-Allow-Origin' header present
Status: 503
```

**Cause:** Cloud Run container ran out of memory (512MB default)

**Solution:**
```bash
gcloud run services update kinemotion-backend \
  --region us-central1 \
  --memory 2Gi
```

**Why it happens:** MediaPipe loads ML models (~500MB) + video processing → OOM. Cloud Run kills the container before CORS middleware can respond, returning a plain 503 without CORS headers.

### Issue 2: 404 Not Found on /api/analyze

**Symptom:**
```
POST https://backend.run.app/analyze → 404
```

**Cause:** Frontend calling `/analyze` instead of `/api/analyze`

**Solution:** Check `frontend/src/hooks/useAnalysis.ts:53`:
```typescript
const apiEndpoint = baseApiUrl ? `${baseApiUrl}/api/analyze` : '/api/analyze'
//                                                    ^^^^^ Must include /api prefix
```

### Issue 3: Environment Variable Not Embedded in Build

**Symptom:** `VITE_API_URL` is set in Vercel but frontend still calls relative `/api/analyze`

**Cause:** Vite embeds env vars at **build time**. If you add env var AFTER deployment, it won't be in the build.

**Solution:**
1. Add `VITE_API_URL` in Vercel Dashboard → Settings → Environment Variables
2. **Redeploy** (must rebuild to embed the variable)
3. Verify: Check browser DevTools → Network tab → see full backend URL in request

### Issue 4: CORS Middleware Not Running

**Symptom:** CORS works for OPTIONS but not POST requests

**Cause:** FastAPI middleware is LIFO (Last In, First Out). If CORS is added after rate limiter, rate limit exceptions bypass CORS.

**Solution:** In `backend/src/kinemotion_backend/app.py`, add CORS middleware **immediately after app creation**, before rate limiter:

```python
app = FastAPI(...)

# Add CORS FIRST (runs last in LIFO order, wraps everything)
app.add_middleware(CORSMiddleware, ...)

# Then configure rate limiter
limiter = Limiter(...)
```

---

## Monitoring & Cost Tracking

### Check Cloud Run Costs

```bash
# View billing for current month
gcloud billing accounts list
gcloud billing projects describe PROJECT_ID
```

**Or Cloud Console:**
- Navigation Menu → Billing → Reports
- Filter by Cloud Run service

### Monitor Resource Usage

```bash
# Check memory usage in logs
gcloud logging read "resource.type=cloud_run_revision AND textPayload=~'Memory'" \
  --limit 20 \
  --format json

# Check container crashes
gcloud logging read "resource.type=cloud_run_revision AND textPayload=~'terminated'" \
  --limit 10
```

**Expected memory usage:**
- Idle: ~100MB (Python + dependencies)
- Processing video: ~500-800MB (MediaPipe models loaded)
- Peak: ~1.2GB (large videos with high resolution)

**With 2GB memory:** Headroom for concurrent requests + safety margin

---

## Deployment Checklist

### Before First Deploy

- [ ] Backend: Dockerfile builds locally
- [ ] Backend: Tests pass (`uv run pytest`)
- [ ] Frontend: Builds locally (`yarn build`)
- [ ] Frontend: Environment variables defined in `.env.example`
- [ ] CORS origins list includes production frontend URL

### Deploying Backend

- [ ] Deploy to Cloud Run with 2Gi memory
- [ ] Set CORS_ORIGINS environment variable
- [ ] Test `/health` endpoint responds
- [ ] Test CORS preflight: `curl -X OPTIONS ... -H "Origin: ..."`
- [ ] Check logs for memory warnings

### Deploying Frontend

- [ ] Set `VITE_API_URL` in Vercel project settings
- [ ] Deploy to Vercel (auto or manual)
- [ ] Verify backend URL is in JavaScript bundle
- [ ] Test in browser: upload a video end-to-end
- [ ] Check Network tab: no CORS errors, 200 response

### Post-Deployment

- [ ] Monitor Cloud Run logs for OOM errors
- [ ] Track API request volume
- [ ] Set up billing alerts (if usage exceeds free tier)
- [ ] Document any custom domains or SSL certificates

---

## Quick Reference Commands

```bash
# Backend: Deploy with all settings
gcloud run deploy kinemotion-backend \
  --source . \
  --region us-central1 \
  --memory 2Gi \
  --env-vars-file env.yaml \
  --quiet

# Frontend: Deploy to production
cd frontend && vercel --prod

# Check Cloud Run logs (last 5 minutes)
gcloud logging read "resource.labels.service_name=kinemotion-backend" \
  --limit 50 \
  --freshness=5m

# Test CORS from command line
curl -X OPTIONS https://backend-url/api/analyze \
  -H "Origin: https://kinemotion.vercel.app" \
  -H "Access-Control-Request-Method: POST" \
  -v

# Check Vercel environment variables
vercel env ls
```

---

## Cost Optimization Tips

1. **Use request-based CPU allocation** (default) - only pay when processing
2. **Set min instances to 0** - no idle costs
3. **Set max instances to 10** - prevent runaway costs from traffic spikes
4. **Monitor GiB-seconds usage** - largest cost factor for video processing
5. **Consider batch processing** - process multiple videos in one container lifecycle

**Estimated costs (100 videos/day, 30 sec each):**
- Free tier covers: ~120 videos/day
- Overage: ~$4-5/month for the extra videos
- Total: Essentially free for MVP usage

---

## Related Documentation

- [Deployment Decision Analysis](memory://strategy/deployment-decision-analysis-for-kinemotion)
- [Vercel Monorepo Best Practice](memory://deployment/vercel-monorepo-deployment-best-practice)
- [Google Cloud Run Pricing](https://cloud.google.com/run/pricing)
- [Vercel Environment Variables](https://vercel.com/docs/concepts/projects/environment-variables)
