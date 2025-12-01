# Backend CORS Configuration - FastAPI Middleware Order

## Critical Architecture Detail

**File:** `backend/src/kinemotion_backend/app.py`

### Middleware Order Matters (LIFO)

FastAPI processes middleware in **LIFO (Last In, First Out)** order:
- Middleware added FIRST → Runs LAST (wraps all other middleware)
- Middleware added LAST → Runs FIRST (innermost handler)

### Correct Configuration

```python
# Line 163-228 in app.py

app = FastAPI(
    title="Kinemotion Backend API",
    description="Video-based kinematic analysis API for athletic performance",
    version="0.1.0",
)

# ========== CORS Configuration (added FIRST for correct middleware order) ==========

cors_origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:8080",
    "http://localhost:8888",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:8080",
    "http://127.0.0.1:8888",
]

# Add production origins from environment variable
cors_origins_env = os.getenv("CORS_ORIGINS", "").strip()
if cors_origins_env:
    prod_origins = [origin.strip() for origin in cors_origins_env.split(",")]
    cors_origins.extend(prod_origins)

# Add CORS middleware FIRST so it wraps all other middleware (LIFO order)
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=[
        "Accept",
        "Accept-Language",
        "Content-Language",
        "Content-Type",
        "Authorization",
    ],
)

# ========== Rate Limiting Configuration ==========
# This is added AFTER CORS, so it runs BEFORE CORS in the request chain
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
```

### Why This Order Is Critical

**Request Flow (with correct order):**
```
Request → CORS Middleware → Rate Limiter → Endpoint Handler
                ↑                 ↓
         Wraps response    May throw 503
```

If rate limiter throws 503, CORS middleware still wraps it → **503 WITH CORS headers**

**Wrong Order (CORS added after rate limiter):**
```
Request → Rate Limiter → CORS Middleware → Endpoint Handler
              ↓              (never reached)
         Throws 503
```

If rate limiter throws 503, it returns immediately → **503 WITHOUT CORS headers** → Browser CORS error

### Environment Variable Configuration

**Production CORS origins set via environment variable:**

```bash
# Cloud Run deployment
CORS_ORIGINS=https://kinemotion.vercel.app,https://other-domain.com
```

**Important:** The code strips whitespace from each origin, so these are equivalent:
- `https://a.com,https://b.com`
- `https://a.com, https://b.com` (with spaces after comma)

### Testing CORS Configuration

```bash
# Test OPTIONS preflight
curl -X OPTIONS https://backend-url/api/analyze \
  -H "Origin: https://kinemotion.vercel.app" \
  -H "Access-Control-Request-Method: POST" \
  -v 2>&1 | grep access-control

# Should show:
# access-control-allow-origin: https://kinemotion.vercel.app
# access-control-allow-methods: GET, POST, OPTIONS
```

### Related Files

- **CORS configuration:** `backend/src/kinemotion_backend/app.py:169-228`
- **Rate limiter decorator:** `backend/src/kinemotion_backend/app.py:326` (`@limiter.limit("3/minute")`)
- **Environment variable parsing:** `backend/src/kinemotion_backend/app.py:181-185`

### Common Gotchas

1. **Never add CORS after rate limiter** - it won't wrap rate limit errors
2. **Always strip whitespace** from env var - spaces after commas are common
3. **Use allow_credentials=False** - allows wildcard headers, simpler CORS
4. **Explicitly list allowed headers** - more secure than `["*"]`
