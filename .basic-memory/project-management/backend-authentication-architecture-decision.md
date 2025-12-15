---
title: Backend Authentication Architecture Decision
type: note
permalink: project-management/backend-authentication-architecture-decision
---

# Authentication Architecture Options for /analyze Endpoint

## Current State
- `/analyze` endpoint: **Public (no auth)** → files saved as `anonymous`
- `/api/analysis/sessions` endpoint: **Requires auth** → 401 errors until SUPABASE_PUBLISHABLE_KEY was set
- Issue: User IDs never passed to storage, so no user organization in R2

## Option A: Add Authentication to /analyze
Require JWT token for video analysis upload

### Pros
- User uploads immediately organized by user ID in R2 (no "anonymous" folder clutter)
- Single consistent auth model across entire backend
- Session ID returned from analysis is tied to authenticated user
- Easier user management and analytics (know who uploaded what)
- Prevents abuse (rate limiting per user instead of globally)
- Better for compliance/auditing (track all user actions)

### Cons
- **Breaks existing workflow**: Frontend must authenticate BEFORE uploading video
- Frontend must fetch auth token before making `/analyze` request
- Adds latency to video upload (auth check required)
- API less flexible (can't generate quick demos without login)
- Complicates testing/development (need to authenticate first)
- Reduces discoverability (users must login to try the feature)

---

## Option B: Keep /analyze Public, Return Session ID
Keep video analysis public but return ephemeral session ID that can be claimed by authenticated user

### Pros
- **Zero friction user experience**: Upload video immediately without login
- Users can try the feature without committing to account creation
- Better for demos and marketing
- Faster upload (no auth overhead)
- Reduces initial friction to adoption
- Guests can analyze videos without creating account
- Optional: Can send session to email/link for later claiming

### Cons
- Files stay in `anonymous/` folder (harder to organize)
- Session IDs need TTL (expire after N hours if not claimed)
- Need migration logic to move anonymous sessions to user when they login
- More complex database schema (sessions linked to either user_id or session_id)
- Harder to enforce rate limiting (per IP instead of per user)
- Anonymous sessions could fill up storage
- Audit trail less complete (guest activities not tracked)
- Two different storage paths to manage

---

## Option C: Both (Recommended)
Offer both authenticated AND guest analysis

### Pros
- **Best UX**: Guests can try immediately, authenticated users get benefits
- Maximizes adoption (low barrier to entry)
- Users experience value before creating account
- Authenticated users get proper tracking/organization
- Can implement "upgrade" flow (guest → user)
- Flexible for different use cases (demos, research, production)
- Solves the "try before you buy" problem
- Future monetization: Basic (guest) vs Premium (registered)

### Cons
- **Most complex**: Handle both auth and anonymous sessions
- Two code paths to maintain and test
- Database migration needed (sessions table needs optional user_id)
- Storage organization more complicated (both `anonymous/` and `users/{id}/`)
- Rate limiting needs dual strategy (per-IP for guests, per-user for authenticated)
- More edge cases to handle and debug
- Longer development timeline

---

## Recommendation Context

**For MVP (current goal):**
- Option B (guest-friendly) makes sense if you're trying to get product in coaches' hands quickly
- Coaches can try without friction
- You get immediate feedback on use cases

**For Production (coaches paying):**
- Option C (both) provides best UX
- Coaches get analytics/tracking when they're part of org
- Guests can demonstrate to team before purchasing

**Current Blocker:**
- Fix auth.py to use SUPABASE_PUBLISHABLE_KEY (DONE) ✅
- This unblocks Option A or C immediately
- Option B requires no backend changes (already works)
