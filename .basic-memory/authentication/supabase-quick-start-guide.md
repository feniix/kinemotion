---
title: Supabase Quick Start Guide
type: note
permalink: authentication/supabase-quick-start-guide-1
tags:
- supabase
- authentication
- quick-start
- setup
---

# Supabase Authentication - Quick Start

## ✅ Implementation Complete!

Supabase authentication has been fully integrated with both frontend and backend.

---

## What Was Implemented

### Frontend (React + Vite)
- ✅ Supabase client configuration (`src/lib/supabase.ts`)
- ✅ Authentication hook (`src/hooks/useAuth.ts`)
- ✅ Sign in/sign up component (`src/components/Auth.tsx`)
- ✅ Updated App.tsx with auth flow
- ✅ Auth token sent to backend in API requests
- ✅ CSS styling for auth UI

### Backend (FastAPI + Cloud Run)
- ✅ Supabase JWT validation (`src/kinemotion_backend/auth.py`)
- ✅ RS256 verification via JWKS endpoint (recommended)
- ✅ Automatic fallback to Auth server for HS256 projects
- ✅ Middleware extracts user ID from tokens (`middleware.py`)
- ✅ User ID automatically logged in all requests
- ✅ User email logged for audit trail

---

## Setup Instructions

### 1. Create Supabase Project

1. Go to [database.new](https://database.new) (official Supabase project creation URL)
2. Sign in or create account
3. Create new project:
   - **Name:** `kinemotion`
   - **Database password:** Click "Generate a password"
   - **Region:** Choose closest to users (e.g., `us-east-1`)
   - **Plan:** Free (50,000 MAUs)
4. Click **Create new project**
5. Wait ~2 minutes for setup

### 2. Get Credentials

Dashboard → **Settings** → **API Keys**:

| Credential | Where to Find | Format |
|------------|---------------|--------|
| **Project URL** | Top of API Keys page | `https://xxx.supabase.co` |
| **Publishable key** | Under "Publishable key" | `sb_publishable_xxx...` |

> **Note:** New projects use `sb_publishable_xxx` format. Legacy projects may have JWT-style keys (`eyJ...`).

### 3. Configure Authentication

Dashboard → **Authentication** → **URL Configuration**:

| Setting | Value |
|---------|-------|
| **Site URL** | `https://kinemotion.vercel.app` |
| **Redirect URLs** | `https://kinemotion.vercel.app/**` |
| | `http://localhost:5173/**` |

> **Tip:** Use `/**` wildcard to allow all paths under your domain.

### 4. Frontend Environment Variables

**Development** (`frontend/.env.local`):
```bash
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=sb_publishable_xxxxxxxxxxxxxxxxxxxxx
VITE_API_URL=http://localhost:8000
```

**Production** (Vercel Dashboard → Settings → Environment Variables):
```
VITE_SUPABASE_URL → https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY → sb_publishable_xxx...
VITE_API_URL → https://kinemotion-backend-xxx.run.app
```

### 5. Backend Environment Variables

**Development** (`backend/.env`):
```bash
SUPABASE_URL=https://your-project.supabase.co
# Optional: for Auth server fallback (HS256 projects)
SUPABASE_ANON_KEY=sb_publishable_xxxxxxxxxxxxxxxxxxxxx
LOG_LEVEL=INFO
JSON_LOGS=false
```

> **Note:** JWT secret is NOT needed for new RS256 projects! The backend verifies tokens via JWKS endpoint.

**Production** (Google Secret Manager):

```bash
# 1. Create secrets
echo -n "https://your-project-id.supabase.co" | \
  gcloud secrets create SUPABASE_URL --data-file=- --project=kinemotion-backend

echo -n "sb_publishable_xxxxxxxxxxxxxxxxxxxxx" | \
  gcloud secrets create SUPABASE_ANON_KEY --data-file=- --project=kinemotion-backend

# 2. Grant access to Cloud Run service account
gcloud secrets add-iam-policy-binding SUPABASE_URL \
  --member="serviceAccount:github-actions-deploy@kinemotion-backend.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor" \
  --project=kinemotion-backend

gcloud secrets add-iam-policy-binding SUPABASE_ANON_KEY \
  --member="serviceAccount:github-actions-deploy@kinemotion-backend.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor" \
  --project=kinemotion-backend
```

---

## Testing

### Local Testing

```bash
# Terminal 1: Backend
cd backend
uv run uvicorn kinemotion_backend.app:app --reload

# Terminal 2: Frontend
cd frontend
yarn dev
```

Open `http://localhost:5173`:
1. Sign up with email
2. Check email for confirmation
3. Sign in
4. Upload video (token automatically sent!)

### Check Logs

Backend logs will show:

```json
{
  "event": "request_started",
  "user_id": "abc123...",
  "user_email": "coach@example.com",
  "request_id": "xyz...",
  "method": "POST",
  "path": "/api/analyze"
}
```

---

## Production Deployment

### Deploy Backend
```bash
git add .
git commit -m "feat: add Supabase authentication"
git push origin main
```

### Deploy Frontend
```bash
# Vercel auto-deploys on push
git push origin main
```

---

## Features

### User ID Logging ✅
Every request now includes:
- `user_id` - Unique Supabase user ID
- `user_email` - User email
- `request_id` - Request tracking ID

Example log:
```json
{
  "event": "video_analysis_completed",
  "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "user_email": "coach@example.com",
  "jump_type": "cmj",
  "duration_ms": 15234.56
}
```

### Audit Trail ✅
All API calls are logged with user identity for:
- Video uploads
- Analysis requests
- Errors and failures
- Authentication attempts

---

## Free Tier Capacity

**Supabase Free Tier:**
- 50,000 MAUs/month
- 500 MB database
- 2 GB bandwidth
- Unlimited API requests

**Estimated usage for kinemotion:**
- 100 videos/day = ~1,000-2,000 MAUs/month
- **Cost: $0** (well within free tier)

---

## Next Steps (Optional)

- [ ] Add password reset flow
- [ ] Enable Google OAuth
- [ ] Add user profile page
- [ ] Implement role-based access (coach vs athlete)
- [ ] Add email verification reminders

---

## Support

**Documentation:**
- Setup Guide: See "Supabase Production Setup Guide" note
- Structured Logging: See "Structured Logging Implementation" note

**Links:**
- Supabase Docs: https://supabase.com/docs
- Supabase Auth Guide: https://supabase.com/docs/guides/auth

**Issues:**
- GitHub: https://github.com/feniix/kinemotion/issues
