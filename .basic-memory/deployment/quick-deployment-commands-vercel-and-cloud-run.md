---
title: Quick Deployment Commands - Vercel and Cloud Run
type: note
permalink: deployment/quick-deployment-commands-vercel-and-cloud-run
tags:
- deployment
- quick-reference
- vercel
- cloud-run
- commands
---

# Quick Deployment Commands - Vercel and Cloud Run

## Production URLs

- **Frontend:** https://kinemotion.vercel.app/
- **Backend:** https://kinemotion-backend-1008251132682.us-central1.run.app/api/analyze
- **Backend Health:** https://kinemotion-backend-1008251132682.us-central1.run.app/health

---

## Deploy Backend (Google Cloud Run)

### Full Deployment

```bash
cd backend

# Option 1: Single env var
gcloud run deploy kinemotion-backend \
  --source . \
  --region us-central1 \
  --memory 2Gi \
  --set-env-vars CORS_ORIGINS=https://kinemotion.vercel.app \
  --quiet

# Option 2: Multiple env vars (use file)
cat > env.yaml <<EOF
CORS_ORIGINS: "https://kinemotion.vercel.app,https://other-domain.com"
R2_ENDPOINT: "https://your-r2-endpoint"
EOF

gcloud run deploy kinemotion-backend \
  --source . \
  --region us-central1 \
  --memory 2Gi \
  --env-vars-file env.yaml \
  --quiet
```

### Update Configuration Only

```bash
# Update memory
gcloud run services update kinemotion-backend \
  --region us-central1 \
  --memory 2Gi

# Update env vars (won't work with commas - use console or redeploy)
# Better: Use Cloud Console → Edit & Deploy New Revision
```

### Check Status

```bash
# Get service URL
gcloud run services describe kinemotion-backend \
  --region us-central1 \
  --format='value(status.url)'

# Check latest revision
gcloud run services describe kinemotion-backend \
  --region us-central1 \
  --format='value(status.latestReadyRevisionName)'

# Test health
curl https://kinemotion-backend-1008251132682.us-central1.run.app/health
```

---

## Deploy Frontend (Vercel)

### First-Time Setup

```bash
cd frontend

# Deploy and follow prompts
vercel --prod

# Link to existing project if needed
vercel link
```

**Then set environment variable in Vercel Dashboard:**
1. Project → Settings → Environment Variables
2. Add: `VITE_API_URL=https://kinemotion-backend-1008251132682.us-central1.run.app`
3. Environment: Production
4. Redeploy

### Redeploy After Changes

```bash
cd frontend
vercel --prod

# Or use GitHub integration (auto-deploys on push to main)
git push origin main
```

### Check Vercel Status

```bash
# List recent deployments
vercel ls

# Check environment variables
vercel env ls

# View specific deployment logs
vercel inspect <deployment-url> --logs
```

---

## Test CORS Configuration

### Test Preflight (OPTIONS)

```bash
curl -v -X OPTIONS https://kinemotion-backend-1008251132682.us-central1.run.app/api/analyze \
  -H "Origin: https://kinemotion.vercel.app" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: content-type" 2>&1 | grep access-control

# Should show:
# access-control-allow-origin: https://kinemotion.vercel.app
# access-control-allow-methods: GET, POST, OPTIONS
# access-control-allow-headers: Accept, Content-Type, ...
```

### Test Actual POST

```bash
curl -X POST https://kinemotion-backend-1008251132682.us-central1.run.app/api/analyze \
  -H "Origin: https://kinemotion.vercel.app" \
  -F "file=@/path/to/video.mp4" \
  -F "jump_type=cmj" \
  -F "quality=balanced"

# Should return: JSON with metrics (200) or validation error (422)
# Should NOT return: 503 or empty response
```

---

## View Logs

### Cloud Run Logs

```bash
# Recent logs (last 5 minutes)
gcloud logging read \
  "resource.labels.service_name=kinemotion-backend" \
  --limit 50 \
  --freshness=5m

# Filter for errors
gcloud logging read \
  "resource.labels.service_name=kinemotion-backend AND severity>=ERROR" \
  --limit 20

# Search for memory issues
gcloud logging read \
  "resource.labels.service_name=kinemotion-backend AND textPayload=~'Memory'" \
  --limit 20
```

**Or use Cloud Console:**
- Cloud Run → kinemotion-backend → Logs tab
- Real-time streaming
- Filter by severity

### Vercel Logs

**Note:** Vercel only shows server-side logs. Frontend is static (no runtime logs).

To see frontend errors:
- Browser DevTools → Console tab (client-side JavaScript errors)
- Network tab (API call failures)

---

## Emergency Rollback

### Cloud Run

```bash
# List revisions
gcloud run revisions list \
  --service kinemotion-backend \
  --region us-central1

# Route 100% traffic to previous revision
gcloud run services update-traffic kinemotion-backend \
  --region us-central1 \
  --to-revisions kinemotion-backend-00012-abc=100
```

### Vercel

```bash
# List deployments
vercel ls

# Promote a previous deployment to production
vercel promote <deployment-url>
```

**Or use Dashboard:**
- Deployments → Click deployment → Promote to Production

---

## Environment Variables

### Required Backend Env Vars

```yaml
# Production
CORS_ORIGINS: "https://kinemotion.vercel.app"

# Optional (for R2 storage)
R2_ENDPOINT: "https://your-account-id.r2.cloudflarestorage.com"
R2_ACCESS_KEY: "your-access-key"
R2_SECRET_KEY: "your-secret-key"
R2_BUCKET_NAME: "kinemotion"
```

### Required Frontend Env Vars

```bash
# Production only (build-time)
VITE_API_URL=https://kinemotion-backend-1008251132682.us-central1.run.app
```

**Note:** Vite env vars are embedded at **build time**. Changes require redeployment.

---

## Troubleshooting Checklist

### CORS Error in Browser

- [ ] Check Cloud Run logs for memory errors
- [ ] Verify CORS_ORIGINS includes frontend URL
- [ ] Test CORS with curl OPTIONS request
- [ ] Check middleware order in app.py (CORS must be first)
- [ ] Hard refresh browser (Cmd+Shift+R)

### 404 Error

- [ ] Check frontend is calling `/api/analyze` (not `/analyze`)
- [ ] Verify VITE_API_URL is set in Vercel
- [ ] Verify Vercel redeployed after env var was added
- [ ] Check Network tab for actual URL being called

### 503 Error

- [ ] Check Cloud Run logs for OOM (Out of Memory)
- [ ] Verify memory is set to 2Gi (not 512Mi)
- [ ] Check for container crashes in logs
- [ ] Verify rate limiter isn't blocking (3 requests/minute limit)

### Environment Variable Not Working

- [ ] Verify env var is set: `vercel env ls` or `gcloud run services describe`
- [ ] For Vite vars: Redeploy after adding (build-time embedding)
- [ ] Check for typos in env var name (VITE_ prefix required)
- [ ] Verify env var is for correct environment (Production vs Preview)

---

## Cost Monitoring

```bash
# View current month billing
gcloud billing accounts list
gcloud beta billing accounts get-iam-policy ACCOUNT_ID

# Set up billing alerts (via Cloud Console)
# Billing → Budgets & Alerts → Create Budget
# Alert threshold: $10/month for MVP
```

**Expected costs (MVP usage):**
- Cloud Run: $0-5/month (free tier + small overage)
- Vercel: $0/month (Hobby tier)
- **Total: ~$0-5/month**

---

## Production Deployment Workflow

**After code changes:**

1. **Commit and push:**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   git push origin main
   ```

2. **Deploy backend:**
   ```bash
   cd backend
   gcloud run deploy kinemotion-backend \
     --source . \
     --region us-central1 \
     --env-vars-file env.yaml \
     --quiet
   ```

3. **Frontend auto-deploys** (if GitHub integration is set up)
   - Or manual: `cd frontend && vercel --prod`

4. **Verify:**
   - Test backend health: `curl .../health`
   - Test frontend: Open https://kinemotion.vercel.app/
   - Upload a video end-to-end

5. **Monitor logs** for first few minutes after deployment

---

## Related Documentation

- [Production Deployment Guide](memory://deployment/production-deployment-guide-vercel-google-cloud-run)
- [CORS and Memory Issues Debugging](memory://deployment/cors-and-memory-issues-production-debugging-guide)
- [Backend CORS Configuration (Serena)](memory://backend-cors-fastapi-middleware-order)
