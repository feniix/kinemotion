# Backend Setup Guide

Complete setup guide for the Kinemotion FastAPI backend.

## Prerequisites

- Python 3.10+ (3.12 recommended)
- `uv` package manager (or pip)
- Cloudflare R2 account (optional, for video/results storage)

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/feniix/kinemotion.git
cd kinemotion
```

### 2. Install Backend Dependencies

From the project root:

```bash
cd backend
uv sync
```

Or without uv:

```bash
pip install -e .
```

### 3. Configure Environment

Create `.env` file in backend directory:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Optional: R2 credentials for cloud storage
R2_ENDPOINT=https://your-account.r2.cloudflarestorage.com
R2_ACCESS_KEY=your_access_key
R2_SECRET_KEY=your_secret_key
R2_BUCKET_NAME=kinemotion

# Optional: Production CORS origins
CORS_ORIGINS=https://myapp.example.com
```

**Note:** R2 credentials are optional. The API works without them but won't persist videos to cloud storage.

## Running the Server

### Development (with auto-reload)

```bash
cd backend
uv run uvicorn kinemotion_backend.app:app --reload
```

Server runs at: `http://localhost:8000`

### Production

```bash
uv run uvicorn kinemotion_backend.app:app --host 0.0.0.0 --port 8000
```

### API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Cloudflare R2 Setup (Optional)

If you want to enable cloud storage for videos and results:

### 1. Create R2 Bucket

1. Log in to Cloudflare Dashboard
1. Navigate to R2 Storage
1. Create a new bucket (e.g., "kinemotion")
1. Note the bucket name

### 2. Create API Token

1. In Cloudflare Dashboard, go to Account Settings > API Tokens
1. Create a custom token with R2 permissions:
   - Read/Write permissions on R2
   - Include specific bucket(s) if desired
1. Copy the API credentials

### 3. Get Endpoint URL

1. In R2 Storage, select your bucket
1. Go to Settings
1. Copy the S3 API endpoint (e.g., `https://abc123.r2.cloudflarestorage.com`)

### 4. Configure Backend

Update `.env`:

```env
R2_ENDPOINT=https://abc123.r2.cloudflarestorage.com
R2_ACCESS_KEY=your_token_access_key_id
R2_SECRET_KEY=your_token_secret_access_key
R2_BUCKET_NAME=kinemotion
```

Restart the backend server.

### 5. Verify Configuration

Check the health endpoint:

```bash
curl http://localhost:8000/health

# Response should show:
# "r2_configured": true
```

## Testing the API

### 1. Health Check

```bash
curl http://localhost:8000/health
```

### 2. Analyze Sample Video

Download or create a sample video, then:

```bash
curl -X POST "http://localhost:8000/api/analyze" \
  -F "file=@sample.mp4" \
  -F "jump_type=cmj" \
  -F "quality=balanced"
```

### 3. Python Client Example

```python
import requests

# Upload and analyze
with open("video.mp4", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/analyze",
        files={"file": f},
        data={
            "jump_type": "cmj",
            "quality": "balanced"
        }
    )

result = response.json()
print(f"Status: {result['status']}")
print(f"Jump Height: {result['metrics']['data']['jump_height_m']}m")
print(f"Processing Time: {result['processing_time_s']}s")

# Optional: Access results in cloud
if "results_url" in result:
    print(f"Results stored at: {result['results_url']}")
```

### 4. JavaScript Client Example

```javascript
const formData = new FormData();
const videoFile = document.getElementById("video-input").files[0];
formData.append("file", videoFile);
formData.append("jump_type", "cmj");
formData.append("quality", "balanced");

const response = await fetch("http://localhost:8000/api/analyze", {
  method: "POST",
  body: formData
});

const result = await response.json();
console.log(`Jump height: ${result.metrics.data.jump_height_m}m`);
```

## Development Workflow

### Running Tests

```bash
cd backend
uv run pytest
```

### Type Checking

```bash
uv run pyright
```

### Linting and Formatting

```bash
uv run ruff check --fix
```

### All Quality Checks

```bash
uv run ruff check --fix && uv run pyright && uv run pytest
```

## Troubleshooting

### Import Errors

If you see `ModuleNotFoundError: No module named 'kinemotion'`:

Make sure you're running from backend directory with proper installation:

```bash
cd backend
uv sync
uv run uvicorn kinemotion_backend.app:app --reload
```

### R2 Connection Failed

Check that:

1. R2 credentials are correctly set in `.env`
1. R2 bucket exists and is accessible
1. Network connectivity to Cloudflare

Debug with:

```bash
python3 << 'EOF'
import os
from kinemotion_backend.app import R2StorageClient

try:
    client = R2StorageClient()
    print("R2 client initialized successfully")
    print(f"Endpoint: {client.endpoint}")
    print(f"Bucket: {client.bucket_name}")
except Exception as e:
    print(f"Error: {e}")
EOF
```

### Video Analysis Failures

If analysis fails:

1. Check video format (MP4, AVI, MOV, etc.)
1. Ensure video shows clear jumping motion
1. Try "accurate" quality preset: `/api/analyze?quality=accurate`
1. Check server logs for detailed errors

### Memory Issues

For large videos or low-memory systems:

1. Process smaller videos first
1. Use "fast" quality preset
1. Increase available system memory
1. Consider Docker with memory limits

## Docker Deployment

### Build Docker Image

Create `Dockerfile` in backend directory:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsm6 libxext6 libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install --no-cache-dir uv

# Copy pyproject.toml and uv.lock
COPY pyproject.toml uv.lock* ./

# Install Python dependencies
RUN uv sync --frozen

# Copy application code
COPY src ./src

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PATH="/root/.local/bin:$PATH"

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "kinemotion_backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Build and Run

```bash
# From backend directory
docker build -t kinemotion-backend .

# Run with environment variables
docker run -p 8000:8000 \
  -e R2_ENDPOINT=https://your-r2.cloudflarestorage.com \
  -e R2_ACCESS_KEY=your_key \
  -e R2_SECRET_KEY=your_secret \
  kinemotion-backend
```

## Production Deployment

### Environment Variables

Set these in your production environment:

```bash
# Required: Kinemotion library path
PYTHONPATH=/path/to/kinemotion/src:$PYTHONPATH

# R2 Storage (optional)
R2_ENDPOINT=https://your-r2.cloudflarestorage.com
R2_ACCESS_KEY=production_access_key
R2_SECRET_KEY=production_secret_key
R2_BUCKET_NAME=kinemotion-prod

# CORS
CORS_ORIGINS=https://app.example.com,https://api.example.com

# Server
PYTHONUNBUFFERED=1
```

### Performance Tuning

1. **Workers**: Run multiple gunicorn workers for concurrency:

```bash
gunicorn --workers 4 --worker-class uvicorn.workers.UvicornWorker kinemotion_backend.app:app
```

2. **Reverse Proxy**: Use nginx to handle static files and load balancing

1. **Monitoring**: Add logging and error tracking (e.g., Sentry)

### Security Considerations

1. **CORS**: Set specific allowed origins, not "\*"
1. **Rate Limiting**: Add rate limiting middleware
1. **Authentication**: Add API key/JWT authentication if needed
1. **Validation**: All input validation is already implemented
1. **HTTPS**: Use SSL/TLS in production
1. **Secrets**: Never commit `.env` to version control

## Integration with Frontend

### React Setup

```bash
# Create React app with CORS proxy
npm create vite@latest kinemotion-ui -- --template react
cd kinemotion-ui

# For development, add proxy in vite.config.ts
export default {
  server: {
    proxy: {
      '/api': 'http://localhost:8000'
    }
  }
}
```

### Frontend API Call

```typescript
const analyzeVideo = async (file: File) => {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("jump_type", "cmj");
  formData.append("quality", "balanced");

  const response = await fetch("/api/analyze", {
    method: "POST",
    body: formData
  });

  const data = await response.json();
  return data;
};
```

## Monitoring and Logging

### Enable Request Logging

```python
from fastapi.middleware.logging import LoggingMiddleware
import logging

logging.basicConfig(level=logging.INFO)
app.add_middleware(LoggingMiddleware)
```

### View Logs

```bash
# Real-time logs
tail -f /var/log/kinemotion-backend.log

# Filter by error
grep "ERROR" /var/log/kinemotion-backend.log
```

## Getting Help

- Check README.md for API documentation
- Review error messages in server logs
- Check kinemotion main repository for issues
- Test with sample videos first

## Next Steps

1. Set up frontend (React/Vue component for video upload)
1. Configure production deployment
1. Set up monitoring and alerts
1. Create admin dashboard for usage metrics
1. Add authentication and rate limiting if needed
