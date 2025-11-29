# Fly.io Deployment Guide

Complete deployment configuration for the Kinemotion backend on Fly.io.

## Files Created

1. **`Dockerfile`** - Multi-stage Python 3.12 container optimized for video processing
1. **`fly.toml`** - Fly.io configuration with free tier settings
1. **`.dockerignore`** - Excludes unnecessary files from Docker build

## Quick Start

### 1. Install Fly CLI

```bash
curl -L https://fly.io/install.sh | sh
flyctl auth login
```

### 2. Initialize and Deploy

```bash
cd backend
flyctl launch --image-label kinemotion-backend
# OR deploy existing app:
flyctl deploy --remote-only
```

### 3. Set Required Secrets

For Cloudflare R2 storage (optional but recommended for production):

```bash
# Get credentials from Cloudflare R2 dashboard
flyctl secrets set R2_ENDPOINT=https://YOUR_ACCOUNT_ID.r2.cloudflarestorage.com
flyctl secrets set R2_ACCESS_KEY=YOUR_ACCESS_KEY
flyctl secrets set R2_SECRET_KEY=YOUR_SECRET_KEY
flyctl secrets set R2_BUCKET_NAME=kinemotion
```

### 4. Update CORS Origins (Optional)

To add your frontend domain:

```bash
flyctl config set env.CORS_ORIGINS="https://your-domain.com,https://another-domain.com"
```

## Configuration Details

### Docker Image

- **Base**: Python 3.12-slim (latest, most efficient)
- **Dependencies**:
  - ffmpeg (video processing)
  - libsm6, libxext6, libxrender-dev (OpenCV/MediaPipe support)
  - libgomp1 (NumPy optimization)
- **Package Manager**: uv (fast, deterministic dependency installation)
- **Health Check**: `/health` endpoint monitored every 30 seconds

### Fly.io Settings

- **App Name**: `kinemotion-api`
- **Region**: `sjc` (San Jose, US - adjust in `fly.toml` if needed)
- **Machine**: Free tier (shared CPU, 256MB memory, 1 worker)
- **Port**: 8000 (internal and external)
- **Workers**: 1 (single worker for free tier stability)

### Graceful Shutdown

- **Timeout**: 60 seconds for video processing completion
- **Health Check Grace Period**: 5 seconds on startup
- **Restart**: Automatic on crash or deployment

## Environment Variables

### Default Configuration (in fly.toml)

- `LOG_LEVEL`: "info" (set to "debug" for troubleshooting)
- `WORKERS`: "1" (shared CPU safe setting)
- `CORS_ORIGINS`: "https://kinemotion-mvp.vercel.app"
- `PYTHONUNBUFFERED`: "1" (streaming output)
- `PYTHONDONTWRITEBYTECODE`: "1" (reduce disk I/O)

### Secrets (set via `flyctl secrets set`)

- `R2_ENDPOINT`: Cloudflare R2 endpoint
- `R2_ACCESS_KEY`: R2 access key ID
- `R2_SECRET_KEY`: R2 secret key
- `R2_BUCKET_NAME`: S3 bucket name (default: "kinemotion")

## Performance Notes

### Free Tier Considerations

1. **Single Worker**: Video processing is CPU-bound, single worker prevents memory thrashing
1. **256MB Memory**: Sufficient for sequential video processing with temp file cleanup
1. **Graceful Timeout**: 60 seconds allows complete video analysis before shutdown
1. **Auto Restart**: Failed requests trigger immediate restart

### Expected Performance

- **Typical analysis time**: 30-120 seconds (depends on video length/quality)
- **Concurrent requests**: Limited to 1 (single worker)
- **Queue timeout**: Requests will fail if processing exceeds 60s

### Upgrade Path

For production with multiple concurrent requests:

1. Increase `WORKERS` to 2-4 in `fly.toml`
1. Upgrade machine to `shared-cpu-2x` or `shared-cpu-4x`
1. Increase memory_mb to 512-1024
1. Consider load balancing across multiple machines

## Monitoring

### View Logs

```bash
flyctl logs
flyctl logs -n 100  # Last 100 lines
flyctl logs --follow  # Stream logs
```

### Check Status

```bash
flyctl status
flyctl machine list
flyctl machine status <machine_id>
```

### View Metrics

```bash
flyctl metrics
```

## Common Issues

### "Out of memory" errors

- Increase machine memory in `fly.toml`: `memory_mb = 512`
- Or upgrade machine type: `cpu_kind = "shared-cpu-2x"`
- Reduce concurrent workers or process videos sequentially

### Health check fails

- Check logs: `flyctl logs | grep health`
- Ensure `/health` endpoint is working: `curl https://kinemotion-api.fly.dev/health`
- Increase `grace_period` in `fly.toml` if startup takes time

### Video analysis timeouts

- Increase `timeout-graceful-shutdown` in `[processes]` section
- Consider processing videos offline with async jobs
- Implement video streaming/chunking for large files

### R2 storage errors

- Verify secrets are set: `flyctl secrets list`
- Check R2 credentials in Cloudflare dashboard
- Ensure bucket name matches R2 settings

## Debugging

### Build locally

```bash
docker build -t kinemotion-backend .
docker run -p 8000:8000 kinemotion-backend
```

### Test health endpoint

```bash
curl http://localhost:8000/health
```

### Test analysis endpoint

```bash
curl -X POST -F "file=@test.mp4" -F "jump_type=cmj" \
  http://localhost:8000/api/analyze
```

## Useful Commands

```bash
# Deploy changes
flyctl deploy --remote-only

# Check app info
flyctl info

# View environment variables
flyctl config view

# Scale machines (paid tier)
flyctl scale count 2

# Restart machines
flyctl machines restart <machine_id>

# SSH into machine (debugging)
flyctl ssh console

# View recent deployments
flyctl releases
```

## Next Steps

1. **Customize Region**: Update `primary_region` in `fly.toml` (e.g., "lax", "iad", "lon")
1. **Add Domain**: Use `flyctl certs add your-domain.com`
1. **Configure Monitoring**: Set up alerts via Fly dashboard
1. **Optimize**: Monitor logs and metrics, adjust WORKERS if needed
1. **Scale**: Upgrade to paid machine when needed for production load

## References

- [Fly.io Documentation](https://fly.io/docs/)
- [Dockerfile Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [Python on Fly.io](https://fly.io/docs/languages-and-frameworks/python/)
- [Fly Machines API](https://fly.io/docs/reference/machines/)
