# JSON Structure Comparison: Design Options

**Decision Point:** How to structure kinemotion JSON output for v0.26.0

______________________________________________________________________

## Side-by-Side Comparison

### Current (v0.25.0) - Flat Structure

```json
{
  "jump_height_m": 0.352,
  "flight_time_ms": 534.0,
  "takeoff_frame": 154.3,
  "landing_frame": 172.8,
  "confidence": "high",
  "quality_score": 87.5,
  "quality_indicators": {
    "avg_visibility": 0.89,
    "tracking_stable": true
  },
  "warnings": ["..."]
}
```

**Access:** `result['jump_height_m']`

______________________________________________________________________

### Option A - measurements + quality

```json
{
  "measurements": {
    "jump_height_m": 0.352,
    "flight_time_s": 0.534,
    "takeoff_frame": 154.3,
    "landing_frame": 172.8
  },
  "quality": {
    "confidence": "high",
    "score": 87.5,
    "indicators": {...},
    "warnings": [...]
  }
}
```

**Access:** `result['measurements']['jump_height_m']`
**Later addition:** Need to add `metadata` wrapper → breaking change

______________________________________________________________________

### Option A-Prime - data + quality (staged for B)

```json
{
  "data": {
    "jump_height_m": 0.352,
    "flight_time_s": 0.534,
    "takeoff_frame": 154.3,
    "landing_frame": 172.8
  },
  "quality": {
    "confidence": "high",
    "score": 87.5,
    "indicators": {...},
    "warnings": [...]
  }
}
```

**Access:** `result['data']['jump_height_m']` ✅ (never changes)
**Later:** Move quality under metadata → `result['metadata']['quality']`

______________________________________________________________________

### Option B - data + metadata (FULL)

```json
{
  "data": {
    "jump_height_m": 0.352,
    "flight_time_s": 0.534,
    "takeoff_frame": 154.3,
    "landing_frame": 172.8
  },
  "metadata": {
    "quality": {
      "confidence": "high",
      "score": 87.5,
      "indicators": {...},
      "warnings": [...]
    },
    "video": {
      "fps": 29.6,
      "resolution": {"width": 720, "height": 1280}
    },
    "processing": {
      "version": "0.26.0",
      "timestamp": "2025-01-13T18:30:45Z",
      "quality_preset": "balanced"
    },
    "algorithm": {
      "detection_method": "backward_search",
      "smoothing": {...},
      "detection": {...}
    }
  }
}
```

**Access:** `result['data']['jump_height_m']` ✅ (never changes)
**Later additions:** All go in metadata → non-breaking ✅

______________________________________________________________________

### Option C - Hybrid (nest quality only)

```json
{
  "jump_height_m": 0.352,
  "flight_time_ms": 534.0,
  "takeoff_frame": 154.3,
  "landing_frame": 172.8,
  "quality": {
    "confidence": "high",
    "score": 87.5,
    "indicators": {...},
    "warnings": [...]
  }
}
```

**Access:** `result['jump_height_m']` ✅ (minimal change)
**Later:** Where to add video/processing info? → need to restructure → breaking

______________________________________________________________________

## Decision Matrix

| Criteria                    | Current                | Option A                          | A-Prime                           | Option B                                      | Option C                          |
| --------------------------- | ---------------------- | --------------------------------- | --------------------------------- | --------------------------------------------- | --------------------------------- |
| **Future breaking changes** | Many                   | 1 more                            | 1 more                            | None ✅                                       | 1+ more                           |
| **Measurement access**      | `result['x']`          | `result['measurements']['x']`     | `result['data']['x']` ✅          | `result['data']['x']` ✅                      | `result['x']`                     |
| **Quality access**          | `result['confidence']` | `result['quality']['confidence']` | `result['quality']['confidence']` | `result['metadata']['quality']['confidence']` | `result['quality']['confidence']` |
| **Extensibility**           | Poor ❌                | Good ✅                           | Excellent ✅                      | Excellent ✅                                  | Poor ❌                           |
| **Industry standard**       | No ❌                  | Partial ⚠️                        | Yes ✅                            | Yes ✅                                        | No ❌                             |
| **Nesting levels**          | 0-1                    | 1                                 | 1-2                               | 2                                             | 1                                 |
| **DataFrame export**        | Hard                   | Easy ✅                           | Easy ✅                           | Easy ✅                                       | Hard                              |
| **Implementation now**      | -                      | Medium                            | Medium                            | Large                                         | Small                             |

______________________________________________________________________

## Why Option B Wins (Especially in Alpha)

**Since you're in alpha:**

- 🎯 No users to break → implement ideal structure now
- 🎯 Breaking changes are FREE → use them wisely
- 🎯 Get it right once → never break again

**Option B gives you:**

1. ✅ **Zero future breaking changes** - all additions go in metadata
1. ✅ **Complete context** - video, processing, algorithm info
1. ✅ **Research-ready** - full reproducibility
1. ✅ **Industry standard** - matches REST API patterns
1. ✅ **Validation-ready** - all context needed for validation studies

**The cost:**

- One extra nesting level: `result['metadata']['quality']` vs `result['quality']`
- Worth it for never breaking again ✅

______________________________________________________________________

## Recommended Implementation Order

### Phase 1: Data structure classes

```python
@dataclass
class JumpData:
    """Physical measurements."""
    jump_height_m: float
    flight_time_ms: float
    ...

@dataclass
class VideoInfo:
    """Video characteristics."""
    source_path: str
    fps: float
    resolution: dict[str, int]
    ...

@dataclass
class ProcessingInfo:
    """Processing context."""
    version: str
    timestamp: str
    ...

@dataclass
class AlgorithmConfig:
    """Algorithm configuration."""
    detection_method: str
    ...

@dataclass
class ResultMetadata:
    """Complete metadata."""
    quality: QualityAssessment
    video: VideoInfo
    processing: ProcessingInfo
    algorithm: AlgorithmConfig

@dataclass
class JumpResult:
    """Complete result."""
    data: JumpData
    metadata: ResultMetadata
```

### Phase 2: Update .to_dict() methods

Convert all metrics classes to return `{data, metadata}` structure

### Phase 3: Update API functions

Populate video, processing, algorithm info

### Phase 4: Update tests

Adjust assertions for new structure

### Phase 5: Update documentation

Examples, migration guide

______________________________________________________________________

## Minimal vs Full Implementation

### Minimal (Option A-Prime approach)

**Implement now:**

- ✅ `data` structure
- ✅ `metadata.quality`

**Add later (non-breaking):**

- 📅 `metadata.video`
- 📅 `metadata.processing`
- 📅 `metadata.algorithm`

**Pros:** Smaller initial change
**Cons:** Incomplete, need to add later anyway

### Full (Recommended)

**Implement now:**

- ✅ `data` structure
- ✅ `metadata.quality`
- ✅ `metadata.video`
- ✅ `metadata.processing`
- ✅ `metadata.algorithm`

**Pros:** Complete, nothing to add later
**Cons:** Larger change (but in alpha, who cares?)

______________________________________________________________________

## My Strong Recommendation

**Full Option B implementation now** because:

1. You're in **alpha** - breaking changes are expected and fine
1. You'll need this info for **validation studies** anyway
1. Get it **right once** - no incremental migrations
1. **Professional structure** from day 1
1. **Zero future breaking changes**

The extra work now (adding video/processing/algorithm fields) is minimal compared to the benefit of getting the structure correct permanently.

______________________________________________________________________

## Questions?

1. ✅ **Full Option B implementation?** (data + complete metadata)
1. ⚠️ **Alternative: Minimal Option A-Prime?** (data + quality only, add rest later)

Since you said "full impl now", I interpret this as **Full Option B** - correct?

Let me know and I'll implement it!
