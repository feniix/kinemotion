# Quick Start

Kinemotion provides video-based kinematic analysis for athletic performance using MediaPipe pose tracking.

## Installation

```bash
pip install kinemotion
```

## Supported Jump Types

- **Drop Jump**: Ground contact time, flight time, reactive strength index
- **Counter Movement Jump (CMJ)**: Jump height, flight time, countermovement depth, triple extension

## Quick Examples

### Drop Jump Analysis

```bash
kinemotion dropjump-analyze video.mp4
```

Or via Python API:

```python
from kinemotion import process_dropjump_video

metrics = process_dropjump_video("video.mp4", quality="balanced")
print(f"Ground contact time: {metrics.ground_contact_time:.3f}s")
print(f"RSI: {metrics.reactive_strength_index:.2f}")
```

### CMJ Analysis

```bash
kinemotion cmj-analyze video.mp4
```

Or via Python API:

```python
from kinemotion import process_cmj_video

metrics = process_cmj_video("video.mp4")
print(f"Jump height: {metrics.jump_height:.2f}m")
print(f"Flight time: {metrics.flight_time:.3f}s")
```

## Next Steps

- [CMJ Analysis Guide](guides/cmj-guide.md) - Detailed guide for CMJ analysis
- [Camera Setup](guides/camera-setup.md) - How to set up your camera for best results
- [API Reference](api/overview.md) - Complete API documentation
