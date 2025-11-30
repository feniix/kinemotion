---
title: Deployment Decision Analysis for Kinemotion
type: note
permalink: strategy/deployment-decision-analysis-for-kinemotion-1
tags:
- deployment
- strategy
- google-cloud-run
- vercel
---

# Deployment Decision: Google Cloud Run

## Decision
**Deploy Kinemotion backend to Google Cloud Run + Vercel frontend**

## Why Cloud Run

### Platform Requirements Met
- ✅ Long-running tasks: Up to 24h timeout (need 60-120 seconds per video)
- ✅ Stateless architecture: Perfect for horizontal scaling
- ✅ Free tier: 2M requests/month free (MVP uses ~3k requests/month)
- ✅ Cost: Essentially $0-5/month for MVP traffic
- ✅ No spindowns: Unlike Render (15min spindown kills 60+ sec requests)
- ✅ No credit exhaustion: Unlike Railway ($5 credit, then must pay)
- ✅ Fast deployment: Docker support already in place

### MVP Timeline Fit
- Deploy this week (before 3-week coach validation window)
- No infrastructure complexity
- Auto-scaling for reliability
- Pay-per-use (transparent costs)

### Architecture
```
Browser → Vercel Frontend (kinemotion-mvp.vercel.app)
               ↓
         VITE_API_URL env var
               ↓
         Google Cloud Run Backend
         (kinemotion-backend-REGION)
```

### Platform Comparison Results

| Platform | Free Tier | Long Tasks | Spindown | Cost/Month |
|----------|-----------|-----------|----------|-----------|
| **Cloud Run** | ✅ 2M requests | ✅ 24h | ❌ No | ~$0-5 |
| Railway | ✅ $5 credit | ✅ Unlimited | ✅ After credit | $0 then paid |
| Render | ✅ Always-on | ❌ 15min limit | ✅ After 15min inactivity | $0 |
| Fly.io | ❌ Paid only | ✅ Unlimited | ❌ No | $5-10+ |

### Cost Breakdown (MVP: 100 videos/day)
- Requests: 3,000/month → Free tier covers all
- vCPU-seconds: 360,000/month (120s per video)
  - Free: 180,000/month
  - Overage: 180,000 @ $0.000024/sec = $4.32
- Storage: Minimal (temp processing only)
- **Total: ~$4-5/month**

## Next Steps
1. Create Google Cloud project
2. Set up Cloud Run service (Docker)
3. Deploy backend
4. Set VITE_API_URL in Vercel
5. Test end-to-end with coaches
