# CMJ Sample Video

## Video Information

- **File**: `cmj.mp4`
- **Resolution**: 720x1280 (portrait, phone camera)
- **FPS**: 29.58
- **Frames**: 236
- **Duration**: ~8 seconds
- **Camera View**: Lateral (side view)

## Validated Results

Results from analyzing this video with kinemotion:

```bash
kinemotion cmj-analyze samples/cmjs/cmj.mp4 --output debug.mp4
```

**Jump Performance:**

- Jump Height: 50.6cm
- Flight Time: 642.3ms

**Phase Detection:**

- Lowest Point: Frame 146
- Takeoff: Frame 154
- Landing: Frame 173

**Accuracy**: ±1 frame (±33ms at 30fps)

See `cmj_metrics.json` for complete output.

## Usage as Test Data

This video is used for:

- Integration testing of CMJ module
- Documentation examples
- Algorithm validation

**Known ground truth:**

- Takeoff: Frame 153 (detected: 154, error: +1 frame)
- Landing: Frame 172 (detected: 173, error: +1 frame)
- Jump height: ~50cm (detected: 50.6cm)
