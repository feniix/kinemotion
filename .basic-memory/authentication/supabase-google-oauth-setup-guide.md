---
title: Supabase Google OAuth Setup Guide
type: note
permalink: authentication/supabase-google-oauth-setup-guide-1
---

# Supabase Google OAuth Setup Guide

## Overview
This guide explains how to enable Google OAuth authentication in Supabase, allowing users to sign in with their Google accounts.

## Step 1: Configure Google Cloud Console

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Navigate to **APIs & Services** → **Credentials**
4. Click **Create Credentials** → **OAuth client ID**
5. If prompted, configure the OAuth consent screen:
   - Choose **External** (unless you have a Google Workspace)
   - Fill in app name, support email, developer contact
   - Add scopes: `email`, `profile`, `openid`
   - Add test users if needed (for testing before verification)
6. Create OAuth client:
   - **Application type**: Web application
   - **Name**: Kinemotion (or your app name)
   - **Authorized JavaScript origins**:
     - `https://kinemotion.vercel.app` (production)
     - `http://localhost:5173` (local development)
   - **Authorized redirect URIs**:
     - Get from Supabase Dashboard → Authentication → Providers → Google
     - Format: `https://<project-id>.supabase.co/auth/v1/callback`
     - For local dev: `http://localhost:3000/auth/v1/callback` (if using Supabase local)
7. Click **Create** and save:
   - **Client ID** (looks like: `123456789-abc...googleusercontent.com`)
   - **Client Secret** (looks like: `GOCSPX-abc...`)

## Step 2: Configure Supabase Dashboard

1. Go to your Supabase project dashboard
2. Navigate to **Authentication** → **Providers**
3. Find **Google** in the list and click to configure
4. Enable the provider
5. Enter:
   - **Client ID**: From Google Cloud Console
   - **Client Secret**: From Google Cloud Console
6. Click **Save**

**Important**: The redirect URI in Google Cloud Console must match:
- Production: `https://<your-project-id>.supabase.co/auth/v1/callback`
- Local dev: `http://localhost:3000/auth/v1/callback` (if using Supabase local)

## Step 3: Update Frontend Code

### Add Google Sign-In Button

Update `frontend/src/components/Auth.tsx` to include a Google sign-in button.

### Update useAuth Hook

Add `signInWithGoogle()` method to `frontend/src/hooks/useAuth.ts`:

```typescript
signInWithGoogle: () => Promise<void>
```

Implementation uses `supabase.auth.signInWithOAuth({ provider: 'google' })`.

## Step 4: Update Redirect URLs

Ensure your Supabase project has the correct redirect URLs configured:

1. Go to **Authentication** → **URL Configuration**
2. **Site URL**: `https://kinemotion.vercel.app`
3. **Redirect URLs**:
   - `https://kinemotion.vercel.app/**`
   - `http://localhost:5173/**`

## Testing

1. Start your frontend: `cd frontend && yarn dev`
2. Click "Sign in with Google"
3. You should be redirected to Google's OAuth consent screen
4. After authorization, you'll be redirected back to your app
5. Check Supabase Dashboard → Authentication → Users to see the new user

## Troubleshooting

**Error: "redirect_uri_mismatch"**
- Ensure the redirect URI in Google Cloud Console exactly matches Supabase callback URL
- Check for trailing slashes or protocol mismatches (http vs https)

**Error: "invalid_client"**
- Verify Client ID and Client Secret are correct in Supabase Dashboard
- Ensure Google OAuth consent screen is configured

**User not appearing in Supabase**
- Check browser console for errors
- Verify redirect URLs are configured correctly
- Check Supabase logs in Dashboard → Logs → Auth Logs

## Security Notes

- Never commit Client Secret to git
- Use environment variables for sensitive values
- Google OAuth tokens are handled by Supabase automatically
- JWT tokens from Supabase work the same way for Google-authenticated users

## Free Tier Limits

- Google OAuth: No additional cost
- Supabase Auth: 50,000 MAUs/month (free tier)
- Each Google sign-in counts as one MAU

## References

- [Supabase Google OAuth Docs](https://supabase.com/docs/guides/auth/social-login/auth-google)
- [Google Cloud Console](https://console.cloud.google.com/)
- [Supabase Dashboard](https://supabase.com/dashboard)
