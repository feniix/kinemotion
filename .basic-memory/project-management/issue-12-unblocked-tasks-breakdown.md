---
title: Issue
type: note
permalink: project-management/issue-12-unblocked-tasks-breakdown-1
tags:
- issue-12
- web-ui
- unblocked
- scaffolding
---

# Issue #12: Unblocked Tasks Breakdown

## Current Status
✅ **UNBLOCKED FOR SCAFFOLDING** - Backend/frontend skeleton + deployment can start NOW

While full E2E integration requires #10 + #11, most infrastructure work is independent.

**Total MVP Cost:** $0 (Fly.io free + Vercel free + Cloudflare R2 free)

---

## Phase 0: Infrastructure & Scaffolding (CAN START NOW)

### Backend Scaffolding (2 days)
- Create FastAPI app structure (`src/kinemotion_backend/app.py`)
- Health check endpoint: `GET /health`
- Analysis endpoint: `POST /api/analyze` (returns REAL metrics)
- File upload handler (upload to R2, validate, process immediately)
- CORS configuration
- Error response wrapper

### Frontend Scaffolding (2 days)
- Create React app with Vite + TypeScript
- Component structure: UploadForm, ResultsDisplay, ErrorDisplay, LoadingSpinner
- Mobile responsive styling
- Real metric display (not mocked)

### Deployment Infrastructure (1 day)
- Dockerfile with Python 3.12 + MediaPipe
- fly.toml for Fly.io
- vercel.json for Vercel
- Environment variable setup templates

### Phase 0 Success Criteria
✅ Both apps scaffold with clean directory structure
✅ Backend health check works locally
✅ Frontend displays real metrics (not mocked)
✅ Both deploy successfully
✅ Ready for coach recruitment

---

## Why It's Unblocked

✅ Uses **current kinemotion implementation** (real metrics, not mocked)
✅ **No dependency on #10 or #11**
✅ Metrics refinement (when #10 done) = just update library version
✅ **Phase 0 is fully independent from blocking issues**

---

## Architecture

```
Coach uploads video
    ↓
Frontend (Vercel) ──POST /api/analyze──→ Backend (Fly.io)
    ↑                                        ↓
    │                                    Process video
    └─────── Display metrics ──────────── Return real metrics
```

---

## Tech Stack

- **Backend:** FastAPI + Python 3.12 + uv
- **Frontend:** React + TypeScript + Vite + Yarn
- **Hosting:** Fly.io (backend) + Vercel (frontend)
- **Storage:** Cloudflare R2 (optional)
- **Total Cost:** $0 for MVP

---

## Next Steps

1. Create backend + frontend scaffolding
2. Deploy to Fly.io + Vercel
3. Recruit coaches for testing
4. Gather feedback
5. When #10 done: update metrics (1 version bump)
