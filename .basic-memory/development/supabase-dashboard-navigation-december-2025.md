---
title: Supabase Dashboard Navigation December 2025
type: note
permalink: development/supabase-dashboard-navigation-december-2025
tags:
- supabase
- authentication
- dashboard
- december-2025
---

# Supabase Dashboard Navigation (December 2025)

## Project Creation
- **URL**: [database.new](https://database.new) - Official shortcut for creating new projects
- New projects use ES256 (Elliptic Curve) signing by default

## API Keys Location
- **Path**: Settings → API Keys
- **Publishable key**: New terminology for "anon key" (safe for frontend)
- **Secret key**: Server-side only (replaces service_role)

## JWT Signing Keys
- **Path**: Settings → JWT signing keys
- Shows current signing algorithm (ES256, RS256, or HS256)
- "Migrate JWT secret" button for legacy projects

## URL Configuration
- **Path**: Authentication → URL Configuration
- Site URL: Default redirect after auth
- Redirect URLs: Support wildcards like `https://example.com/**`

## Environment Variables (React/Vite)
```
VITE_SUPABASE_URL=https://project-id.supabase.co
VITE_SUPABASE_ANON_KEY=eyJ...  # or VITE_SUPABASE_PUBLISHABLE_KEY
```

## JWKS Endpoint
- **URL**: `https://project-id.supabase.co/auth/v1/.well-known/jwks.json`
- Returns public keys for asymmetric (ES256/RS256) projects
- Returns empty `{"keys":[]}` for HS256 legacy projects

## References
- [React Quickstart](https://supabase.com/docs/guides/getting-started/quickstarts/reactjs)
- [JWT Signing Keys](https://supabase.com/docs/guides/auth/signing-keys)
- [Redirect URLs](https://supabase.com/docs/guides/auth/redirect-urls)
