# Cloud Run Deployment - Quick Reference

## First-Time Setup (One Time)

```bash
# Install gcloud CLI
# https://cloud.google.com/sdk/docs/install

# Set project ID
export PROJECT_ID="kinemotion-backend"

# Create Google Cloud project
gcloud projects create $PROJECT_ID --name="Kinemotion Backend"
gcloud config set project $PROJECT_ID

# Enable APIs
gcloud services enable run.googleapis.com containerregistry.googleapis.com cloudbuild.googleapis.com

# Configure Docker
gcloud auth configure-docker gcr.io
```

## Build and Deploy (One Command)

From `/backend` directory:

```bash
PROJECT_ID=$(gcloud config get-value project)

# Build (x86_64 for Cloud Run), push, and deploy
docker buildx build --platform linux/amd64 -t gcr.io/${PROJECT_ID}/kinemotion-backend:latest . && \
docker push gcr.io/${PROJECT_ID}/kinemotion-backend:latest && \
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
  --set-env-vars "WORKERS=1"
```

## Get Backend URL

```bash
gcloud run services describe kinemotion-backend \
  --platform managed \
  --region us-central1 \
  --format 'value(status.url)'
```

## Test Backend

```bash
# Set URL variable
BACKEND_URL=$(gcloud run services describe kinemotion-backend \
  --platform managed --region us-central1 --format 'value(status.url)')

# Test health check
curl $BACKEND_URL/health
```

## View Logs

```bash
# Real-time logs
gcloud run logs read kinemotion-backend --follow

# Last 50 lines
gcloud run logs read kinemotion-backend --limit 50
```

## Update Frontend Environment Variable

**In Vercel Dashboard:**

1. Go to Settings → Environment Variables
1. Add/update `VITE_API_URL` with your Cloud Run URL
1. Redeploy frontend

**Or via CLI:**

```bash
cd frontend
npx vercel env add VITE_API_URL
# Enter: https://kinemotion-backend-xxxxx-uc.a.run.app
npx vercel --prod
```

## Redeploy After Code Changes

```bash
cd backend
docker buildx build --platform linux/amd64 -t gcr.io/${PROJECT_ID}/kinemotion-backend:latest . && \
docker push gcr.io/${PROJECT_ID}/kinemotion-backend:latest && \
gcloud run deploy kinemotion-backend \
  --image gcr.io/${PROJECT_ID}/kinemotion-backend:latest \
  --platform managed \
  --region us-central1
```

## Update Environment Variables

```bash
gcloud run services update kinemotion-backend \
  --platform managed \
  --region us-central1 \
  --set-env-vars "CORS_ORIGINS=https://kinemotion-mvp.vercel.app"
```

## Scale Resources

```bash
# Increase memory
gcloud run services update kinemotion-backend \
  --platform managed \
  --region us-central1 \
  --memory 1Gi

# Increase timeout
gcloud run services update kinemotion-backend \
  --platform managed \
  --region us-central1 \
  --timeout 1800
```

## URLs After Deployment

- **Frontend**: https://kinemotion-mvp.vercel.app
- **Backend**: https://kinemotion-backend-xxxxx-uc.a.run.app
- **Backend Health**: https://kinemotion-backend-xxxxx-uc.a.run.app/health
- **Cloud Run Console**: https://console.cloud.google.com/run/detail/us-central1/kinemotion-backend

## Environment Variables

**Cloud Run:**

- `CORS_ORIGINS`: Frontend URL
- `WORKERS`: Number of uvicorn workers (default: 1)
- `PORT`: Server port (default: 8000)
- `R2_ENDPOINT` (optional): Cloudflare R2 storage
- `R2_ACCESS_KEY` (optional): R2 credentials
- `R2_SECRET_KEY` (optional): R2 credentials
- `R2_BUCKET_NAME` (optional): R2 bucket name

**Vercel:**

- `VITE_API_URL`: Cloud Run backend URL

## Pricing

**Free Tier:**

- 2M requests/month
- 180,000 vCPU-seconds/month
- 1GB data transfer/month

**MVP Usage (100 videos/day):**

- Requests: 3,000/month ✅
- vCPU-seconds: 360,000/month = $4.32
- **Total: ~$4-5/month**

## Troubleshooting

| Issue              | Solution                                                         |
| ------------------ | ---------------------------------------------------------------- |
| Health check fails | Check logs: `gcloud run logs read kinemotion-backend --limit 50` |
| CORS errors        | Update CORS_ORIGINS env var                                      |
| Video upload hangs | Increase `--timeout` (max 3600s)                                 |
| Out of memory      | Increase `--memory` to 1Gi or 2Gi                                |
| Slow analysis      | Increase `--cpu` to 2 or 4                                       |

## Cost Tracking

- Monitor: https://console.cloud.google.com/billing
- Cloud Run metrics: https://console.cloud.google.com/run/detail/us-central1/kinemotion-backend?tab=metrics
