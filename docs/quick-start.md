# Quick Start: Local Testing (5 minutes)

## Option 1: Automated Setup (Easiest)

```bash
# Run the setup script (one time)
./local_dev.sh

# Then open your browser:
# - Frontend: http://localhost:5173
# - API Docs: http://localhost:8000/docs

# Upload a video and test!
```

## Option 2: Manual Setup (More Control)

### Terminal 1: Backend

```bash
cd backend
uv sync                    # Install dependencies (first time only)
uv run uvicorn kinemotion_backend.app:app --reload
# Wait for: "Application startup complete"
```

### Terminal 2: Frontend

```bash
cd frontend
yarn install               # Install dependencies (first time only)
cp .env.example .env.local # Set API URL to http://localhost:8000
yarn dev
# Wait for: "Local: http://localhost:5173/"
```

### Terminal 3: Test (Optional)

```bash
# Check backend is running
curl http://localhost:8000/health

# You should see:
# {"status":"healthy",...}
```

## Testing

1. **Open frontend:** http://localhost:5173
1. **Upload video:** Any CMJ or Drop Jump video (\< 500MB)
1. **Select jump type:** CMJ or Drop Jump
1. **Click "Analyze"**
1. **Wait 10-60 seconds**
1. **See real metrics!**

## Test a Video via CLI

```bash
# Upload and analyze
curl -X POST "http://localhost:8000/api/analyze" \
  -F "video=@your_video.mp4" \
  -F "jump_type=cmj"

# Should return metrics JSON with analysis results
```

## Troubleshooting

### Backend won't start

```bash
# Make sure Python 3.12+
python --version

# Reinstall
cd backend
rm -rf uv.lock
uv sync
```

### Frontend can't reach backend

```bash
# Check backend is running
curl http://localhost:8000/health

# Check frontend .env.local has correct API URL
cat frontend/.env.local
# Should show: VITE_API_URL=http://localhost:8000
```

### Port conflicts

```bash
# Kill process on port 8000
lsof -i :8000 | grep LISTEN | awk '{print $2}' | xargs kill -9

# Kill process on port 5173
lsof -i :5173 | grep LISTEN | awk '{print $2}' | xargs kill -9
```

## API Documentation

Once backend is running, visit: **http://localhost:8000/docs**

This shows all available endpoints with interactive testing.

## What Happens When You Upload

```
1. Frontend uploads video → Backend (POST /api/analyze)
2. Backend receives video file
3. Backend uploads to Cloudflare R2 (optional, skipped if not configured)
4. Backend processes with real kinemotion library (10-60 seconds)
5. Backend stores results to R2 (optional)
6. Backend returns metrics to frontend
7. Frontend displays results in table
```

## Next Steps

- **Local testing works?** → Deploy to Cloud Run + Vercel (automatic via GitHub Actions)
- **Issues?** → See [`local-testing.md`](guides/local-testing.md) for detailed troubleshooting
- **Ready to deploy?** → Follow [`setup-issue-12.md`](guides/setup-issue-12.md)

## Reference

- **Local Frontend:** http://localhost:5173
- **Local Backend:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Backend Health:** http://localhost:8000/health

______________________________________________________________________

**Total time to test locally:** 5-10 minutes (after first setup)
