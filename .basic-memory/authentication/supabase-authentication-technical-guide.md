---
title: Supabase Authentication Technical Guide
type: note
permalink: authentication/supabase-authentication-technical-guide-1
tags:
- supabase
- authentication
- technical
- jwt
- security
---

# Supabase Authentication Technical Guide

## Overview

Kinemotion uses Supabase for authentication, providing secure user management with JWT tokens.

**What's Included:**
- ✅ Email/password authentication
- ✅ JWT token validation in backend (RS256 + Auth server fallback)
- ✅ Automatic user ID logging in all requests
- ✅ Protected API endpoints
- ✅ Works with `kinemotion.vercel.app` domain

---

## Important: JWT Signing Keys (Modern Approach)

Supabase now uses **asymmetric JWT signing keys** (ES256/RS256) as the modern standard:

| Type | Algorithm | Status | Verification Method |
|------|-----------|--------|---------------------|
| **Asymmetric** (modern) | ES256/RS256 | ✅ **Recommended** | JWKS endpoint |
| **Symmetric** (legacy) | HS256 | ⚠️ Deprecated | Auth server fallback |

**Our backend supports both automatically:**
1. Tries asymmetric verification via JWKS endpoint first (modern)
2. Falls back to Auth server verification if JWKS is empty (legacy compatibility)

**To use the modern approach:**
1. Supabase Dashboard → **Settings** → **JWT signing keys**
2. Click **"Migrate JWT secret"** if you see it
3. Then click **"Rotate keys"** to start using ES256

> **Why ES256?** Faster verification, better security (public/private keys can't be forged), easier compliance (SOC2, HIPAA), and automatic key revocation via JWKS.

---

## Step 1: Create Supabase Project

1. Go to [database.new](https://database.new) (official Supabase project creation URL)
2. Sign in or create a Supabase account
3. Create a new organization (if needed)
4. Fill in project details:
   - **Project name:** `kinemotion`
   - **Database password:** (click "Generate a password" for a strong password)
   - **Region:** Choose closest to your users (e.g., `us-east-1`)
   - **Plan:** Free (50,000 MAUs included)
5. Click **Create new project**
6. Wait for project to be created (~2 minutes)

> **Note:** New projects (created July 2025+) automatically use ES256 (asymmetric) signing keys. If you have an existing project with legacy JWT secret, migrate it: **Settings** → **JWT signing keys** → **Migrate JWT secret**.

---

## Step 2: Get Supabase Credentials

Once your project is ready:

1. Go to **Settings** (gear icon in sidebar)
2. Click **API Keys** in the left menu
3. Copy the following:

| Credential | Location | Description |
|------------|----------|-------------|
| **Project URL** | Top of API Keys page | `https://xxx.supabase.co` |
| **Publishable key** | Under "Publishable key" | Safe for frontend (starts with `sb_publishable_...`) |
| **Secret key** | Under "Secret keys" | Server-side only (starts with `sb_secret_...`) |

> **Key Format Change (2025):** New projects use the `sb_publishable_xxx` format. Legacy projects may still show JWT-style keys starting with `eyJ...`. Both formats work the same way.

---

## Step 3: Configure Authentication Settings

### URL Configuration

1. In Supabase dashboard, click **Authentication** in sidebar
2. Click **URL Configuration** in the left menu
3. Configure the following:

| Setting | Value | Purpose |
|---------|-------|---------|
| **Site URL** | `https://kinemotion.vercel.app` | Default redirect after auth |
| **Redirect URLs** | `https://kinemotion.vercel.app/**` | Production redirects |
| | `http://localhost:5173/**` | Local development |

> **Tip:** Use `/**` wildcard to allow all paths under your domain.

### Email Provider

1. Click **Providers** in the left menu
2. **Email** provider is enabled by default
3. *(Optional)* Configure email templates under **Email Templates**

### Social Providers (Optional)

1. Under **Providers**, enable Google, GitHub, etc.
2. Follow the setup instructions for each provider

---

## Step 4: Frontend Environment Variables

### Development (.env.local)

Create `frontend/.env.local`:

```bash
VITE_SUPABASE_URL=https://your-project-id.supabase.co
VITE_SUPABASE_ANON_KEY=sb_publishable_xxxxxxxxxxxxxxxxxxxxx
VITE_API_URL=http://localhost:8000
```

> **Note:** New projects use `sb_publishable_xxx` format. Legacy projects may have JWT-style keys (`eyJ...`). Both formats work.

### Production (Vercel)

Add environment variables in Vercel dashboard:

1. Go to your project on [vercel.com](https://vercel.com)
2. Click **Settings** → **Environment Variables**
3. Add the following:

| Variable | Value | Environment |
|----------|-------|-------------|
| `VITE_SUPABASE_URL` | `https://xxx.supabase.co` | Production |
| `VITE_SUPABASE_ANON_KEY` | Your publishable key | Production |
| `VITE_API_URL` | `https://kinemotion-backend-xxx.run.app` | Production |

4. Click **Save** for each variable

---

## Step 5: Backend Environment Variables

### Development (.env)

Create `backend/.env`:

```bash
# Required
SUPABASE_URL=https://your-project.supabase.co

# Optional (for Auth server fallback verification)
SUPABASE_ANON_KEY=sb_publishable_xxxxxxxxxxxxxxxxxxxxx

# Logging
LOG_LEVEL=INFO
JSON_LOGS=false
```

**Environment Variables Explained:**

| Variable | Required | Description |
|----------|----------|-------------|
| `SUPABASE_URL` | Yes | Your project URL (e.g., `https://xxx.supabase.co`) |
| `SUPABASE_ANON_KEY` | No | Anon/public key for Auth server fallback |

> **Note:** JWT secret is NOT needed for new RS256 projects. The backend verifies tokens via the public JWKS endpoint (`/.well-known/jwks.json`).

### Production (Cloud Run)

**Step 1: Create secrets in Google Cloud**

```bash
# Set Supabase URL secret (required)
echo -n "https://your-project-id.supabase.co" | \
  gcloud secrets create SUPABASE_URL \
  --data-file=- \
  --project=kinemotion-backend

# Set Anon key secret (optional, for Auth server fallback)
echo -n "sb_publishable_xxxxxxxxxxxxxxxxxxxxx" | \
  gcloud secrets create SUPABASE_ANON_KEY \
  --data-file=- \
  --project=kinemotion-backend

# Grant Cloud Run service account access to secrets
gcloud secrets add-iam-policy-binding SUPABASE_URL \
  --member="serviceAccount:github-actions-deploy@kinemotion-backend.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor" \
  --project=kinemotion-backend

gcloud secrets add-iam-policy-binding SUPABASE_ANON_KEY \
  --member="serviceAccount:github-actions-deploy@kinemotion-backend.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor" \
  --project=kinemotion-backend
```

**Step 2: Update `.github/workflows/deploy-backend.yml`**

Find the "Deploy to Cloud Run" step and update the `flags` section:

```yaml
- name: Deploy to Cloud Run
  uses: google-github-actions/deploy-cloudrun@v3
  with:
    service: ${{ env.SERVICE_NAME }}
    region: ${{ env.GCP_REGION }}
    image: ${{ env.REGISTRY }}/${{ env.GCP_PROJECT_ID }}/${{ env.SERVICE_NAME }}:${{ github.sha }}
    flags: |
      --memory=2Gi
      --allow-unauthenticated
      --set-env-vars=CORS_ORIGINS=https://kinemotion.vercel.app,JSON_LOGS=true,LOG_LEVEL=INFO
      --set-secrets=SUPABASE_URL=SUPABASE_URL:latest,SUPABASE_ANON_KEY=SUPABASE_ANON_KEY:latest
```

---

## Step 6: Test Locally

### Start Backend

```bash
cd backend
source .env  # Load environment variables
uv run uvicorn kinemotion_backend.app:app --reload
```

### Start Frontend

```bash
cd frontend
yarn dev
```

### Test Authentication Flow

1. Open `http://localhost:5173`
2. Click "Sign Up"
3. Enter email and password
4. Check email for confirmation link
5. Click confirmation link
6. Sign in with credentials
7. Upload a video to test authenticated API call

---

## Step 7: Deploy to Production

### Deploy Backend

```bash
git add .
git commit -m "feat: add Supabase authentication"
git push origin main
```

GitHub Actions will automatically:
- Run tests
- Build Docker image
- Deploy to Cloud Run
- Configure with Supabase secrets

### Deploy Frontend

```bash
cd frontend
git push origin main
```

Vercel will automatically:
- Build React app with Vite
- Deploy to production
- Use environment variables

---

## Verification

### Check Logs (Backend)

All requests will now include user information:

```json
{
  "event": "request_started",
  "request_id": "abc123...",
  "user_id": "a1b2c3d4-e5f6...",
  "user_email": "coach@example.com",
  "method": "POST",
  "path": "/api/analyze"
}
```

### Test API Authentication

```bash
# Get token from browser console after sign in
# (Run in browser console: supabase.auth.getSession())

curl -X POST https://kinemotion-backend-xxx.run.app/api/analyze \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -F "file=@video.mp4" \
  -F "jump_type=cmj"
```

---

## Troubleshooting

### "Invalid token" errors

**Cause:** Token expired or verification failed

**Fix:**
1. Tokens expire after 1 hour - sign in again
2. Check browser console for auth errors
3. Verify `SUPABASE_URL` is correct in backend env

### "JWKS verification failed" in logs

**Cause:** Project uses HS256 signing (legacy)

**This is normal!** The backend automatically falls back to Auth server verification.

**Fix (optional):**
- Set `SUPABASE_ANON_KEY` for faster fallback verification
- Or migrate to asymmetric keys: Supabase Dashboard → **Settings** → **JWT signing keys** → Click "Migrate JWT secret"

### "CORS error" from API

**Cause:** Backend not allowing frontend domain

**Fix:**
1. Verify `CORS_ORIGINS` includes your Vercel domain
2. Redeploy backend with correct environment variable

### Email confirmation not working

**Cause:** Supabase email settings

**Fix:**
1. Supabase Dashboard → Authentication → Email Templates
2. Verify "Confirm signup" template is enabled
3. Check spam folder for confirmation email
4. For development, check Supabase logs for email delivery status

### Backend not validating tokens

**Cause:** Missing `SUPABASE_URL` environment variable

**Fix:**
1. Check Cloud Run logs: `gcloud logging read --limit 50`
2. Look for "supabase_auth_not_configured" warning
3. Verify `SUPABASE_URL` secret is set in Google Secret Manager
4. Redeploy with correct secret configuration

### Tokens verified but user info empty

**Cause:** Auth server fallback returns minimal data

**Fix:**
1. This is normal for HS256 projects using fallback
2. `user_id` (sub) and `email` are always extracted
3. For full token claims, migrate to RS256 signing

---

## Security Notes

1. **Never commit secrets to Git**
   - Use `.env.local` (gitignored) for local development
   - Use Secret Manager for production

2. **RS256 vs HS256 Security**
   - **RS256 (recommended):** Uses public/private key pairs. Public key can't forge tokens.
   - **HS256 (legacy):** Uses shared secret. Anyone with the secret can forge tokens.
   - Supabase recommends RS256 for all new projects.

3. **Rate limiting**
   - Backend has rate limiting (3 requests/minute per IP)
   - Supabase free tier: 50,000 MAUs

4. **User data**
   - User emails are logged (for audit trail)
   - Consider privacy regulations (GDPR, CCPA)
   - Add privacy policy if collecting user data

5. **Token verification**
   - Tokens are verified via Supabase JWKS endpoint (RS256)
   - Fallback to Auth server verification (HS256)
   - Never verify tokens using JWT secret directly (deprecated)

---

## Free Tier Limits

**Supabase Free Tier:**
- ✅ 50,000 monthly active users
- ✅ 500 MB database storage
- ✅ 2 GB bandwidth
- ✅ Unlimited API requests
- ✅ Social OAuth providers

**Cost after free tier:**
- Pro plan: $25/month (includes 100,000 MAUs)
- Additional MAUs: $0.00325 per MAU

---

## Next Steps

- [ ] Add email templates customization
- [ ] Enable password reset flow
- [ ] Add social OAuth (Google, GitHub)
- [ ] Implement role-based access control
- [ ] Add user profile management

---

## Support

- **Supabase Docs:** https://supabase.com/docs
- **Supabase Community:** https://github.com/supabase/supabase/discussions
- **Kinemotion Issues:** https://github.com/feniix/kinemotion/issues
