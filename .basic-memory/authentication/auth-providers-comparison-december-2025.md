---
title: Auth Providers Comparison December 2025
type: note
permalink: authentication/auth-providers-comparison-december-2025-1
tags:
- authentication
- comparison
- supabase
- clerk
- auth0
---

[{"text": "# Third-Party Auth Providers Comparison (December 2025)\n\n## For Kinemotion (Vercel + Cloud Run)\n\n| Provider | Free MAUs | Vercel | Backend | Best For |\n|----------|-----------|--------|---------|----------|\n| **Clerk** | 10,000 | \u2b50 Native | \u2705 Excellent | MVP Speed |\n| **Supabase** | 50,000 | \u2705 Good | \u2705 Excellent | Long-term Cost |\n| **Auth0** | 25,000 | \u2705 Good | \u2705 Excellent | Enterprise |\n| **Firebase** | 50,000 | \u2705 Good | \u2705 Good | Google ecosystem |\n\n## Decision: Supabase (Chosen)\n\n**Why Supabase:**\n- \u2705 Most generous free tier (50K MAUs)\n- \u2705 Works with `kinemotion.vercel.app` (Clerk doesn't)\n- \u2705 Open source (can self-host)\n- \u2705 Includes Postgres database\n- \u2705 Cheapest long-term ($0.00325/MAU)\n\n## Clerk (Not Chosen - Domain Restriction)\n\n**Clerk Issue (December 2025):**\n- Does NOT allow `*.vercel.app` domains for production\n- Requires custom domain\n- Otherwise: fastest setup, best DX\n\n**Free Tier:** 10,000 MAUs\n**Paid:** $25/month + $0.02/MAU over 10K\n\n## Auth0 (Not Recommended - Expensive)\n\n**Free Tier:** 25,000 MAUs\n**Paid:** $35/month for 500 MAUs, then $0.07/MAU\n**Example:** 10K users = $700/month \ud83d\ude31\n\n## Firebase Auth\n\n**Free Tier:** 50,000 MAUs (email/password/social)\n**Cons:** Google lock-in, phone auth costs extra\n\n## Cost Projection for Kinemotion\n\n**Supabase Pricing:**\n- 0-50K MAUs: $0/month\n- 50K-100K MAUs: $25/month (Pro plan)\n- 100K+ MAUs: $25 + ($0.00325 per additional MAU)\n\n**Estimated usage:**\n- 100 videos/day \u2248 1,000-2,000 MAUs/month\n- **Cost: $0** (well within free tier)\n\n## Implementation Status\n\n\u2705 **Supabase fully integrated** (December 2025)\n- Frontend: React + @supabase/supabase-js\n- Backend: FastAPI + JWT validation\n- Deployment: Vercel + Cloud Run\n- Logging: User ID in all requests", "type": "text"}]
