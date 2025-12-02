---
title: Auth Provider Comparison December 2025
type: note
permalink: authentication/auth-provider-comparison-december-2025-1
tags:
- authentication
- comparison
- supabase
- clerk
- pricing
---

## Auth Provider Comparison (December 2025)

### Chosen: Supabase

**Why:**
- 50,000 MAUs free tier (vs Clerk 10K)
- Works with `kinemotion.vercel.app` (Clerk requires custom domain)
- $0.00325/MAU after free tier (cheapest)
- Open source, includes Postgres
- Excellent Python/FastAPI support

### Clerk (Not Chosen)
**Reason**: Doesn't allow `*.vercel.app` domains for production
- Free: 10,000 MAUs
- Paid: $25/month + $0.02/MAU
- Best DX, fastest setup
- Native Vercel integration

### Auth0 (Not Recommended)
**Reason**: Too expensive
- Free: 25,000 MAUs
- Paid: $35/month + $0.07/MAU (10K users = $700/month!)

### Firebase Auth
- Free: 50,000 MAUs
- Cons: Google lock-in, phone auth costs extra

### Cost Projection (Supabase)
- 0-50K MAUs: $0/month
- 100 videos/day ≈ 1-2K MAUs/month
- **Well within free tier**
