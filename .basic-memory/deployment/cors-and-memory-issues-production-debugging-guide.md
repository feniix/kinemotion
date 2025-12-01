---
title: CORS and Memory Issues - Production Debugging Guide
type: note
permalink: deployment/cors-and-memory-issues-production-debugging-guide-1
tags:
- cors
- debugging
- memory
- cloud-run
- vercel
- troubleshooting
- mediaπpe
---

# CORS and Memory Issues - Production Debugging Guide

## The CORS + 503 Mystery (Solved)

### Symptom
```
Browser Console:
Access to XMLHttpRequest blocked by CORS policy:
No 'Access-Control-Allow-Origin' header present
Status: 503 Service Unavailable
```

**But:**
- ✅ curl tests show CORS headers ARE present
- ✅ OPTIONS preflight succeeds
- ✅ Backend `/health` endpoint works
- ❌ POST requests with file uploads fail

### Root Cause

**Cloud Run container ran out of memory** (512MB → 556MB used during video processing). When the container exceeds memory:

1. Cloud Run's infrastructure **kills the container mid-request**
2. Returns a **503 from "Google Frontend"** (not your app)
3. The 503 response is **plain-text, no CORS headers** (because your app never ran)
4. Browser sees 503 without CORS headers → **CORS error**

### Why It Was Confusing

| Test Type | Result | Why |
|-----------|--------|-----|
| curl OPTIONS | ✅ 200 with CORS headers | Tiny request, doesn't load MediaPipe models |
| curl POST (empty) | ✅ 422 validation error | Validation happens before video processing |
| Browser POST (video) | ❌ 503 no CORS | Video processing loads MediaPipe → OOM crash |
| curl POST (video) | ❌ Timeout/503 | Same OOM crash, but curl shows different error |

### The Fix

```bash
gcloud run services update kinemotion-backend \
  --region us-central1 \
  --memory 2Gi
```

**Why 2GB:**
- Python runtime: ~100MB
- MediaPipe models: ~500MB
- Video processing buffers: ~300MB
- NumPy arrays: ~200MB
- Safety margin: ~900MB
- **Total headroom:** Handles concurrent requests + large videos

---

## CORS Configuration Deep Dive

### FastAPI Middleware Order (Critical!)

**Problem:** FastAPI middleware is **LIFO** (Last In, First Out). If CORS is added AFTER other middleware, it won't wrap error responses.

**Wrong (CORS doesn't wrap rate limiter errors):**
```python
app = FastAPI(...)

limiter = Limiter(...)  # Added first
app.state.limiter = limiter

app.add_middleware(CORSMiddleware, ...)  # Added last → runs first
```

**Correct (CORS wraps everything):**
```python
app = FastAPI(...)

# Add CORS FIRST (runs last, wraps all responses)
app.add_middleware(CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Accept", "Content-Type", ...],
)

# Then configure other middleware
limiter = Limiter(...)  # Added after → runs before CORS
```

### Environment Variable Parsing

**Problem:** Special characters in env vars can break gcloud parsing

**Wrong:**
```bash
# Comma gets parsed as separator
gcloud run deploy --set-env-vars CORS_ORIGINS=https://a.com,https://b.com
# Error: Bad syntax for dict arg
```

**Correct - Use env-vars-file:**
```bash
# Create env.yaml
cat > env.yaml <<EOF
CORS_ORIGINS: "https://a.com,https://b.com,https://c.com"
EOF

# Deploy with file
gcloud run deploy kinemotion-backend \
  --region us-central1 \
  --env-vars-file env.yaml
```

### Backend CORS Origins List

```python
cors_origins = [
    "http://localhost:3000",
    "http://localhost:5173",    # Vite dev server
    "http://localhost:8080",
    "http://localhost:8888",    # Test server
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:8080",
    "http://127.0.0.1:8888",
]

# Add production from env var
cors_origins_env = os.getenv("CORS_ORIGINS", "").strip()
if cors_origins_env:
    prod_origins = [origin.strip() for origin in cors_origins_env.split(",")]
    cors_origins.extend(prod_origins)
```

**Strips whitespace** to handle `"https://a.com, https://b.com"` (with spaces)

---

## Debugging Workflow

### Step 1: Verify Backend is Running

```bash
# Health check
curl https://kinemotion-backend-1008251132682.us-central1.run.app/health

# Expected:
# {"status":"ok","service":"kinemotion-backend","version":"0.1.0",...}
```

### Step 2: Test CORS Preflight

```bash
curl -v -X OPTIONS https://backend-url/api/analyze \
  -H "Origin: https://kinemotion.vercel.app" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: content-type" 2>&1 | grep access-control

# Expected:
# < access-control-allow-origin: https://kinemotion.vercel.app
# < access-control-allow-methods: GET, POST, OPTIONS
# < access-control-allow-headers: ...
```

### Step 3: Test Actual POST (Without Video)

```bash
curl -X POST https://backend-url/api/analyze \
  -H "Origin: https://kinemotion.vercel.app" \
  -F "jump_type=cmj" \
  -F "quality=balanced"

# Expected: 422 validation error (file missing)
# {"detail":[{"type":"missing","loc":["body","file"],"msg":"Field required"}]}
```

If this fails with 503 or no CORS headers → **memory issue** or middleware order issue.

### Step 4: Check Cloud Run Logs

```bash
gcloud logging read \
  "resource.type=cloud_run_revision AND resource.labels.service_name=kinemotion-backend" \
  --limit 50 \
  --format json \
  --freshness=5m | python3 -c "import sys,json; logs=json.load(sys.stdin); [print(f\"{l.get('timestamp','')}: {l.get('textPayload','')}\") for l in logs]"

# Look for:
# - "Memory limit exceeded"
# - "container instance was found to be using too much memory and was terminated"
# - 503 errors
```

### Step 5: Create Local Test Page

**Bypasses Vercel to isolate backend issues:**

```html
<!-- test.html -->
<!DOCTYPE html>
<html>
<body>
    <input type="file" id="video">
    <button onclick="upload()">Upload</button>
    <pre id="result"></pre>
    <script>
        async function upload() {
            const formData = new FormData();
            formData.append('file', document.getElementById('video').files[0]);
            formData.append('jump_type', 'cmj');

            try {
                const res = await fetch('https://backend-url/api/analyze', {
                    method: 'POST',
                    body: formData
                });
                const data = await res.json();
                document.getElementById('result').textContent = JSON.stringify(data, null, 2);
            } catch (err) {
                document.getElementById('result').textContent = err.message;
            }
        }
    </script>
</body>
</html>
```

**Serve locally:**
```bash
cd frontend
python3 -m http.server 8888
# Open http://localhost:8888/test.html
```

If this works but Vercel doesn't → Vercel caching or env var issue.

---

## Memory Profiling

### Check Current Memory Usage

```bash
# Get service configuration
gcloud run services describe kinemotion-backend \
  --region us-central1 \
  --format='value(spec.template.spec.containers[0].resources.limits.memory)'

# Should output: 2Gi
```

### Monitor Memory in Real-Time

```bash
# Stream logs (watch for memory warnings)
gcloud logging read \
  "resource.labels.service_name=kinemotion-backend AND textPayload=~'Memory'" \
  --limit 20 \
  --format json \
  --freshness=10m
```

### Memory Usage Patterns

**From Cloud Run logs analysis:**
- **Idle startup:** ~100MB (Python + uvicorn)
- **First request:** ~500MB spike (MediaPipe model loading)
- **Processing 1080p video:** ~600-800MB
- **Peak during processing:** ~1.2GB (large video + NumPy arrays)

**Why 512MB failed:**
- Base: 100MB
- MediaPipe: 500MB
- Processing: 200MB
- **Total:** 800MB → **exceeds 512MB limit**

---

## Vite Environment Variables

### How They Work

Vite replaces `import.meta.env.VITE_*` at **build time**, not runtime:

```typescript
// In code:
const apiUrl = import.meta.env.VITE_API_URL || ''

// After build (if VITE_API_URL=https://backend.com):
const apiUrl = "https://backend.com" || ''
```

**Critical:** Environment variables are **baked into the JavaScript bundle** during `yarn build`. Changing env vars requires redeployment.

### Vercel Environment Variables

**Set in Dashboard:**
1. Project → Settings → Environment Variables
2. Add `VITE_API_URL` for Production
3. **Must redeploy** for it to take effect

**Verify it's embedded:**
```bash
# Check if backend URL is in the JavaScript bundle
curl -s https://kinemotion.vercel.app/ | grep -o 'kinemotion-backend'

# Should return: kinemotion-backend-1008251132682
```

If no match → env var wasn't set before build, or Vercel is serving cached version.

---

## Production URLs

**Frontend:** https://kinemotion.vercel.app/
**Backend:** https://kinemotion-backend-1008251132682.us-central1.run.app

**Environment Variables:**
- **Vercel:** `VITE_API_URL=https://kinemotion-backend-1008251132682.us-central1.run.app`
- **Cloud Run:** `CORS_ORIGINS=https://kinemotion.vercel.app`

**Configuration:**
- **Cloud Run Memory:** 2Gi (required for MediaPipe)
- **Cloud Run Region:** us-central1 (Tier 1 pricing)
- **Vercel Root Directory:** `frontend/`
- **Vercel Framework:** Vite (auto-detected)

---

## Lessons Learned

1. **Always check Cloud Run logs first** when debugging CORS + 503
2. **OOM crashes return 503 without CORS headers** (infrastructure-level error)
3. **CORS middleware must be added FIRST** in FastAPI (LIFO order)
4. **Vite env vars are build-time**, not runtime (must redeploy after changes)
5. **Use env-vars-file for complex values** (commas, special chars)
6. **512MB is too low for MediaPipe** (need minimum 2GB)
7. **Local test page** is fastest way to isolate backend issues
