## MVP Roadmap & Current Priorities

### Phase 1: MVP Validation (IN PROGRESS)
**Goal**: Get product in coaches' hands, gather market feedback

**Completed**
- ✅ CLI analysis (Drop Jump & CMJ) - v0.34.0 stable
- ✅ Backend API scaffolding - v0.1.0 deployed
- ✅ Frontend UI scaffolding - v0.1.0 deployed
- ✅ Supabase integration - auth + storage
- ✅ Cloud Run deployment - production-ready
- ✅ Security hardening - least-privilege service accounts

**In Progress**
- 🚀 Frontend → Backend integration (video upload pipeline)
- 🚀 Results display in UI
- 🚀 End-to-end testing

**Blockers**
- None currently - deployment working as of Dec 2, 2025

**Next Immediate Tasks** (Priority Order)
1. **[HIGH]** Connect frontend upload to backend API
   - Create `/analyze` endpoint in FastAPI
   - Hook upload form to endpoint
   - Test video → analysis → results flow

2. **[HIGH]** Display results in frontend
   - Receive metrics from backend
   - Show in React components (metrics, charts)
   - Export to PDF/CSV

3. **[MEDIUM]** Create end-to-end tests
   - Frontend upload → Backend processing → Database storage → Results display
   - Verify metrics accuracy
   - Performance testing

4. **[MEDIUM]** Frontend deployment automation
   - Add GitHub Actions workflow for Vercel auto-deploy
   - Parallel with manual Vercel setup

5. **[MEDIUM]** API Documentation
   - Add OpenAPI/Swagger to FastAPI
   - Document all endpoints
   - Example requests/responses

6. **[LOW]** Video size/format validation
   - Client-side validation in frontend
   - Server-side validation in backend
   - Graceful error messages

### Phase 2: Market-Driven Development (Week 4+)
**Goal**: Build features customers actually want

**Completed in Phase 1**
- ✅ Frontend i18n (English, Spanish, French) - 86+ translation keys, 5 components with tests

**Deferred to Phase 2**
- ⏳ Backend i18n - error messages, response messages (English-only acceptable for MVP; coach feedback will inform priority)

**Candidates** (based on coach feedback, currently blocked by MVP completion)
- Real-Time Analysis (if coaches want live feedback)
- Running Gait Analysis (if runners/coaches ask for it)
- API & Integrations (if partners request them)
- Batch Processing UI (if coaches upload multiple videos)

### Current State Summary

| Feature | Status | Owner | Effort |
|---------|--------|-------|--------|
| CLI Drop Jump | ✅ Complete | Done | - |
| CLI CMJ | ✅ Complete | Done | - |
| Backend API | 🚀 In Progress | TBD | 2-3 days |
| Frontend UI | 🚀 In Progress | TBD | 2-3 days |
| Integration | ⏳ Planned | TBD | 1-2 days |
| Testing | ⏳ Planned | TBD | 2-3 days |
| Deployment | ✅ Ready | Done | - |

### Resource Allocation

**Critical Path**
1. Backend API endpoints (video upload, analysis, results)
2. Frontend video upload component
3. Integration testing
4. Results display UI

**Parallel Tracks**
- Documentation (can happen anytime)
- Frontend deployment automation (lower priority)
- Performance optimization (can happen later)

### Risk Assessment

**HIGH RISK**
- None identified - deployment working, team can iterate rapidly

**MEDIUM RISK**
- Video processing timeout (Cloud Run 60-min limit) - monitor during testing
- Supabase connection issues - have fallback (local processing)
- Frontend auth issues - test end-to-end authentication

**LOW RISK**
- Documentation gaps - won't block MVP
- Manual Vercel deploys - acceptable workaround

### Success Criteria for MVP

1. ✅ Deployment pipeline working (DONE)
2. ⏳ Video → Backend analysis → Results display (IN PROGRESS)
3. ⏳ End-to-end test passes (PLANNED)
4. ⏳ Real metrics shown in UI (PLANNED)
5. ⏳ Export functionality (PLANNED)
6. ⏳ Error handling user-friendly (PLANNED)

### Feedback Collection Plan

Once MVP is ready (Phases 1-5 complete):
- Invite 3-5 coaches to test
- Collect feedback on:
  - Usability
  - Accuracy of metrics
  - Missing features
  - Pain points
- Record session videos (if permitted)
- Iterate based on feedback

### Decision Gates

**Phase 1 → Phase 2 Gate**
- MVP complete (all success criteria met)
- Coach feedback collected from 3+ testers
- No critical bugs in production
- Decision: Continue, pivot, or stop development

### Related Documentation

- Strategic direction: `.basic-memory/strategy/mvp-first-strategic-direction`
- Validation checkpoints: `.basic-memory/strategy/mvp-validation-checkpoints`
- Feedback plan: `.basic-memory/strategy/mvp-feedback-collection-plan`
- Current state: `.basic-memory/project-management/project-state-summary-december-2025`

---
**Last Updated**: 2025-12-02
**Next Review**: After MVP integration complete
