# Kinemotion MVP Deployment Guide

## Architecture: Google Cloud Run + Vercel

This guide deploys the Kinemotion MVP across two platforms:

- **Frontend**: Vercel (React/TypeScript)
- **Backend**: Google Cloud Run (FastAPI)

**Total Cost**: ~$4-5/month (essentially free for MVP traffic)

______________________________________________________________________

## Prerequisites

1. **Google Cloud Account**: Sign up at https://cloud.google.com/
1. **Vercel Account**: Already configured
1. **gcloud CLI**: Install from https://cloud.google.com/sdk/docs/install
1. **Docker**: For local testing (optional but recommended)

______________________________________________________________________

## Step 1: Set Up Google Cloud Project

### 1.1 Create a Google Cloud Project

```bash
# Create new project
gcloud projects create kinemotion-backend --name="Kinemotion Backend"

# Set as default
gcloud config set project kinemotion-backend

# Get project ID
PROJECT_ID=$(gcloud config get-value project)
echo "Project ID: $PROJECT_ID"
```

### 1.2 Enable Required APIs

```bash
# Enable Cloud Run
gcloud services enable run.googleapis.com

# Enable Container Registry (for image storage)
gcloud services enable containerregistry.googleapis.com

# Enable Cloud Build (for building images)
gcloud services enable cloudbuild.googleapis.com
```

### 1.3 Authenticate with Docker

```bash
# Configure Docker authentication to Google Container Registry
gcloud auth configure-docker gcr.io
```

______________________________________________________________________

## Step 2: Build and Push Docker Image

### 2.1 Build Docker Image Locally

From the `/backend` directory:

```bash
cd backend

# Build Docker image for x86_64 (Cloud Run architecture)
# Using buildx for cross-platform builds from Apple Silicon
docker buildx build --platform linux/amd64 -t gcr.io/${PROJECT_ID}/kinemotion-backend:latest .
```

### 2.2 Push to Container Registry

```bash
# Push image to Google Container Registry
docker push gcr.io/${PROJECT_ID}/kinemotion-backend:latest

# Verify push (optional)
gcloud container images list --repository=gcr.io/${PROJECT_ID}
```

______________________________________________________________________

## Step 3: Deploy to Cloud Run

### 3.1 Deploy Service

```bash
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

**Parameter Explanations:**

- `--platform managed`: Cloud Run fully managed (serverless)
- `--region us-central1`: US Central (adjust to your region)
- `--allow-unauthenticated`: Public API (no auth required for MVP)
- `--timeout 600`: 10 minutes for long video processing
- `--memory 512Mi`: Sufficient for video analysis
- `--cpu 1`: Single CPU (appropriate for MVP)
- `--max-instances 10`: Auto-scale up to 10 instances
- `--set-env-vars`: Environment configuration

### 3.2 Capture Deployment URL

```bash
# Get the deployed service URL
SERVICE_URL=$(gcloud run services describe kinemotion-backend \
  --platform managed \
  --region us-central1 \
  --format 'value(status.url)')

echo "Backend URL: $SERVICE_URL"
# Should output something like:
# https://kinemotion-backend-xxxxx-uc.a.run.app
```

Save this URL - you'll need it for Vercel configuration.

### 3.3 Verify Deployment

```bash
# Test health check
curl $SERVICE_URL/health

# Expected response:
# {"status":"ok","service":"kinemotion-backend","version":"0.1.0","timestamp":"...","r2_configured":false}
```

______________________________________________________________________

## Step 4: Configure Frontend on Vercel

### 4.1 Set Environment Variable

Go to **Vercel Dashboard**:

1. Navigate to `https://vercel.com/dashboard`
1. Select **kinemotion** project
1. Click **Settings** → **Environment Variables**
1. Add new variable:
   - **Name**: `VITE_API_URL`
   - **Value**: `https://kinemotion-backend-xxxxx-uc.a.run.app` (your Cloud Run URL)
   - **Environments**: Production (and Staging if desired)
1. Click **Save**

### 4.2 Trigger Frontend Redeploy

```bash
# Via Vercel Dashboard:
# Deployments → Select latest → Redeploy

# Or via Vercel CLI:
cd frontend
npx vercel --prod
```

______________________________________________________________________

## Step 5: Test End-to-End

### 5.1 Access Frontend

Open `https://kinemotion-mvp.vercel.app` in browser

### 5.2 Upload Test Video

1. Select jump type (CMJ or Drop Jump)
1. Upload test video
1. Wait for analysis
1. Verify metrics display correctly

### 5.3 Check Backend Logs

```bash
# Stream Cloud Run logs
gcloud run logs read kinemotion-backend --platform managed --region us-central1 --limit 50 --follow

# Or use Cloud Console:
# https://console.cloud.google.com/run/detail/us-central1/kinemotion-backend
```

______________________________________________________________________

## Troubleshooting

### Health Check Fails

```bash
# Check Cloud Run status
gcloud run services describe kinemotion-backend --platform managed --region us-central1

# View detailed logs
gcloud run logs read kinemotion-backend --platform managed --region us-central1 --limit 100
```

### CORS Errors

Update CORS origins in Cloud Run:

```bash
gcloud run services update kinemotion-backend \
  --platform managed \
  --region us-central1 \
  --set-env-vars "CORS_ORIGINS=https://kinemotion-mvp.vercel.app"
```

### Video Upload Fails

1. Check file size (max 500MB in code)
1. Verify file format (.mp4, .mov, .avi, etc.)
1. Check backend logs for errors
1. Increase `--timeout` if processing takes >10 minutes

### Memory/CPU Issues

Increase resources:

```bash
gcloud run services update kinemotion-backend \
  --platform managed \
  --region us-central1 \
  --memory 1Gi \
  --cpu 2
```

**Note**: Higher memory/CPU increases monthly cost (~$1 per 512Mi increase)

______________________________________________________________________

## Monitoring & Scaling

### View Metrics

```bash
# View Cloud Run metrics (requests, latency, errors)
gcloud monitoring metrics-descriptors list --filter="metric.type:run.googleapis.com/*"
```

Or in **Cloud Console**:

- https://console.cloud.google.com/run/detail/us-central1/kinemotion-backend?tab=metrics

### Adjust Scaling

```bash
# Update max instances (default 10, can go up to 1000)
gcloud run services update kinemotion-backend \
  --platform managed \
  --region us-central1 \
  --max-instances 100

# Update timeout (default 600s, max 3600s)
gcloud run services update kinemotion-backend \
  --platform managed \
  --region us-central1 \
  --timeout 1800
```

______________________________________________________________________

## Cost Tracking

### Estimate Monthly Cost

**Free Tier Includes:**

- 2,000,000 requests/month
- 180,000 vCPU-seconds/month
- 1 GB data transfer/month

**MVP Usage (100 videos/day):**

- Requests: 3,000/month ✅ (within free tier)
- vCPU-seconds: 360,000/month (180k free + 180k @ $0.000024 = $4.32)
- **Estimated Total: $4-5/month**

### Monitor in Cloud Console

Go to:

- https://console.cloud.google.com/billing

______________________________________________________________________

## Redeploy After Code Changes

### Quick Redeploy

```bash
cd backend

# Build and push new image (x86_64 for Cloud Run)
docker buildx build --platform linux/amd64 -t gcr.io/${PROJECT_ID}/kinemotion-backend:latest . && \
docker push gcr.io/${PROJECT_ID}/kinemotion-backend:latest

# Deploy (reuses most recent image)
gcloud run deploy kinemotion-backend \
  --image gcr.io/${PROJECT_ID}/kinemotion-backend:latest \
  --platform managed \
  --region us-central1
```

______________________________________________________________________

## Optional: R2 Storage Configuration

For persisting results to Cloudflare R2:

```bash
# Set R2 credentials as Cloud Run environment variables
gcloud run services update kinemotion-backend \
  --platform managed \
  --region us-central1 \
  --set-env-vars "R2_ENDPOINT=https://your-r2-domain.com" \
  --set-env-vars "R2_ACCESS_KEY=your-access-key" \
  --set-env-vars "R2_SECRET_KEY=your-secret-key" \
  --set-env-vars "R2_BUCKET_NAME=kinemotion"
```

______________________________________________________________________

## Next Steps

1. ✅ Deploy backend to Cloud Run
1. ✅ Configure frontend on Vercel
1. ✅ Test end-to-end with sample video
1. 📋 Recruit 5-10 coaches for MVP testing
1. 📊 Gather feedback on metrics accuracy
1. 🔄 Iterate based on feedback

______________________________________________________________________

## Support

- **Google Cloud Documentation**: https://cloud.google.com/run/docs
- **Cloud Run FAQ**: https://cloud.google.com/run/docs/faq
- **Kinemotion Issues**: https://github.com/feniix/kinemotion/issues
