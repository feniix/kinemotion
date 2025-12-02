---
title: Supabase Authentication Setup Guide
type: note
permalink: authentication/supabase-authentication-setup-guide-1
tags:
- supabase
- authentication
- setup-guide
- production
---

# Supabase Authentication Setup Guide

## Overview
Kinemotion uses Supabase for authentication with JWT token validation, automatic user ID logging, and protected API endpoints.

## Modern Approach (December 2025)

**JWT Signing Keys:**
- **Modern**: ES256/RS256 (asymmetric) - JWKS endpoint verification
- **Legacy**: HS256 (symmetric) - Auth server fallback

**Backend support:** Tries JWKS first, falls back to Auth server automatically.

## Step 1: Create Supabase Project

1. Go to [database.new](https://database.new)
2. Fill in: Name (kinemotion), Password (generate), Region (us-east-1), Plan (Free)
3. Click "Create new project"
4. Wait ~2 minutes

**Note:** New projects (July 2025+) use ES256 automatically. Legacy projects: migrate via Settings → JWT signing keys → "Migrate JWT secret".

## Step 2: Get Credentials

Dashboard → Settings → API Keys:
- **Project URL**: `https://xxx.supabase.co`
- **Publishable key**: `sb_publishable_xxx...` (safe for frontend)
- **Secret key**: `sb_secret_xxx...` (server-side only)

**Key format change (2025):** New format is `sb_publishable_xxx`, legacy is JWT-style `eyJ...`.

## Step 3: Configure Authentication

### URL Configuration
- Path: Authentication → URL Configuration
- Site URL: `https://kinemotion.vercel.app`
- Redirect URLs: `https://kinemotion.vercel.app/**`, `http://localhost:5173/**`

### Email Provider
- Path: Authentication → Providers
- Email is enabled by default

## Step 4: Frontend Environment Variables

**Development (.env.local):**
```
VITE_SUPABASE_URL=https://project-id.supabase.co
VITE_SUPABASE_ANON_KEY=sb_publishable_xxx
VITE_API_URL=http://localhost:8000
```

**Production (Vercel):**
Add same variables via Settings → Environment Variables

## Step 5: Backend Environment Variables

**Development (.env):**
```
SUPABASE_URL=https://project-id.supabase.co
SUPABASE_ANON_KEY=sb_publishable_xxx  # Optional, for Auth server fallback
LOG_LEVEL=INFO
JSON_LOGS=false
```

**Production (Cloud Run):**
1. Create secrets in Google Secret Manager
2. Grant IAM access to service account
3. Update deploy-backend.yml with --set-secrets flag

See full commands in detailed guide.

## Testing Locally

```bash
# Backend
cd backend && uv run uvicorn kinemotion_backend.app:app --reload

# Frontend
cd frontend && yarn dev
```

Open http://localhost:5173 → Sign up → Confirm email → Sign in → Upload video

## Verification
Logs show: `user_id`, `user_email`, `request_id` in all requests

## Troubleshooting
- Invalid token: Re-sign in (tokens expire after 1 hour)
- JWKS failed: Normal for HS256, backend uses fallback
- CORS error: Check CORS_ORIGINS includes Vercel domain

## Security
- ES256: Public/private keys (can't forge tokens)
- HS256: Shared secret (anyone with it can forge) - deprecated
- Never commit .env files
- Use Secret Manager for production

## Free Tier: 50,000 MAUs/month
Pro: $25/month (100K MAUs), Additional: $0.00325/MAU
