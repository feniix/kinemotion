---
title: drop-jump-vs-cmj-key-differences
type: note
permalink: biomechanics/drop-jump-vs-cmj-key-differences
tags:
- biomechanics
- algorithms
- metrics
---

# Drop Jump vs CMJ - Key Differences

## Comparison Table

| Feature | Drop Jump | CMJ |
|---------|-----------|-----|
| Starting Position | Elevated box | Floor level |
| Search Algorithm | Forward search | Backward search from peak |
| Velocity Calculation | Absolute (magnitude only) | Signed (direction matters) |
| Key Metric | Ground contact time (GCT) | Jump height from flight time |
| Reactive Strength | RSI = Jump height / GCT | N/A |
| Auto-Tuning | Quality presets | Quality presets |
| Countermovement | N/A | Measured from lowest point |
| Triple Extension | N/A | Ankle, knee, hip angles |

## Drop Jump Algorithm

1. **Search pattern**: Forward scan from box exit
2. **Metrics calculated**:
   - Ground contact time (GCT)
   - Flight time
   - Reactive Strength Index (RSI) = jump_height / GCT
3. **Velocity use**: Absolute magnitude
4. **Implementation**: src/kinemotion/dropjump/

## CMJ Algorithm

1. **Search pattern**: Backward from peak (find highest point first)
2. **Metrics calculated**:
   - Jump height (derived from flight time)
   - Countermovement depth (lowest point in descent)
   - Triple extension: ankle plantarflexion, knee, hip angles
3. **Velocity use**: Signed (positive = upward, negative = downward)
4. **Critical detail**: Use **foot_index** (not heel) for accurate ankle plantarflexion
5. **Implementation**: src/kinemotion/cmj/

## Why Different Algorithms?

- **Drop Jump**: Starts from known position (box), easier to detect contact → forward search efficient
- **CMJ**: Contact point ambiguous on floor → find peak first (easiest to detect), work backward

## Critical Gotchas

### Shared
- Read first actual frame for dimensions (not OpenCV properties)
- Handle rotation metadata from mobile videos
- Convert NumPy types to native Python for JSON

### CMJ Specific
- Use **signed velocity** (not absolute)
- Backward search algorithm mandatory
- Lateral view required for accurate angles
- Ankle angle MUST use `foot_index` for plantarflexion accuracy

## Testing Strategy

- **Drop Jump**: Forward search validation, RSI calculation tests
- **CMJ**: Backward search validation, phase progression tests, physiological bounds checks
