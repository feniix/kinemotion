# E2E Test Fixtures

This directory contains test videos for E2E testing.

## Files

- `cmj-45-IMG_6733.MOV` - CMJ test video (45° oblique camera angle)
- `dj-45-IMG_6739.MOV` - Drop Jump test video (45° oblique camera angle)

## Source

Videos are from `/samples/validation/` in the kinemotion CLI project.

## Adding More Test Videos

To add more test videos:

```bash
# Copy from samples
cp /path/to/samples/validation/*.MOV e2e/fixtures/

# Or create a minimal test video (requires ffmpeg)
ffmpeg -f lavfi -i testsrc=duration=5:size=320x240:rate=30 \
  -c:v libx264 -tune fastblur -pix_fmt yuv420p \
  -t 5 test-video.mp4
```

Keep test videos small (< 10MB) for fast test execution.
