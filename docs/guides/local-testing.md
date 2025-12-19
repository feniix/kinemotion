# Issue #12: Local Testing Guide

This guide shows how to test the complete MVP stack locally before deploying to Google Cloud Run and Vercel.

## Prerequisites

```bash
# Verify Python 3.12+
python --version  # Should show 3.12.x

# Verify uv is installed
uv --version

# Verify Node/Yarn installed
yarn --version
```

## Setup Phase (One-time)

### 1. Backend Setup

```bash
cd backend

# Install dependencies with uv
uv sync

# Create environment file (optional - R2 not needed for local testing)
cp .env.example .env.local

# You can leave R2 variables empty for testing
# They'll gracefully degrade (videos stored temporarily only)
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies with Yarn
yarn install

# Create environment file
cp .env.example .env.local

# Edit .env.local and set:
# VITE_API_URL=http://localhost:8000
nano .env.local  # or your preferred editor
```

## Running Locally (Development)

### Terminal 1: Start Backend

```bash
cd backend

# Start FastAPI development server
uv run uvicorn kinemotion_backend.app:app --reload

# You should see:
# INFO:     Uvicorn running on http://127.0.0.1:8000
# INFO:     Application startup complete
```

**Verify backend is running:**

```bash
curl http://localhost:8000/health

# Should return:
# {
#   "status": "healthy",
#   "service": "Kinemotion Web Backend",
#   "version": "0.1.0",
#   "r2_configured": false,
#   "timestamp": "2024-11-28T..."
# }
```

**API Documentation (optional):**

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Terminal 2: Start Frontend

```bash
cd frontend

# Start Vite development server
yarn dev

# You should see:
# VITE v5.x.x  ready in XXX ms
# ➜  Local:   http://localhost:5173/
# ➜  press h to show help
```

**Open in browser:**

- http://localhost:5173

## Testing the Full Stack

### Test 1: Health Check

```bash
# In a new terminal
curl http://localhost:8000/health

# Expected: 200 status with "healthy" message
```

### Test 2: API Documentation

1. Open http://localhost:8000/docs
1. You should see interactive Swagger UI with endpoints
1. Try `/health` endpoint first to verify it works

### Test 3: Upload a Video (Via Frontend)

1. Open http://localhost:5173 in your browser
1. You should see:
   - File upload input
   - Jump type selector (CMJ / Drop Jump)
   - Analyze button
1. Upload a CMJ or Drop Jump video (\< 500MB)
1. Select jump type
1. Click "Analyze"
1. Wait 10-60 seconds
1. See real metrics displayed

### Test 4: Upload a Video (Via API Directly)

If you want to test the backend API directly:

```bash
# Create a test video upload
curl -X POST "http://localhost:8000/api/analyze" \
  -F "video=@/path/to/your/video.mp4" \
  -F "jump_type=cmj"

# Expected response (200):
# {
#   "status": 200,
#   "message": "Successfully analyzed cmj video",
#   "processing_time_s": 12.34,
#   "metrics": {
#     "data": {
#       "jump_height_m": 0.456,
#       "flight_time_ms": 608.23,
#       ...
#     },
#     "metadata": {...},
#     "validation": {...}
#   },
#   "results_url": null  # or R2 URL if R2 configured
# }
```

### Test 5: Error Handling

#### Test Invalid File Format

```bash
# Try uploading a non-video file
echo "This is not a video" > test.txt

curl -X POST "http://localhost:8000/api/analyze" \
  -F "video=@test.txt" \
  -F "jump_type=cmj"

# Expected: 422 Validation Error
```

#### Test File Too Large

```bash
# Create a 501MB file
dd if=/dev/zero of=large_file.bin bs=1M count=501

curl -X POST "http://localhost:8000/api/analyze" \
  -F "video=@large_file.bin" \
  -F "jump_type=cmj"

# Expected: 422 Validation Error (file too large)
```

#### Test Invalid Jump Type

```bash
curl -X POST "http://localhost:8000/api/analyze" \
  -F "video=@your_video.mp4" \
  -F "jump_type=invalid_type"

# Expected: 422 Validation Error
```

### Test 6: Mobile Responsive

1. Open http://localhost:5173 in browser
1. Open DevTools (F12)
1. Toggle device toolbar (Ctrl+Shift+M)
1. Test on various phone sizes:
   - iPhone 12 (390x844)
   - iPad (768x1024)
   - Android (375x667)
1. Verify:
   - All elements fit
   - Buttons are clickable
   - Text is readable
   - Upload works on mobile

## Using Your Own Videos

### Prerequisites for Testing

- CMJ video: Lateral view (side profile), feet visible, clear motion
- Drop Jump video: Lateral view, box visible, clear landing
- Quality: At least 30fps, clear lighting
- Format: MP4, AVI, MOV, MKV, FLV, or WMV
- Size: Less than 500MB

### How to Test with Your Video

**Option 1: Via Frontend UI (Recommended)**

1. Open http://localhost:5173
1. Upload your video
1. Select jump type
1. See metrics

**Option 2: Via curl**

```bash
curl -X POST "http://localhost:8000/api/analyze" \
  -F "video=@/path/to/your/video.mp4" \
  -F "jump_type=cmj" \
  -s | jq .

# The -s flag silences progress
# The | jq . formats JSON nicely
```

**Option 3: Via Python Script**

```python
import requests
import json

api_url = "http://localhost:8000/api/analyze"

with open('/path/to/video.mp4', 'rb') as f:
    files = {'video': f}
    data = {'jump_type': 'cmj'}

    response = requests.post(api_url, files=files, data=data)

    print(json.dumps(response.json(), indent=2))
```

## Troubleshooting Local Testing

### Backend won't start

```bash
# Check Python version
python --version  # Must be 3.12+

# Check uv is installed
uv --version

# Reinstall dependencies
cd backend
rm -rf .venv uv.lock
uv sync

# Check for port conflicts
lsof -i :8000  # Should show nothing or just our uvicorn
```

### Frontend can't connect to backend

```bash
# Check backend is running
curl http://localhost:8000/health  # Should work

# Check .env.local in frontend
cat frontend/.env.local
# Should have: VITE_API_URL=http://localhost:8000

# Check browser console for CORS errors
# (Open DevTools → Console tab)

# Verify backend has CORS configured
# Should allow localhost:5173
```

### Video upload fails

```bash
# Check file exists and is accessible
ls -lh /path/to/video.mp4

# Check file size
du -h /path/to/video.mp4  # Must be < 500MB

# Check file type
file /path/to/video.mp4  # Should show video/mp4

# Test with curl
curl -X POST "http://localhost:8000/api/analyze" \
  -F "video=@/path/to/video.mp4" \
  -F "jump_type=cmj" \
  -v  # -v for verbose output

# Check backend logs for error details
```

### Analysis takes too long

Video processing can take 10-60 seconds depending on:

- Video length (longer = slower)
- Video resolution (higher = slower)
- Computer specs (slower = slower)

This is normal. The frontend shows a loading spinner during analysis.

### Port conflicts

If you get "Address already in use" errors:

```bash
# Backend port 8000
lsof -i :8000  # Find what's using port
kill -9 <PID>  # Kill it

# Frontend port 5173
lsof -i :5173
kill -9 <PID>

# Or change ports
cd backend
uv run uvicorn kinemotion_backend.app:app --port 8001 --reload

cd frontend
yarn dev --port 5174
```

## Performance Testing

### Measure Analysis Time

```bash
# Time a complete analysis
time curl -X POST "http://localhost:8000/api/analyze" \
  -F "video=@sample_video.mp4" \
  -F "jump_type=cmj" \
  -s > /dev/null

# You'll see: real 0m12.345s (analysis time + network)
```

### Check Memory Usage

```bash
# Monitor backend memory
watch -n 1 'ps aux | grep uvicorn'

# During video processing, you should see < 1GB RAM usage
```

### Check Frontend Build Size

```bash
cd frontend

# Build optimized version
yarn build

# Check output size
du -sh dist/

# Typical: 150-200KB gzipped
```

## Testing Checklist

- [ ] Backend starts without errors
- [ ] Frontend starts without errors
- [ ] `curl http://localhost:8000/health` returns 200
- [ ] Frontend loads at http://localhost:5173
- [ ] Frontend can reach backend (check browser console)
- [ ] Upload CMJ video → see metrics
- [ ] Upload Drop Jump video → see metrics
- [ ] File validation works (reject >500MB)
- [ ] File format validation works (reject non-videos)
- [ ] Error messages are user-friendly
- [ ] Loading spinner appears during analysis
- [ ] Results display correctly
- [ ] Mobile responsive on phone
- [ ] Analysis completes in 10-60 seconds
- [ ] API docs work at http://localhost:8000/docs
- [ ] No CORS errors in browser console

## Browser DevTools Debugging

### Check Network Tab

1. Open DevTools (F12)
1. Go to Network tab
1. Upload a video
1. You should see:
   - POST to `/api/analyze` (200 status after analysis)
   - Response contains metrics JSON
   - No CORS errors

### Check Console Tab

1. Open DevTools → Console
1. Should be clean (no red errors)
1. You might see vite/react dev messages (yellow is OK)
1. Look for any red error messages

### Check Application Tab

1. Open DevTools → Application
1. Go to Storage → Local Storage
1. You should see environment variables if stored

## Next Steps After Local Testing

### If Everything Works ✅

1. Commit changes to GitHub
1. Deploy backend: `cd backend && flyctl deploy --remote-only`
1. Deploy frontend: Connect GitHub to Vercel
1. Recruit coaches for MVP testing

### If Issues Found ❌

1. Check troubleshooting sections above
1. Review backend logs: Terminal showing `uv run uvicorn`
1. Review frontend logs: Browser console (F12)
1. Check API docs at http://localhost:8000/docs for request format

## Advanced: Local Testing with R2 (Optional)

If you want to test R2 storage locally:

### Setup R2

```bash
# Create Cloudflare account and R2 bucket
# Generate API token (S3-compatible)
# Copy credentials

# In backend/.env.local
R2_ENDPOINT=https://YOUR_ACCOUNT_ID.r2.cloudflarestorage.com
R2_ACCESS_KEY=YOUR_ACCESS_KEY
R2_SECRET_KEY=YOUR_SECRET_KEY
R2_BUCKET_NAME=kinemotion
```

### Test R2 Upload

```bash
# Restart backend to load new environment
# Ctrl+C then re-run uvicorn

# Upload a video (it should now store in R2)
curl -X POST "http://localhost:8000/api/analyze" \
  -F "video=@sample_video.mp4" \
  -F "jump_type=cmj"

# Response should include results_url pointing to R2
# Example: https://kinemotion.abc123.r2.cloudflarestorage.com/results/...
```

### Verify R2 Files

```bash
# Visit https://dash.cloudflare.com
# Go to R2 → your bucket
# You should see:
# - videos/ directory (temporarily stored)
# - results/ directory (analysis JSON results)
```

## Local Development Workflow

### Typical Session

```bash
# Terminal 1: Backend
cd backend
uv run uvicorn kinemotion_backend.app:app --reload

# Terminal 2: Frontend
cd frontend
yarn dev

# Terminal 3: Testing (optional)
# Use this for curl commands, monitoring, etc.
```

### Code Changes

**Backend changes:**

- Edit `backend/src/kinemotion_backend/app.py`
- uvicorn auto-reloads (watch the terminal)
- Refresh browser to test changes

**Frontend changes:**

- Edit `frontend/src/` files
- Vite auto-rebuilds (watch the terminal)
- Browser auto-refreshes

### Database/State (None for MVP)

- MVP has no database
- State is in memory during requests
- Videos are temporary (deleted after processing)
- Results stored in R2 (optional)

## Performance Baseline

For reference, typical performance on a modern laptop:

| Operation          | Time                                               |
| ------------------ | -------------------------------------------------- |
| Backend startup    | 2-3 seconds                                        |
| Frontend startup   | 3-5 seconds                                        |
| First video upload | 15-60 seconds (first time MediaPipe loads models)  |
| Subsequent uploads | 10-60 seconds (depends on video length/resolution) |
| Frontend build     | 5-10 seconds                                       |

## Getting Help

If local testing fails:

1. **Check logs**

   - Backend: Terminal output
   - Frontend: Browser console (F12)

1. **Try fresh install**

   ```bash
   # Backend
   cd backend && rm -rf .venv uv.lock && uv sync

   # Frontend
   cd frontend && rm -rf node_modules yarn.lock && yarn install
   ```

1. **Check environment**

   ```bash
   # Verify Python
   python --version  # Must be 3.12+

   # Verify dependencies
   uv --version
   yarn --version
   ```

1. **Test individual components**

   ```bash
   # Test backend API directly
   curl http://localhost:8000/health

   # Test frontend loads
   curl http://localhost:5173
   ```

______________________________________________________________________

**Status:** Ready for local testing
**Next:** Deploy to Cloud Run + Vercel after confirming local testing works (automatic via GitHub Actions)
