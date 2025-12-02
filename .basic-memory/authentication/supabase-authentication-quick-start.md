---
title: Supabase Authentication Quick Start
type: note
permalink: authentication/supabase-authentication-quick-start-1
tags:
- supabase
- authentication
- quickstart
- implementation
---

# Supabase Authentication - Quick Start

## ✅ Implementation Complete!

Supabase authentication has been fully integrated with both frontend and backend.

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
- ✅ ES256/RS256 verification via JWKS endpoint (modern)
- ✅ Automatic fallback to Auth server for HS256 projects (legacy)
- ✅ Middleware extracts user ID from tokens (`middleware.py`)
- ✅ User ID automatically logged in all requests
- ✅ User email logged for audit trail

## Quick Setup Steps

### 1. Create Supabase Project
- Go to [database.new](https://database.new)
- Name: `kinemotion`, Region: closest, Plan: Free (50K MAUs)

### 2. Get Credentials
- Dashboard → Settings → API Keys
- Copy: Project URL + Publishable key (`sb_publishable_xxx`)

### 3. Configure Authentication
- Dashboard → Authentication → URL Configuration
- Site URL: `https://kinemotion.vercel.app`
- Redirect URLs: `https://kinemotion.vercel.app/**`, `http://localhost:5173/**`

### 4. Environment Variables

**Frontend (.env.local):**
```
VITE_SUPABASE_URL=https://project.supabase.co
VITE_SUPABASE_ANON_KEY=sb_publishable_xxx
VITE_API_URL=http://localhost:8000
```

**Backend (.env):**
```
SUPABASE_URL=https://project.supabase.co
SUPABASE_ANON_KEY=sb_publishable_xxx
LOG_LEVEL=INFO
JSON_LOGS=false
```

### 5. Production Deployment

**Google Cloud Secrets:**
```bash
./scripts/setup-supabase-production.sh
```

**Vercel Environment Variables:**
Add VITE_SUPABASE_URL, VITE_SUPABASE_ANON_KEY, VITE_API_URL

## Testing Results
- ✅ All 85 backend tests pass
- ✅ 0 type errors (pyright strict)
- ✅ 0 linting errors (ruff)
- ✅ Frontend type checking passes

## Files Changed
**Frontend:** package.json, src/lib/supabase.ts, src/hooks/useAuth.ts, src/components/Auth.tsx, src/App.tsx, src/index.css
**Backend:** pyproject.toml, src/kinemotion_backend/auth.py, src/kinemotion_backend/middleware.py

## Free Tier: 50,000 MAUs/month (well within capacity)
