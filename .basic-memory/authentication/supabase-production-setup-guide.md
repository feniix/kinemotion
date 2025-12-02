---
title: Supabase Production Setup Guide
type: note
permalink: authentication/supabase-production-setup-guide-1
tags:
- supabase
- authentication
- production
- deployment
- configuration
---

# Supabase Production Setup for Kinemotion

## Your Supabase Project

- **Project URL**: https://smutfsalcbnfveqijttb.supabase.co
- **Publishable Key**: `sb_publishable_WMMkJVB5hpNdZlyWykxDRg_uvW1lqPN`
- **Frontend URL**: https://kinemotion.vercel.app

---

## Step 1: Configure Supabase Dashboard

### 1.1 Migrate to Modern JWT Signing Keys (Required)

Your project is using the legacy JWT secret. Let's upgrade to modern asymmetric keys:

1. **Go to JWT Settings**: https://supabase.com/dashboard/project/smutfsalcbnfveqijttb/settings/jwt

2. **Click "Migrate JWT secret"**:
   - This imports your existing JWT secret into the new system
   - Creates a new asymmetric key (ES256) as a standby
   - Takes about 5 minutes

3. **Wait for migration to complete**, then **click "Rotate keys"**:
   - Starts using the new asymmetric key (ES256) for new tokens
   - Existing tokens remain valid (no users are signed out)
   - Migration is seamless!

4. **Done!** Your project now uses modern asymmetric keys (ES256)

> **Why this matters**: ES256 provides better performance (no Auth server in hot path), better security (public/private keys), and better reliability. This is the modern standard for JWT signing.

### 1.2 Configure URL Configuration

1. **Direct link**: https://supabase.com/dashboard/project/smutfsalcbnfveqijttb/auth/url-configuration

2. Set the following:
   - **Site URL**: `https://kinemotion.vercel.app`
   - **Redirect URLs**:
     - `https://kinemotion.vercel.app/**`
     - `http://localhost:5173/**`

### 1.3 Verify Email Provider

1. **Navigate**: **Authentication** → **Providers**
2. Ensure **Email** is enabled (should be by default)

---

## Step 2: Local Development Setup

Run the setup script:

```bash
./scripts/setup-supabase-local.sh
```

This creates:
- `frontend/.env.local` with your Supabase credentials
- `backend/.env` with your Supabase credentials

### Start Services

**Terminal 1 - Backend:**
```bash
cd backend
uv run uvicorn kinemotion_backend.app:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
yarn dev
```

### Test Locally

1. Open http://localhost:5173
2. Click "Sign Up"
3. Enter email and password
4. Check your email for confirmation link
5. Sign in with your credentials
6. Upload a test video!

---

## Step 3: Production Setup

### 3.1 Configure Google Cloud Secrets

Run the production setup script:

```bash
./scripts/setup-supabase-production.sh
```

This will:
- Create `SUPABASE_URL` and `SUPABASE_ANON_KEY` secrets in Google Secret Manager
- Grant access to the Cloud Run service account

### 3.2 Deploy Backend

The workflow has been updated to use Supabase secrets. Deploy:

```bash
git add .github/workflows/deploy-backend.yml scripts/
git commit -m "feat: configure Supabase authentication for production"
git push origin main
```

GitHub Actions will automatically deploy with Supabase configuration.

### 3.3 Configure Vercel Environment Variables

1. Go to: https://vercel.com/dashboard
2. Select your **kinemotion** project
3. Go to **Settings** → **Environment Variables**
4. Add the following variables (for **Production** environment):

| Variable | Value |
|----------|-------|
| `VITE_SUPABASE_URL` | `https://smutfsalcbnfveqijttb.supabase.co` |
| `VITE_SUPABASE_ANON_KEY` | `sb_publishable_WMMkJVB5hpNdZlyWykxDRg_uvW1lqPN` |
| `VITE_API_URL` | `https://kinemotion-backend-1008251132682.us-central1.run.app` |

> **Note**: `VITE_SUPABASE_ANON_KEY` uses the new `sb_publishable_xxx` format (December 2025). This is safe to use in the frontend.

5. Click **Save** for each variable
6. **Redeploy** the frontend:

```bash
git commit --allow-empty -m "chore: trigger Vercel redeploy with Supabase env vars"
git push origin main
```

---

## Step 4: Verify Production

1. Go to https://kinemotion.vercel.app
2. You should see the authentication screen
3. Sign up with a new account
4. Check email for confirmation
5. Sign in
6. Upload a video to test the full flow!

### Check Backend Logs

View logs to see user authentication working:

```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=kinemotion-backend" \
  --limit 50 \
  --project=kinemotion-backend \
  --format=json | jq '.[] | select(.jsonPayload.user_id) | {timestamp: .timestamp, event: .jsonPayload.event, user_id: .jsonPayload.user_id, user_email: .jsonPayload.user_email}'
```

You should see logs with `user_id` and `user_email` fields!

---

## Troubleshooting

### Local Development Issues

**Issue**: "Missing Supabase environment variables"
- **Fix**: Run `./scripts/setup-supabase-local.sh` again

**Issue**: Email confirmation not working
- **Fix**: Check your spam folder, or check Supabase logs in the dashboard

### Production Issues

**Issue**: "CORS error" in browser console
- **Fix**: Verify CORS_ORIGINS includes `https://kinemotion.vercel.app`

**Issue**: "Invalid token" errors in backend
- **Fix**: Ensure secrets are properly set in Google Secret Manager

**Issue**: Frontend shows old version without auth
- **Fix**: Check Vercel environment variables are set and redeploy

---

## Security Notes

✅ **Good Practices:**
- Publishable key is safe to use in frontend (public)
- Secrets are stored in Google Secret Manager (encrypted)
- Environment variables are not committed to Git

⚠️ **Remember:**
- Never commit `.env` or `.env.local` files
- Rotate keys if accidentally exposed
- Use RLS (Row Level Security) in Supabase for data protection

---

## Next Steps

- [ ] Set up password reset flow
- [ ] Add social OAuth (Google, GitHub)
- [ ] Configure email templates in Supabase
- [ ] Add user profile management
- [ ] Implement role-based access control (coach vs athlete)

---

## Support

- **Supabase Dashboard**: https://supabase.com/dashboard/project/smutfsalcbnfveqijttb
- **Supabase API Keys**: https://supabase.com/dashboard/project/smutfsalcbnfveqijttb/settings/api
- **Supabase Auth Settings**: https://supabase.com/dashboard/project/smutfsalcbnfveqijttb/auth/url-configuration
- **Supabase Docs**: https://supabase.com/docs
- **Kinemotion Docs**: See "Supabase Authentication Technical Guide" note

---

## December 2025 Updates

This guide uses Supabase's **modern approach** (December 2025):
- ✅ **Asymmetric JWT keys (ES256)** - Industry best practice for security & performance
- ✅ New API key format: `sb_publishable_xxx`
- ✅ Direct links to dashboard pages
- ✅ Modern authentication flow with JWKS verification
- ✅ Zero-downtime migration from legacy JWT secret

### Modern vs Legacy

| Aspect | Modern (ES256) | Legacy (HS256) |
|--------|----------------|----------------|
| **Security** | Public/private keys | Shared secret |
| **Performance** | Fast, local verification | Requires Auth server |
| **Compliance** | SOC2, HIPAA friendly | Harder to certify |
| **Revocation** | Automatic via JWKS | Requires redeployment |
| **This Guide** | ✅ **Recommended** | ❌ Deprecated |

**Our implementation**: Backend uses JWKS verification with Auth server fallback for maximum compatibility.
