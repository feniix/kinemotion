# Determinism Test Results

**Test Type:** Test-Retest Reliability (Determinism)
**Status:** Ready to run
**Estimated Time:** 30 minutes

______________________________________________________________________

## Purpose

Verify that kinemotion produces **identical results** when processing the **same video** multiple times. This is a fundamental requirement for:

- Scientific validity
- Reproducible research
- Reliable validation studies
- User confidence

**Hypothesis:** Algorithm is deterministic (zero variance across runs)

______________________________________________________________________

## Test Protocol

### Method

1. **Create test dataset**

   - Use single video: `samples/cmjs/cmj.mp4`
   - Create 100 symlinks to same video
   - Process all with batch mode (4 workers)

1. **Process videos**

   ```bash
   kinemotion cmj-analyze data/determinism_test/videos/*.mp4 \
       --batch \
       --workers 4 \
       --json-output-dir data/determinism_test/results \
       --quality balanced
   ```

1. **Compare results**

   - Load all 100 JSON outputs
   - Compare to baseline (first result)
   - Check for any differences

1. **Analyze variance**

   - Calculate std, range for key metrics
   - Identify any non-deterministic behavior
   - Document findings

### Success Criteria

- **PASS:** All 100 runs produce byte-identical JSON output
- **ACCEPTABLE:** Differences only in floating point precision (\< 1e-10)
- **FAIL:** Any metric shows variance > 1e-6

______________________________________________________________________

## Running the Test

### Quick Test (Recommended)

```bash
# Run complete test
./scripts/test_determinism.sh

# Analyze variance
./scripts/analyze_determinism_variance.py
```

### Manual Steps

```bash
# 1. Setup
mkdir -p data/determinism_test/videos

# 2. Create symlinks
for i in $(seq -f "%03g" 1 100); do
    ln -s ../../../samples/cmjs/cmj.mp4 data/determinism_test/videos/test_${i}.mp4
done

# 3. Process
uv run kinemotion cmj-analyze data/determinism_test/videos/*.mp4 \
    --batch --workers 4 \
    --json-output-dir data/determinism_test/results \
    --quality balanced

# 4. Compare
python scripts/analyze_determinism_variance.py
```

______________________________________________________________________

## Expected Results

### Success Output

```text
Comparing 100 result files...
============================================================
✅ SUCCESS: All 100 runs produced identical results

Algorithm is DETERMINISTIC!

This means:
  ✓ Same input always produces same output
  ✓ Results are reproducible
  ✓ No random variation
  ✓ Reliable for validation studies

============================================================
```

### Variance Analysis

```text
Jump Height (m):
  Mean:  0.4540739478
  Std:   0.000000000000000
  Range: 0.000000000000000
  ✅ PERFECT: Zero variance (perfectly deterministic)

Flight Time (s):
  Mean:  0.6085184949
  Std:   0.000000000000000
  Range: 0.000000000000000
  ✅ PERFECT: Zero variance (perfectly deterministic)

Quality Score:
  Mean:  87.5000000000
  Std:   0.000000000000000
  Range: 0.000000000000000
  ✅ PERFECT: Zero variance (perfectly deterministic)

Processing Time Variance: 0.2341s
  (This SHOULD vary - depends on system load)
```

______________________________________________________________________

## What This Tests

### Algorithm Components

- ✅ **Pose tracking:** MediaPipe landmark detection
- ✅ **Smoothing:** Savitzky-Golay filtering, outlier rejection
- ✅ **Phase detection:** CMJ phase identification
- ✅ **Kinematics:** Jump height calculation from flight time
- ✅ **Quality assessment:** Confidence scoring
- ✅ **Metadata generation:** Video info, algorithm config

### System Components

- ✅ **Batch processing:** Parallel worker stability
- ✅ **CLI → API:** Full pipeline determinism
- ✅ **JSON serialization:** Consistent output formatting

______________________________________________________________________

## If Test Fails

### Investigation Steps

1. **Identify which metric varies**

   ```bash
   python scripts/analyze_determinism_variance.py
   ```

   - Shows exactly which fields have variance
   - Helps narrow down the problem

1. **Check for random seeds**

   ```bash
   grep -r "random\|shuffle" src/kinemotion/
   ```

   - Look for unseeded random operations

1. **Check for timestamps in calculations**

   ```bash
   grep -r "time\.time()\|datetime\.now()" src/kinemotion/
   ```

   - Timestamps should only be in metadata
   - Not in measurement calculations

1. **Check MediaPipe version**

   ```bash
   uv run python -c "import mediapipe; print(mediapipe.__version__)"
   ```

   - Ensure consistent MediaPipe version

1. **Test sequentially** (remove parallelism variable)

   ```bash
   # Run 10 times sequentially
   for i in {1..10}; do
       uv run kinemotion cmj-analyze samples/cmjs/cmj.mp4 \
           --json-output data/seq_test/result_${i}.json
   done
   ```

   - If this is deterministic but batch isn't → multiprocessing issue
   - If this also fails → core algorithm issue

### Common Issues and Fixes

### Issue: Timestamps in metadata vary

- **Expected!** Processing time and timestamp SHOULD vary
- **Not a problem** - these are metadata, not measurements
- **Fix:** Exclude these from comparison or accept variance

### Issue: Small floating point differences

- **Acceptable** if std \< 1e-10
- **Cause:** Floating point arithmetic order
- **Fix:** Not needed, this is normal

### Issue: Large variance in measurements

- **Problem!** Algorithm is non-deterministic
- **Fix:** Debug and fix before proceeding

______________________________________________________________________

## Deliverable

After successful test, create results document:

```markdown
# Determinism Test Results - PASSED

**Test Date:** 2025-01-13
**Test Video:** samples/cmjs/cmj.mp4
**Runs:** 100
**Method:** Batch processing (4 workers)
**Result:** ✅ PASS

## Statistics

All measurements showed zero variance:
- Jump height: 0.000000 variance
- Flight time: 0.000000 variance
- All frame indices: identical
- Quality scores: identical

## Conclusion

Kinemotion's algorithm is fully deterministic. Same input video
produces identical output across 100 runs, even with parallel processing.

This confirms:
- Algorithm reliability
- Reproducible results
- Ready for validation studies
- No hidden randomness or instability

**Validation Status:** ✅ Determinism confirmed
```

______________________________________________________________________

## What This Enables

With determinism confirmed, you can:

1. **Proceed with validation roadmap**

   - Test-retest studies meaningful
   - ICC calculations valid
   - Comparison studies reliable

1. **Make scientific claims**

   - "Algorithm proven deterministic (100/100 runs)"
   - Shows rigorous testing
   - Professional credibility

1. **Debug with confidence**

   - If results differ → real problem, not random noise
   - Can reproduce any issue reliably

1. **Trust the tool**

   - Results are stable
   - Not dependent on system state
   - Reproducible research possible

______________________________________________________________________

## Timeline

- **Now:** Run test (~30 minutes)
- **After:** Document results (~15 minutes)
- **Then:** Move to task 1.4 (Known Height Validation)

______________________________________________________________________

## Notes

- Test uses batch mode (real-world usage pattern)
- Tests full CLI → API → processing pipeline
- 100 runs gives high confidence (could reduce to 30-50 for speed)
- Can test drop jump similarly: just change VIDEO path

______________________________________________________________________

Ready to run! Execute:

```bash
./scripts/test_determinism.sh
```
