---
title: Kinemotion Supabase Production Configuration
type: note
permalink: project-management/kinemotion-supabase-production-configuration-1
tags:
- supabase
- production
- credentials
- kinemotion
---

## Kinemotion Supabase Production Configuration

**Project ID**: smutfsalcbnfveqijttb

### Credentials
- **URL**: https://smutfsalcbnfveqijttb.supabase.co
- **Publishable Key**: `sb_publishable_WMMkJVB5hpNdZlyWykxDRg_uvW1lqPN`

### Deployment URLs
- **Frontend**: https://kinemotion.vercel.app
- **Backend**: https://kinemotion-backend-1008251132682.us-central1.run.app

### Dashboard Links
- Main: https://supabase.com/dashboard/project/smutfsalcbnfveqijttb
- API Keys: https://supabase.com/dashboard/project/smutfsalcbnfveqijttb/settings/api
- JWT Settings: https://supabase.com/dashboard/project/smutfsalcbnfveqijttb/settings/jwt
- URL Config: https://supabase.com/dashboard/project/smutfsalcbnfveqijttb/auth/url-configuration

### Setup Scripts
- Local: `./scripts/setup-supabase-local.sh`
- Production: `./scripts/setup-supabase-production.sh`

### Current Status
- JWT Signing: Legacy HS256 (needs migration to ES256)
- Backend: Supports both HS256 and ES256 automatically

### Migration Steps
1. Go to JWT Settings (link above)
2. Click "Migrate JWT secret"
3. Wait 5 minutes
4. Click "Rotate keys"
