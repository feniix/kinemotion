# Issue #12: Web UI MVP - Complete Setup Guide

This document provides a complete setup guide for the Kinemotion Web UI MVP (Issue #12), including both backend and frontend scaffolding.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                  KINEMOTION WEB MVP                      │
└─────────────────────────────────────────────────────────┘
          │                           │
          ▼                           ▼
    ┌─────────────┐         ┌──────────────────┐
    │  Frontend   │         │     Backend      │
    │  (Vercel)   │         │  (Cloud Run)     │
    │             │         │                  │
    │ React+Vite  │◄────────┤ FastAPI + uv     │
    │ Yarn        │ API     │ Real metrics     │
    └─────────────┘ calls   └────────┬─────────┘
         │                           │
         │                           ▼
         │                    ┌──────────────────┐
         │                    │ Cloudflare R2    │
         │                    │ Video Storage    │
         │                    │ Results Persist  │
         └────────────────────┘ Download URLs    │
                                └──────────────────┘

FLOWS:
1. Coach uploads video via frontend → Backend analyzes → R2 stores results
2. Backend returns real metrics (CMJ/Drop Jump) → Frontend displays
3. Coach downloads debug video/results from R2 link
```

## Quick Start (Development)

### Backend Setup

```bash
cd backend

# Install dependencies
uv sync

# Set environment variables (optional - R2 is optional)
cp .env.example .env.local
# Leave empty for now - R2 storage is optional for MVP

# Start backend
uv run uvicorn kinemotion_backend.app:app --reload

# Backend is now running at http://localhost:8000
# API docs at http://localhost:8000/docs
```

### Frontend Setup

```bash
cd frontend

# Install dependencies with Yarn
yarn install

# Set environment variables
cp .env.example .env.local
# Set: VITE_API_URL=http://localhost:8000

# Start frontend
yarn dev

# Frontend is now running at http://localhost:5173
# Open browser and start testing
```

### Test the Full Stack

1. Open http://localhost:5173
1. Upload a CMJ or Drop Jump video (\< 500MB)
1. Select jump type
1. Click "Analyze"
1. Wait 10-60 seconds
1. See real metrics from kinemotion library

## Deployment

### Backend: Deploy to Google Cloud Run

Backend deploys automatically via GitHub Actions when you push to main.

```bash
# Manual deployment (if needed)
# Ensure you have gcloud CLI installed and authenticated

cd backend

# Build and push to Google Cloud Run
# This is handled by .github/workflows/deploy-backend.yml automatically

# View logs
gcloud run services logs tail kinemotion-backend --project=kinemotion-backend

# Your backend is live at https://kinemotion-backend-1008251132682.us-central1.run.app
```

### Frontend: Deploy to Vercel

```bash
cd frontend

# Option 1: Connect GitHub repo to Vercel (recommended)
# 1. Visit https://vercel.com/new
# 2. Select this repository
# 3. Set Root Directory: frontend
# 4. Add environment variable: VITE_API_URL=https://kinemotion-backend-1008251132682.us-central1.run.app
# 5. Deploy

# Option 2: Deploy via Vercel CLI
vercel --cwd=frontend
# Set: VITE_API_URL=https://kinemotion-backend-1008251132682.us-central1.run.app

# Your frontend is now live at https://kinemotion-mvp.vercel.app
```

## Project Structure

```
kinemotion/
├── backend/                          ← FastAPI backend (can move to separate repo later)
│   ├── src/kinemotion_backend/
│   │   ├── __init__.py
│   │   └── app.py                    ← Main FastAPI application
│   ├── pyproject.toml                ← Dependencies (uv)
│   ├── Dockerfile                    ← Container for Cloud Run
│   ├── .env.example                  ← Environment template
│   ├── .dockerignore
│   ├── README.md                     ← Backend docs
│   ├── SETUP.md                      ← Backend deployment guide
│   ├── IMPLEMENTATION_SUMMARY.md     ← Technical details
│   └── uv.lock                       ← Locked dependencies
│
├── frontend/                         ← React frontend (can move to separate repo later)
│   ├── src/
│   │   ├── main.tsx                  ← React entry point
│   │   ├── App.tsx                   ← Main component
│   │   ├── index.css                 ← Styles
│   │   └── components/
│   │       ├── UploadForm.tsx
│   │       ├── ResultsDisplay.tsx
│   │       ├── ErrorDisplay.tsx
│   │       └── LoadingSpinner.tsx
│   ├── package.json                  ← Yarn dependencies
│   ├── vite.config.ts                ← Vite configuration
│   ├── tsconfig.json                 ← TypeScript configuration
│   ├── vercel.json                   ← Vercel deployment
│   ├── index.html                    ← HTML entry point
│   ├── .env.example                  ← Environment template
│   ├── .gitignore
│   ├── README.md                     ← Frontend docs
│   ├── yarn.lock                     ← Locked dependencies
│   └── dist/                         ← Built files (after yarn build)
│
└── src/kinemotion/                   ← Core library (unchanged)
    ├── api.py
    ├── cli.py
    ├── core/
    ├── cmj/
    └── dropjump/
```

## API Endpoints

### Backend: `http://localhost:8000` (dev) or `https://kinemotion-backend-1008251132682.us-central1.run.app` (prod)

#### Health Check

```bash
GET /health

Response:
{
  "status": "healthy",
  "service": "Kinemotion Web Backend",
  "version": "0.1.0",
  "r2_configured": false,
  "timestamp": "2024-11-28T10:30:00"
}
```

#### Analyze Video

```bash
POST /api/analyze

Request (multipart/form-data):
- video: <file>  (MP4, AVI, MOV, MKV, FLV, WMV)
- jump_type: "cmj" or "dropjump"

Response (200):
{
  "status": 200,
  "message": "Successfully analyzed cmj video",
  "processing_time_s": 12.34,
  "metrics": {
    "data": {
      "jump_height_m": 0.456,
      "flight_time_ms": 608.23,
      "countermovement_depth_m": 0.234,
      "peak_height_m": 0.456,
      ...
    },
    "metadata": {...},
    "validation": {...}
  },
  "results_url": "https://r2-bucket.com/results/cmj/..."
}
```

## Environment Variables

### Backend (`backend/.env`)

```env
# R2 Storage (optional - leave empty for development)
R2_ENDPOINT=https://your-account-id.r2.cloudflarestorage.com
R2_ACCESS_KEY=your_access_key
R2_SECRET_KEY=your_secret_key
R2_BUCKET_NAME=kinemotion

# API Configuration
LOG_LEVEL=info
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,https://kinemotion.vercel.app

# R2 Storage (optional - leave empty for development)
R2_ENDPOINT=https://your-account-id.r2.cloudflarestorage.com
R2_ACCESS_KEY=your_access_key
R2_SECRET_KEY=your_secret_key
R2_BUCKET_NAME=kinemotion

# Supabase Database (configured in Google Cloud Secret Manager for production)
SUPABASE_URL=https://smutfsalcbnfveqijttb.supabase.co
SUPABASE_ANON_KEY=your_key_here
```

### Frontend (`frontend/.env`)

```env
# Development
VITE_API_URL=http://localhost:8000

# Production
# VITE_API_URL=https://kinemotion-backend-1008251132682.us-central1.run.app
```

## Cloudflare R2 Setup (Optional)

R2 is optional for MVP - videos can be stored temporarily without it. To enable:

### 1. Create R2 bucket

```bash
# Visit https://dash.cloudflare.com
# Go to R2 section
# Create bucket named "kinemotion"
```

### 2. Generate API token

```bash
# In R2 settings:
# 1. Create API Token
# 2. Grant: Object Read/Write permissions
# 3. Restrict to "kinemotion" bucket
# 4. Copy: Access Key ID, Secret Access Key
```

### 3. Get R2 endpoint

```bash
# In R2 bucket settings:
# Copy: S3 API endpoint
# Format: https://YOUR_ACCOUNT_ID.r2.cloudflarestorage.com
```

### 4. Set secrets in Google Cloud Secret Manager

```bash
# R2 credentials are stored in Google Cloud Secret Manager
# and accessed by Cloud Run service account
# See backend deployment documentation for details
```

## Key Design Decisions

### 1. Real Metrics (Not Mocked)

- **Why:** MVP coaches test with real data, not fake numbers
- **Implementation:** Uses actual `process_cmj_video()` and `process_dropjump_video()`
- **Future:** When #10 fixes ankle angle, just update library version

### 2. Optional R2 Storage

- **Why:** Free tier MVP doesn't need persistent storage initially
- **Benefit:** Works without R2, scales up gracefully
- **Implementation:** Backend gracefully handles missing R2 credentials

### 3. Google Cloud Run + Vercel + Supabase

- **Backend:** Google Cloud Run (video processing, auto-scales)
- **Frontend:** Vercel free tier (industry standard for React)
- **Database:** Supabase (PostgreSQL database)
- **Authentication:** Supabase Auth (OAuth, email/password)
- **Storage:** Cloudflare R2 (video and results file storage)
- **Total Cost:** Minimal for MVP testing

### 4. Separate Backend/Frontend Directories

- **Why:** Easy to split into separate repos later
- **Path:** `kinemotion` → `kinemotion-backend` + `kinemotion-frontend`
- **Benefit:** Independent development, deployment, scaling

## Troubleshooting

### Backend won't start

```bash
# Check Python version
python --version  # Should be 3.12+

# Reinstall dependencies
cd backend
rm -rf .venv uv.lock
uv sync

# Start with verbose logging
uv run uvicorn kinemotion_backend.app:app --reload --log-level debug
```

### Frontend can't connect to backend

```bash
# Check backend is running
curl http://localhost:8000/health

# Check VITE_API_URL in .env.local
cat .env.local

# Clear frontend build cache
cd frontend
rm -rf node_modules dist
yarn install
yarn dev
```

### Video upload fails

```bash
# Check file size (max 500MB)
ls -lh your_video.mp4

# Check file format (must be video/*)
file your_video.mp4

# Check backend logs
gcloud run services logs tail kinemotion-backend --project=kinemotion-backend
# or check terminal for local development
```

### R2 upload fails (if R2 configured)

```bash
# Check R2 credentials in Google Cloud Secret Manager
gcloud secrets versions access latest --secret=R2_ACCESS_KEY --project=kinemotion-backend
gcloud secrets versions access latest --secret=R2_SECRET_KEY --project=kinemotion-backend

# Verify endpoint and bucket name are correct
# Test R2 connection from Cloud Run logs
```

## Testing Checklist

- [ ] Backend starts without errors
- [ ] Frontend starts without errors
- [ ] Frontend connects to backend (check /docs)
- [ ] Upload CMJ video → see real metrics
- [ ] Upload Drop Jump video → see real metrics
- [ ] File validation works (reject >500MB, wrong format)
- [ ] Loading spinner appears during analysis
- [ ] Results display correctly
- [ ] Error messages are user-friendly
- [ ] Mobile responsive on phone
- [ ] Backend deploys to Cloud Run (automatic via GitHub Actions)
- [ ] Frontend deploys to Vercel
- [ ] Production URLs work
- [ ] R2 download links work (if R2 configured)
- [ ] Supabase integration works

## Next Steps

### After MVP Scaffolding:

1. **Recruit coaches** for testing (5-10 people)
1. **Gather feedback** on metrics and UI
1. **Test issue #10 fixes** - integrate when ankle angle is corrected
1. **Iterate UI** based on coach feedback

### When #10 Complete:

1. Update `backend/pyproject.toml` with new kinemotion version
1. Redeploy backend (30 minutes)
1. Metrics automatically improve for all coaches

### For Production:

1. Add authentication (if needed)
1. Add user accounts/history (if coaches want it)
1. Real-time analysis (if coaches request it)
1. Running gait analysis (if runners request it)

## Documentation Files

- **Backend:**

  - `backend/README.md` - Backend overview
  - `backend/docs/setup.md` - Setup and deployment
  - `backend/docs/implementation-summary.md` - Technical details
  - `backend/docs/tests.md` - Test documentation

- **Frontend:**

  - `frontend/README.md` - Frontend overview
  - `frontend/.env.example` - Environment template

- **This file:**

  - `setup-issue-12.md` - Complete project guide

## Support

For issues:

1. Check troubleshooting section above
1. Review backend logs: `gcloud run services logs tail kinemotion-backend --project=kinemotion-backend`
1. Check frontend console (browser DevTools)
1. Review README files in backend/ and frontend/
1. Check GitHub issues for known problems

## Architecture Diagram

```
Coach (Phone/Desktop)
         │
         ▼
┌─────────────────────────┐
│   Frontend (Vercel)     │
│  https://kinemotion.    │
│  vercel.app             │
│                         │
│ React + Vite + Yarn     │
│ - Upload form           │
│ - Results display       │
│ - Error handling        │
└────────────┬────────────┘
             │ POST /api/analyze
             │ (multipart: video + jump_type)
             ▼
┌─────────────────────────┐
│  Backend (Cloud Run)    │
│  https://kinemotion-    │
│  backend...run.app      │
│                         │
│ FastAPI + Python 3.12   │
│ - Upload handler        │
│ - Real metrics (CMJ/DJ) │
│ - R2 integration        │
│ - Supabase client       │
│ - Error handling        │
└────────────┬────────────┘
             │
    ┌────────┴────────┐
    │                 │
    ▼                 ▼
┌─────────────┐   ┌──────────────────┐
│  Supabase   │   │ Cloudflare R2    │
│             │   │                  │
│ - Auth      │   │ - Videos (temp)  │
│ - Database  │   │ - Results (JSON) │
│ - Sessions  │   │ - Debug videos   │
│ - Metadata  │   └──────────────────┘
└─────────────┘            │
                           ▼
                      (Frontend)
                   Download links
```

______________________________________________________________________

**Issue #12 Status:** ✅ Phase 0 Scaffolding Complete
**Next:** Recruit coaches for testing
**Timeline to MVP Live:** ~1 week (pending coach recruitment)
