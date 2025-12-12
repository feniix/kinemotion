# Kinemotion Backend API

FastAPI backend for Kinemotion video-based kinematic analysis. Provides REST API endpoints for video analysis with real metrics integration and Cloudflare R2 storage support.

## Features

- **Real Metrics Integration**: Uses the kinemotion library for accurate biomechanical analysis
- **Drop Jump Analysis**: Ground contact time, flight time, jump height
- **CMJ Analysis**: Jump height, countermovement depth, flight time, triple extension
- **Cloudflare R2 Storage**: Optional video and results storage on R2
- **Quality Presets**: Fast, balanced, and accurate analysis modes
- **CORS Support**: Development and production configuration
- **Error Handling**: Comprehensive error handling and validation

## Quick Start

### Installation

```bash
# From backend directory
uv sync

# Or with pip
pip install -e .
```

**Note on `uv.lock` files:**

- This backend is part of a uv workspace (root `uv.lock` is the source of truth)
- `backend/uv.lock` is kept in sync for Docker builds and future repository extraction
- When dependencies change, run `uv lock` from the repository root to update both lock files
- CI/CD automatically syncs `backend/uv.lock` with root `uv.lock` during builds

### Running the Server

```bash
# Development (with auto-reload)
uv run uvicorn kinemotion_backend.app:app --reload

# Production
uv run uvicorn kinemotion_backend.app:app --host 0.0.0.0 --port 8000
```

Access API at `http://localhost:8000`

### Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Environment Configuration

### R2 Storage (Optional)

Configure Cloudflare R2 for video and results storage:

```bash
# .env or export these variables
R2_ENDPOINT=https://abc123.r2.cloudflarestorage.com
R2_ACCESS_KEY=your_access_key
R2_SECRET_KEY=your_secret_key
R2_BUCKET_NAME=kinemotion  # Default

# Optional: Serve videos via public URL instead of presigned URLs
R2_PUBLIC_BASE_URL=https://kinemotion-public.example.com  # Custom domain
# Or use R2.dev public URL: https://kinemotion.abc123.r2.dev

# Optional: Presigned URL expiration (default: 604800 = 7 days)
R2_PRESIGN_EXPIRATION_S=604800
```

**URL Strategy:**

- If `R2_PUBLIC_BASE_URL` is set, videos are served via stable public URLs (recommended for production)
- Otherwise, presigned URLs are generated with configurable expiration (default 7 days)
- Presigned URLs expire after `R2_PRESIGN_EXPIRATION_S` seconds (max 604800 = 7 days)

If R2 credentials are not provided, the API will still work but won't store files on R2 (videos are processed locally and deleted after analysis).

### CORS Configuration

By default, CORS is configured for localhost development:

- http://localhost:3000 (React dev server)
- http://localhost:5173 (Vite dev server)
- http://localhost:8080 (Vue dev server)
- http://127.0.0.1:3000, :5173, :8080

For production, add additional origins:

```bash
CORS_ORIGINS=https://myapp.example.com,https://api.example.com
```

## API Endpoints

### Health Check

```http
GET /health
```

Returns service status and configuration information.

**Example Response:**

```json
{
  "status": "ok",
  "service": "kinemotion-backend",
  "version": "0.1.0",
  "timestamp": "2025-11-28T22:30:00.000000",
  "r2_configured": true
}
```

### Analyze Video (Multipart Upload)

```http
POST /api/analyze
Content-Type: multipart/form-data

Parameters:
  - file: Video file (required)
  - jump_type: "drop_jump" or "cmj" (default: "cmj")
  - quality: "fast", "balanced", or "accurate" (default: "balanced")
```

**Example with cURL:**

```bash
curl -X POST "http://localhost:8000/api/analyze" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@video.mp4" \
  -F "jump_type=cmj" \
  -F "quality=balanced"
```

**Success Response (200):**

```json
{
  "status": 200,
  "message": "Successfully analyzed cmj video",
  "processing_time_s": 12.34,
  "metrics": {
    "data": {
      "jump_height_m": 0.456,
      "flight_time_ms": 608.23,
      "countermovement_depth_m": 0.234,
      ...
    },
    "metadata": {...},
    "validation": {...}
  },
  "results_url": "https://r2-bucket.com/results/cmj/20251128_223000_results.json"
}
```

**Error Response (422):**

```json
{
  "status": 422,
  "message": "Validation error",
  "error": "Invalid video format: .txt. Supported formats: .mp4, .avi, .mov, .mkv, .flv, .wmv"
}
```

**Error Response (500):**

```json
{
  "status": 500,
  "message": "Video analysis failed",
  "error": "ValueError: Could not detect CMJ phases in video",
  "processing_time_s": 5.12
}
```

### Analyze Local Video

Development endpoint for testing with local files:

```http
POST /api/analyze-local

Parameters:
  - video_path: Path to local video (required)
  - jump_type: "drop_jump" or "cmj" (default: "cmj")
  - quality: "fast", "balanced", or "accurate" (default: "balanced")
```

**Example with cURL:**

```bash
curl -X POST "http://localhost:8000/api/analyze-local" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "video_path=/path/to/video.mp4&jump_type=cmj&quality=balanced"
```

## Jump Type Details

### Drop Jump

Athlete stands on an elevated platform, drops to ground, and rebounds.

**Key Metrics:**

- `ground_contact_time_ms`: Time in contact with ground
- `flight_time_ms`: Time in air after rebound
- `jump_height_m`: Height calculated from flight time
- `jump_height_kinematic_m`: Height from kinematic equation
- `reactive_strength_index`: Flight time / ground contact time

**Algorithm:** Forward search from drop contact

### Counter Movement Jump (CMJ)

Athlete starts standing and performs a countermovement before jumping.

**Key Metrics:**

- `jump_height_m`: Maximum height reached
- `flight_time_ms`: Time in air
- `countermovement_depth_m`: Maximum downward movement
- `eccentric_duration_ms`: Time during downward movement
- `concentric_duration_ms`: Time during upward push-off
- `peak_eccentric_velocity_m_s`: Maximum downward velocity
- `peak_concentric_velocity_m_s`: Maximum upward velocity

**Algorithm:** Backward search from peak height

## Quality Presets

### Fast

- Lower detection confidence (0.3)
- Reduced smoothing window
- Suitable for quick analysis with acceptable accuracy

### Balanced (Default)

- Moderate detection confidence (0.5)
- Standard smoothing parameters
- Good balance of speed and accuracy for most use cases

### Accurate

- High detection confidence (0.6)
- Aggressive smoothing and outlier rejection
- Best for research and detailed analysis

## File Validation

### Supported Video Formats

- MP4 (.mp4)
- AVI (.avi)
- MOV (.mov)
- Matroska (.mkv)
- FLV (.flv)
- WMV (.wmv)

### Size Limits

- Maximum file size: 500MB
- Recommended: Under 200MB for responsive processing

## Error Handling

### Validation Errors (422)

- Invalid video format
- File too large
- Missing required parameters
- Invalid jump type or quality preset

### File Errors (404)

- Local video file not found

### Processing Errors (500)

- Pose detection failed
- Phase detection failed
- Insufficient video quality
- Unexpected algorithm errors

## Development

### Running Tests

```bash
uv run pytest
```

### Type Checking

```bash
uv run pyright
```

### Linting

```bash
uv run ruff check --fix
```

## Architecture

### Core Components

1. **R2StorageClient**: Handles Cloudflare R2 operations

   - Upload videos and results
   - Download files
   - Delete temporary files

1. **AnalysisResponse**: Standardized response format

   - Status code and message
   - Metrics data
   - Storage URL
   - Processing time

1. **FastAPI Application**

   - CORS middleware for frontend integration
   - Three main endpoints
   - Comprehensive error handling
   - Async video processing

### Data Flow

```
1. Client uploads video file via /api/analyze
   ↓
2. Validate file (format, size)
   ↓
3. Save to temporary location
   ↓
4. Upload to R2 (if configured)
   ↓
5. Process with kinemotion (real analysis)
   ↓
6. Upload results to R2 (if configured)
   ↓
7. Return metrics + storage URLs
   ↓
8. Clean up temporary files
```

## Performance Considerations

### Processing Time

Typical processing times on modern hardware:

- **Fast**: 5-10 seconds
- **Balanced**: 10-20 seconds
- **Accurate**: 20-40 seconds

Depends on:

- Video duration and resolution
- Hardware capabilities
- System load

### Memory Usage

- Video frames cached in memory during processing
- Recommended minimum: 8GB RAM
- For videos >200MB, consider processing in batches

### R2 Upload/Download

- Network bandwidth dependent
- Videos uploaded before processing
- Results uploaded after analysis
- Set appropriate timeouts for production

## Deployment

### Docker (Example)

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install kinemotion backend dependencies
COPY backend/pyproject.toml backend/uv.lock /app/
RUN pip install uv && uv sync --frozen

# Copy source code
COPY backend/src /app/src
COPY src /app/../src  # kinemotion source

ENV R2_ENDPOINT=https://your-r2.cloudflarestorage.com
ENV R2_ACCESS_KEY=***
ENV R2_SECRET_KEY=***
ENV PYTHONUNBUFFERED=1

CMD ["uv", "run", "uvicorn", "kinemotion_backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables for Production

```bash
# R2 Storage (Required for video persistence)
R2_ENDPOINT=https://xxx.r2.cloudflarestorage.com
R2_ACCESS_KEY=your_access_key
R2_SECRET_KEY=your_secret_key
R2_BUCKET_NAME=kinemotion

# Optional: Public URL for serving videos (recommended)
R2_PUBLIC_BASE_URL=https://kinemotion-public.example.com
# Or: R2_PUBLIC_BASE_URL=https://kinemotion.abc123.r2.dev

# Optional: Presigned URL expiration in seconds (default: 604800 = 7 days)
R2_PRESIGN_EXPIRATION_S=604800

# CORS (Add production domain)
CORS_ORIGINS=https://myapp.example.com

# Server Configuration
PYTHONUNBUFFERED=1
```

## Troubleshooting

### "R2 credentials not configured"

R2 is optional. If you don't want cloud storage, simply omit environment variables. The API will still work but process videos locally.

### "Video analysis failed"

Check:

1. Video file is valid and readable
1. Video shows clear drop jump or CMJ motion
1. Camera angle is lateral (side view)
1. Athlete is visible throughout motion
1. Frame rate is 30fps or higher

### "Could not detect CMJ phases"

Possible causes:

- Athlete motion is too fast or distorted
- Video quality is too low
- Try "accurate" preset for better detection
- Check that video shows complete CMJ cycle

### Memory errors on large videos

- Reduce video resolution
- Use "fast" preset
- Increase available system RAM
- Process videos one at a time

## Integration Examples

### Python Client

```python
import requests

response = requests.post(
    "http://localhost:8000/api/analyze",
    files={"file": open("video.mp4", "rb")},
    data={
        "jump_type": "cmj",
        "quality": "balanced"
    }
)

result = response.json()
print(f"Jump height: {result['metrics']['data']['jump_height_m']}m")
```

### JavaScript/TypeScript

```typescript
const formData = new FormData();
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

### React Hook

```typescript
const [loading, setLoading] = useState(false);
const [results, setResults] = useState(null);

const analyzeVideo = async (file: File) => {
  setLoading(true);
  const formData = new FormData();
  formData.append("file", file);
  formData.append("jump_type", "cmj");

  try {
    const response = await fetch("/api/analyze", {
      method: "POST",
      body: formData
    });
    const data = await response.json();
    setResults(data.metrics);
  } finally {
    setLoading(false);
  }
};
```

## Contributing

When adding new features:

1. Maintain type hints (pyright strict)
1. Follow existing error handling patterns
1. Add appropriate validation for inputs
1. Update this README with new endpoints
1. Test with real videos before committing

## License

MIT - See LICENSE file in repository

## Support

For issues:

- Check the troubleshooting section above
- Review error messages and processing_time_s
- Enable verbose mode in kinemotion for debugging
- Open issue on GitHub: https://github.com/feniix/kinemotion/issues
