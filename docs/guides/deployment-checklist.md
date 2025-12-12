# 🚀 Kinemotion MVP - Deployment Checklist

**Status**: Ready for deployment
**Date Prepared**: November 29, 2025
**Cost**: ~$4-5/month (essentially free)
**Timeline**: 3 weeks to coaches

______________________________________________________________________

## What's Been Completed

### ✅ Frontend

- [x] React/TypeScript application built and tested
- [x] Deployed to Vercel (auto-deploys on git push)
- [x] Environment variable support for backend URL (`VITE_API_URL`)
- [x] All UI/UX components (upload, analysis, results display, error handling)
- [x] Mobile responsive testing passed

### ✅ Backend

- [x] FastAPI application with async video processing
- [x] CMJ and Drop Jump analysis endpoints
- [x] Dockerfile optimized for Cloud Run
- [x] Health check endpoint configured
- [x] CORS properly configured
- [x] Error handling and validation implemented
- [x] Rate limiting (3 requests/minute per IP)

### ✅ Deployment Infrastructure

- [x] Dockerfile fixed (Cloud Run optimized)
- [x] Comprehensive deployment guide (docs/guides/cloud-run-deployment.md)
- [x] Quick reference guide (docs/reference/cloud-run-quick-reference.md)
- [x] Decision analysis saved to memory

______________________________________________________________________

## Files Modified/Created

### New Deployment Files

- `docs/guides/cloud-run-deployment.md` - Complete step-by-step deployment guide
- `docs/reference/cloud-run-quick-reference.md` - Quick command reference
- `Dockerfile` - Updated and optimized for Cloud Run

### Key Configuration Files

- `frontend/vite.config.ts` - Proxy and build configuration
- `frontend/.env.example` - Environment variable template
- `backend/src/kinemotion_backend/app.py` - FastAPI application
- `backend/pyproject.toml` - Python dependencies

______________________________________________________________________

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                          Browser                             │
└────────────────┬────────────────────────────────────────────┘
                 │
        ┌────────▼────────┐
        │                 │
        │ Vercel Frontend │
        │ kinemotion-mvp  │
        │  .vercel.app    │
        │                 │
        └────────┬────────┘
                 │
        VITE_API_URL env var
                 │
        ┌────────▼────────────────┐
        │                         │
        │ Google Cloud Run        │
        │ kinemotion-backend      │
        │ (us-central1)           │
        │                         │
        │ FastAPI + Uvicorn       │
        │ Video Analysis Engine   │
        │                         │
        └─────────────────────────┘
```

**Data Flow:**

1. User uploads video to Vercel frontend
1. Frontend calls `VITE_API_URL/api/analyze`
1. Cloud Run receives request, processes video (60-120 seconds)
1. Returns metrics JSON
1. Frontend displays results

______________________________________________________________________

## Environment Configuration

### Required Environment Variables

#### R2 Storage (for video persistence)

```bash
R2_ENDPOINT=https://abc123.r2.cloudflarestorage.com
R2_ACCESS_KEY=your_access_key_from_cloudflare
R2_SECRET_KEY=your_secret_key_from_cloudflare
R2_BUCKET_NAME=kinemotion  # Default bucket name
```

#### Optional R2 URL Strategy

**Public URLs (Recommended for Production):**

```bash
# Use custom domain (requires R2 bucket custom domain setup)
R2_PUBLIC_BASE_URL=https://kinemotion-public.example.com

# Or use R2.dev public URL (simpler, but R2-branded domain)
R2_PUBLIC_BASE_URL=https://kinemotion.abc123.r2.dev
```

**Presigned URLs (Fallback):**

```bash
# If R2_PUBLIC_BASE_URL is not set, presigned URLs are used
# Default expiration: 7 days (604800 seconds)
R2_PRESIGN_EXPIRATION_S=604800  # Optional, defaults to 7 days
```

**Trade-offs:**

- **Public URLs**: Stable, long-lived, better for production (requires bucket to be public or custom domain)
- **Presigned URLs**: Temporary access, expire after N seconds, no custom domain needed

#### CORS Configuration

```bash
CORS_ORIGINS=https://kinemotion-mvp.vercel.app,https://app.example.com
```

______________________________________________________________________

## Deployment Steps (Quick Version)

### Prerequisites

```bash
# Install gcloud CLI
# https://cloud.google.com/sdk/docs/install

# Verify installations
gcloud --version
docker --version
```

### Deploy Backend (5 minutes)

```bash
cd backend

# Set project
export PROJECT_ID="kinemotion-backend"
gcloud config set project $PROJECT_ID

# Build (x86_64 for Cloud Run) and deploy
docker buildx build --platform linux/amd64 -t gcr.io/${PROJECT_ID}/kinemotion-backend:latest . && \
docker push gcr.io/${PROJECT_ID}/kinemotion-backend:latest

gcloud run deploy kinemotion-backend \
  --image gcr.io/${PROJECT_ID}/kinemotion-backend:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --timeout 600 \
  --memory 512Mi \
  --cpu 1 \
  --max-instances 10 \
  --set-env-vars "CORS_ORIGINS=https://kinemotion-mvp.vercel.app" \
  --set-env-vars "WORKERS=1" \
  --set-env-vars "R2_ENDPOINT=https://xxx.r2.cloudflarestorage.com" \
  --set-env-vars "R2_ACCESS_KEY=your_access_key" \
  --set-env-vars "R2_SECRET_KEY=your_secret_key" \
  --set-env-vars "R2_BUCKET_NAME=kinemotion" \
  --set-env-vars "R2_PUBLIC_BASE_URL=https://kinemotion-public.example.com"

# Get URL
BACKEND_URL=$(gcloud run services describe kinemotion-backend \
  --platform managed --region us-central1 --format 'value(status.url)')
echo "Backend URL: $BACKEND_URL"
```

### Deploy Frontend (2 minutes)

1. Go to **Vercel Dashboard** → kinemotion project
1. Settings → Environment Variables
1. Add: `VITE_API_URL` = your backend URL from above
1. Redeploy frontend

```bash
# Or via CLI
cd frontend
npx vercel --prod
```

### Test (2 minutes)

```bash
# Test backend health
curl $BACKEND_URL/health

# Test frontend
# Open: https://kinemotion-mvp.vercel.app
# Upload a video
# Verify analysis results
```

______________________________________________________________________

## Important URLs

| Component            | URL                                                         |
| -------------------- | ----------------------------------------------------------- |
| Frontend (Vercel)    | `https://kinemotion-mvp.vercel.app`                         |
| Backend Health       | `https://kinemotion-backend-xxxxx-uc.a.run.app/health`      |
| API Endpoint         | `https://kinemotion-backend-xxxxx-uc.a.run.app/api/analyze` |
| Cloud Run Console    | `https://console.cloud.google.com/run`                      |
| Vercel Dashboard     | `https://vercel.com/dashboard`                              |
| Google Cloud Console | `https://console.cloud.google.com`                          |

______________________________________________________________________

## Cost Summary

### Pricing Model

- **Requests**: $0.40 per million (2M free/month)
- **vCPU-seconds**: $0.000024 per vCPU-second (180k free/month)
- **Memory**: Included in vCPU-seconds charge
- **Data transfer**: $0.12 per GB after 1GB free

### MVP Usage (100 videos/day, 2 minutes per video)

| Metric    | Monthly | Free Tier | Overage | Cost      |
| --------- | ------- | --------- | ------- | --------- |
| Requests  | 3,000   | 2,000,000 | 0       | $0        |
| vCPU-sec  | 360,000 | 180,000   | 180,000 | $4.32     |
| Data out  | ~1GB    | 1GB       | 0       | $0        |
| **Total** |         |           |         | **~$4-5** |

**If scaled to 1,000 videos/day**: ~$40-50/month
**If scaled to 10,000 videos/day**: ~$400-500/month

______________________________________________________________________

## Monitoring & Maintenance

### View Logs

```bash
# Real-time logs
gcloud run logs read kinemotion-backend --follow

# Last 50 lines
gcloud run logs read kinemotion-backend --limit 50
```

### Monitor Performance

- Cloud Run Console: https://console.cloud.google.com/run/detail/us-central1/kinemotion-backend?tab=metrics
- Check: Request count, latency, errors
- Scale up if: Error rate > 5% or p95 latency > 60s

### Redeploy After Code Changes

```bash
cd backend
docker buildx build --platform linux/amd64 -t gcr.io/${PROJECT_ID}/kinemotion-backend:latest . && \
docker push gcr.io/${PROJECT_ID}/kinemotion-backend:latest && \
gcloud run deploy kinemotion-backend --image gcr.io/${PROJECT_ID}/kinemotion-backend:latest --platform managed --region us-central1
```

______________________________________________________________________

## Next Steps (Post-Deployment)

1. **Test with Coaches** (Week 1-2)

   - Send deployment URL to 5-10 coaches
   - Collect feedback on metrics accuracy
   - Document issues

1. **Monitor Performance** (Week 1-3)

   - Check error logs daily
   - Monitor response times
   - Track cost usage

1. **Iterate Based on Feedback** (Week 2-3)

   - Fix validation issues
   - Improve metric calculations
   - Enhance UI based on feedback

1. **Prepare for Scaling** (Post-MVP)

   - Increase `--max-instances` if needed
   - Add R2 storage for results
   - Implement authentication if required

______________________________________________________________________

## Troubleshooting Quick Links

| Issue                     | Solution                                                          |
| ------------------------- | ----------------------------------------------------------------- |
| Backend not starting      | Check logs: `gcloud run logs read kinemotion-backend --limit 100` |
| CORS errors from frontend | Update `CORS_ORIGINS` env var in Cloud Run                        |
| Video upload timeout      | Increase `--timeout` to 1800 (max 3600)                           |
| High latency              | Increase `--cpu` to 2 and `--memory` to 1Gi                       |
| Out of memory errors      | Increase `--memory` to 1Gi or 2Gi                                 |
| Health check failing      | Verify `$PORT` is 8000 in Dockerfile CMD                          |

______________________________________________________________________

## Documentation References

- **Full Deployment Guide**: `docs/guides/cloud-run-deployment.md`
- **Quick Commands**: `docs/reference/cloud-run-quick-reference.md`
- **Deployment Decision**: Saved in `.basic-memory/strategy/deployment-decision-analysis-for-kinemotion.md`
- **Project README**: `README.md` (project root)
- **API Documentation**: `/backend/README.md`

______________________________________________________________________

## Contact & Support

- **Google Cloud Docs**: https://cloud.google.com/run/docs
- **Vercel Docs**: https://vercel.com/docs
- **Project GitHub**: https://github.com/feniix/kinemotion

______________________________________________________________________

**Ready to deploy!** Start with `docs/guides/cloud-run-deployment.md` or use commands from `docs/reference/cloud-run-quick-reference.md`.
