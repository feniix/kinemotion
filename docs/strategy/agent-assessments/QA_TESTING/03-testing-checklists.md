# QA Testing Implementation Checklists

**Date:** November 17, 2025
**Purpose:** Actionable checklists for each testing phase
**Audience:** QA Engineer + Development Team

______________________________________________________________________

## TASK 1: Ankle Angle Fix Validation (2-3 days)

### Pre-Implementation Checklist

- [ ] Biomechanics specialist reviews foot_index change (get approval)
- [ ] Create snapshot of current test results: `uv run pytest tests/ --cov=kinemotion > baseline_tests.log`
- [ ] Extract current metrics: `python scripts/extract_baseline_metrics.py`
- [ ] Prepare rollback plan (git branch, quick revert)
- [ ] Schedule validation slot (2 hour window)
- [ ] Get real CMJ video for validation testing
- [ ] Prepare foot_index test cases (copy from BIOMECHANICS_ANALYSIS.md)

### Implementation Checklist (Biomechanics + Backend)

**File: `src/kinemotion/cmj/joint_angles.py`**

- [ ] Update `calculate_ankle_angle()` function

  - [ ] Add foot_index landmark support (primary)
  - [ ] Add heel fallback (if foot_index unavailable)
  - [ ] Update docstring with biomechanical explanation
  - [ ] Add confidence threshold check (>0.3)

- [ ] Add `validate_joint_angles()` function (NEW)

  - [ ] Ankle bounds: 70-135°
  - [ ] Knee bounds: 80-185°
  - [ ] Hip bounds: 60-195°
  - [ ] Returns dict of validation results

- [ ] Integrate validation into `calculate_triple_extension()`

  - [ ] Call validate_joint_angles() after calculations
  - [ ] Log warnings for out-of-bounds angles
  - [ ] Don't fail, just report

### Testing Checklist (QA)

**File: `tests/test_cmj_joint_angles.py`**

- [ ] Add foot_index vs heel comparison test

  - [ ] Verify foot_index gives different angle (>10° difference)
  - [ ] Verify fallback to heel works
  - [ ] Verify returns None if neither available

- [ ] Add phase progression test

  - [ ] Ankle: lowest point (80°) → takeoff (120°)
  - [ ] Knee: lowest point (95°) → takeoff (170°)
  - [ ] Hip: lowest point (100°) → takeoff (175°)

- [ ] Add bounds validation tests

  - [ ] All 3 joints within physiological limits
  - [ ] Test with edge case landmarks (extreme positions)

- [ ] Add real video validation

  - [ ] Process real CMJ video
  - [ ] Verify ankle increases 20°+ during concentric
  - [ ] Compare with published research ranges

### Validation Checklist

- [ ] Run full test suite: `uv run pytest tests/`

  - [ ] All tests passing? ✓
  - [ ] No new failures? ✓

- [ ] Compare metrics against baseline

  - [ ] CMJ height: \<2% change acceptable
  - [ ] Flight time: \<2% change acceptable
  - [ ] RSI: \<2% change acceptable

- [ ] Manual validation with real video

  - [ ] Load real CMJ video
  - [ ] Check ankle angles reasonable (110-130° at takeoff)
  - [ ] Compare knee/hip with ankle (should be similar progression)

- [ ] Review with biomechanics specialist

  - [ ] Do new angles match expected ranges?
  - [ ] Does foot_index capture plantarflexion better?
  - [ ] Any concerns before shipping?

### Rollback Checklist (If Needed)

- [ ] Git revert: `git revert <commit-hash>`
- [ ] Re-run tests: `uv run pytest tests/`
- [ ] Verify metrics back to baseline
- [ ] Document root cause
- [ ] Plan re-implementation for next attempt

### Success Criteria

✓ All tests passing
✓ Ankle angles increase 20°+ during concentric phase
✓ Metrics within \<2% of baseline
✓ Real video validation approved by specialist
✓ No regressions in knee/hip angles
✓ Confidence in foot_index implementation high

______________________________________________________________________

## TASK 2: CMJ Testing Expansion (3-4 days)

### Preparation Checklist (Day 1)

- [ ] Design test structure

  - [ ] Create `tests/test_cmj_phase_progression.py`
  - [ ] Create `tests/test_cmj_physiological_bounds.py`
  - [ ] Create `tests/test_cmj_real_video.py`

- [ ] Set up test fixtures

  - [ ] `conftest.py` fixture for phase landmark generation
  - [ ] Fixture for realistic landmark sequences
  - [ ] Fixture for synthetic test video creation

- [ ] Prepare test data

  - [ ] Create synthetic CMJ video (good technique)
  - [ ] Create synthetic CMJ video (poor technique)
  - [ ] Create realistic landmark sequences for all phases

### Phase Progression Tests (Day 1-2)

**File: `tests/test_cmj_phase_progression.py`**

```
Required Tests: 8-10 tests

Test 1: Ankle increases from lowest to takeoff
├─ Input: landmarks_lowest, landmarks_takeoff
├─ Assert: ankle_takeoff > ankle_lowest
└─ Assert: difference > 20°

Test 2: Knee increases from lowest to takeoff
├─ Input: landmarks_lowest, landmarks_takeoff
├─ Assert: knee_takeoff > knee_lowest
└─ Assert: difference > 75°

Test 3: Hip increases from lowest to takeoff
├─ Input: landmarks_lowest, landmarks_takeoff
├─ Assert: hip_takeoff > hip_lowest
└─ Assert: difference > 75°

Test 4-6: Same for intermediate phases
├─ eccentric_start → lowest
├─ lowest → concentric_mid
└─ concentric_mid → takeoff

Test 7-10: Synchronized extension validation
├─ All joints extend together (timing)
├─ No premature extension
├─ Smooth progression (no drops)
└─ Final angles within ranges
```

**Checklist:**

- [ ] All 8-10 tests written
- [ ] All tests passing with current code
- [ ] Coverage estimate: +5-6%
- [ ] Code review completed

### Physiological Bounds Tests (Day 2)

**File: `tests/test_cmj_physiological_bounds.py`**

```
Required Tests: 12-15 tests

Ankle Bounds Tests (70-135°):
├─ 3 tests with dorsiflexed landmarks (70°)
├─ 3 tests with neutral landmarks (90°)
├─ 3 tests with plantarflexed landmarks (120°)
└─ 3 tests with extreme positions (edge cases)

Knee Bounds Tests (80-185°):
├─ 3 tests with flexed (90°)
├─ 3 tests with extended (170°)
└─ 3 tests with edge cases (80°, 185°)

Hip Bounds Tests (60-195°):
├─ 3 tests with flexed (90°)
├─ 3 tests with extended (175°)
└─ 3 tests with edge cases (60°, 195°)

Out-of-Bounds Detection:
├─ 1 test: ankle >135° detected
├─ 1 test: knee <80° detected
├─ 1 test: hip >195° detected
└─ 1 test: multiple out-of-bounds
```

**Checklist:**

- [ ] All 12-15 tests written
- [ ] All tests passing with current code
- [ ] Coverage estimate: +4-5%
- [ ] Parametrized tests used for efficiency
- [ ] Code review completed

### Real Video Validation Tests (Day 3)

**File: `tests/test_cmj_real_video_validation.py`**

```
Required Tests: 4-6 tests

Test 1: Good athlete video
├─ Input: synthetic_cmj_good_technique.mp4
├─ Process: process_cmj_video()
├─ Assert: ankle_takeoff > 110°
├─ Assert: knee_takeoff > 165°
├─ Assert: hip_takeoff > 170°
└─ Assert: synchronization_score > 0.8

Test 2: Poor athlete video
├─ Input: synthetic_cmj_poor_knee_extension.mp4
├─ Process: process_cmj_video()
├─ Assert: knee_takeoff < 160° (incomplete)
└─ Assert: synchronization_score < 0.6

Test 3: Foot_index vs heel comparison
├─ Input: real CMJ video
├─ Calculate: angles with foot_index
├─ Calculate: angles with heel (fallback)
└─ Assert: difference > 10° (meaningful)

Test 4: Different video qualities
├─ Input: good_quality.mp4, poor_quality.mp4
├─ Assert: metrics within 5% tolerance
└─ Assert: both return valid results

Test 5: Different camera angles
├─ Input: straight_angle.mp4, tilted_5deg.mp4
├─ Assert: metrics within 5% tolerance
└─ Assert: robust to angle variations

Test 6: Edge cases
├─ Partial visibility (one side occluded)
├─ Low confidence landmarks
├─ Multiple peaks in video
└─ Assert: handles gracefully
```

**Checklist:**

- [ ] All 4-6 tests written
- [ ] Synthetic video generation working
- [ ] All tests passing with current code
- [ ] Coverage estimate: +3-4%
- [ ] Code review completed

### Coverage Verification (Day 4)

- [ ] Run coverage: `uv run pytest tests/test_cmj*.py --cov=kinemotion.cmj`

- [ ] Parse coverage report

  - [ ] CMJ module coverage: 62% → target 80%+
  - [ ] Joint angles: high coverage
  - [ ] Phase detection: well covered
  - [ ] Analysis functions: >80%

- [ ] If coverage \<80%:

  - [ ] Identify uncovered code
  - [ ] Add targeted tests
  - [ ] Re-run coverage

- [ ] Code review final

  - [ ] Test quality high
  - [ ] No flaky tests
  - [ ] Good documentation

### Success Criteria

✓ CMJ coverage: 62% → 80%+
✓ 40-50 new tests added
✓ All tests passing
✓ Phase progression validated
✓ Physiological bounds validated
✓ Real video discrimination working
✓ Code review approved
✓ Documentation complete

______________________________________________________________________

## TASK 3: Real-Time Performance Testing (Weeks 1-2)

### Week 1: Baseline Profiling Checklist

**Day 1-2: Setup Infrastructure**

- [ ] Create `tests/test_realtime_latency.py`
- [ ] Create `src/kinemotion/realtime/profiling.py` (LatencyProfiler class)
- [ ] Create latency measurement fixtures
- [ ] Set up WebSocket test server
- [ ] Prepare test frames (various resolutions)

**Day 3-4: Single Client Profiling**

```python
Tests to Run:

1. Single Frame Latency
   ├─ Input: 480x640 frame, 30fps
   ├─ Measure: E2E latency
   ├─ Target P50: <150ms
   └─ Target P99: <200ms

2. MediaPipe Inference
   ├─ Input: 100 frames
   ├─ Measure: inference time only
   ├─ Target P50: <50ms
   └─ Target P95: <60ms

3. Metric Calculation
   ├─ Input: MediaPipe results
   ├─ Measure: metric calc time
   └─ Target: <10ms

4. JSON Serialization
   ├─ Input: metrics dict
   ├─ Measure: serialization time
   └─ Target: <5ms

5. WebSocket Send
   ├─ Input: JSON payload
   ├─ Measure: network roundtrip
   └─ Target: <50ms
```

**Checklist:**

- [ ] Test 1 (single frame): P50 \<150ms measured ✓
- [ ] Test 2 (inference): P50 \<50ms measured ✓
- [ ] Test 3-5 (other stages): Profiles collected
- [ ] Bottleneck identified (usually MediaPipe)
- [ ] Results saved to baseline

**Decision Point:**

- If P50 \<150ms → PROCEED with Week 2 ✓
- If P50 150-200ms → PROCEED but plan optimization
- If P50 >200ms → ESCALATE, investigate causes

### Week 2: Load Testing Checklist

**Day 1-2: Setup Load Testing**

- [ ] Install load testing tools

  - [ ] Apache JMeter (WebSocket plugin)
  - [ ] Locust (Python-based)
  - [ ] Or custom asyncio solution

- [ ] Create load test scenarios

  - [ ] Ramp-up: 1→50 clients over 5 min
  - [ ] Sustained: 25 clients for 30 min
  - [ ] Spike: 10→100→10 clients
  - [ ] Stress: 100+ clients until failure

- [ ] Implement monitoring

  - [ ] CPU/memory tracking
  - [ ] Latency percentiles (P50, P95, P99)
  - [ ] Error rates
  - [ ] Connection drop rates

**Day 3-4: Run Load Tests**

```
Scenario 1: Ramp-Up (1→50 clients)
├─ Duration: 5 minutes
├─ Goal: P95 latency <180ms
├─ Expected: Linear increase until bottleneck
└─ Measure: When P95 crosses 180ms

Scenario 2: Sustained (25 clients)
├─ Duration: 30 minutes
├─ Goal: Stable latency, 0 crashes
├─ Watch for: Memory leaks, degradation
└─ Measure: Mean latency stable over time

Scenario 3: Spike (10→100→10)
├─ Duration: 5 minutes total
├─ Goal: Handle spike without crashes
├─ Measure: Recovery time to normal
└─ Check: No data loss during spike

Scenario 4: Stress (100+ clients)
├─ Duration: Until failure
├─ Goal: Find breaking point
├─ Measure: What % clients fail at each level
└─ Document: Failure mode (latency spike vs crash)
```

**Checklist:**

- [ ] Scenario 1 complete: P95 \<180ms at 50 clients
- [ ] Scenario 2 complete: 30-min sustained OK
- [ ] Scenario 3 complete: Handles spike
- [ ] Scenario 4 complete: Failure point identified
- [ ] Monitoring data collected
- [ ] Report generated

### Success Criteria (Week 2)

✓ Single client: P50 \<150ms, P99 \<200ms
✓ 10 clients: P95 \<180ms, 0% error rate
✓ 50 clients: P99 \<200ms, \<0.1% drops
✓ 100 clients: Identify failure mode
✓ Bottleneck: MediaPipe inference identified
✓ Optimization plan: Created if needed

### Optimization Checklist (If Needed)

If P99 latency >200ms at 50 clients:

- [ ] Profile MediaPipe inference

  - [ ] Try GPU acceleration
  - [ ] Try Lite model instead of Full
  - [ ] Reduce frame resolution

- [ ] Profile network layer

  - [ ] Implement frame dropping for older frames
  - [ ] Use binary protocol instead of JSON
  - [ ] Implement delta encoding (send deltas, not full metrics)

- [ ] Profile processing

  - [ ] Batch frame processing
  - [ ] Move non-critical calculations to async task
  - [ ] Cache intermediate results

- [ ] Re-test after optimizations

  - [ ] Measure new latency
  - [ ] Confirm \<200ms achieved
  - [ ] Document changes

______________________________________________________________________

## TASK 4: Running Validation Without Lab (2-3 weeks)

### Preparation Checklist (Week 1)

- [ ] Create `tests/test_running_validation.py`

- [ ] Research published running biomechanics (Lieberman, Buist, etc.)

- [ ] Create synthetic running video generation

- [ ] Define metrics:

  - [ ] Ground contact time (GCT)
  - [ ] Cadence (steps/min)
  - [ ] Stride length
  - [ ] Landing pattern (heel/midfoot/forefoot)

- [ ] Set up crowdsourcing (if using real athletes)

  - [ ] Create survey form
  - [ ] Recruit 10-20 runners
  - [ ] Collect self-reported metrics
  - [ ] Record videos

### Level 1: Published Research Validation (Week 1)

**Checklist:**

```
GCT (Ground Contact Time) Ranges:
├─ Elite sprinter:     0.08-0.15s
├─ Elite distance:     0.25-0.35s
├─ Recreational:       0.35-0.50s
└─ Poor technique:     0.50-0.70s

Cadence (Steps/Minute):
├─ Slow:     140-160 spm
├─ Optimal:  160-180 spm
└─ Fast:     180-200 spm

Stride Length (varies by height):
├─ 160cm:    0.90-1.20m
├─ 170cm:    1.00-1.35m
└─ 180cm:    1.10-1.50m
```

- [ ] Create synthetic videos matching each range

  - [ ] Elite sprinter (0.10s GCT, 190 spm)
  - [ ] Recreational (0.42s GCT, 170 spm)
  - [ ] Beginner (0.55s GCT, 155 spm)

- [ ] Test algorithm against each profile

  - [ ] Measured GCT matches expected range
  - [ ] Measured cadence matches expected range
  - [ ] Measured stride length matches height

- [ ] Add test cases:

  ```python
  def test_gct_recreational_range():
      """GCT for recreational runner should be 0.35-0.50s."""
      video = create_synthetic_running_video(gct_seconds=0.42)
      metrics = process_running_video(video)
      assert 0.35 <= metrics["gct"] <= 0.50

  def test_cadence_optimal_range():
      """Optimal cadence should be 160-180 spm."""
      video = create_synthetic_running_video(cadence_spm=170)
      metrics = process_running_video(video)
      assert 160 <= metrics["cadence"] <= 180

  def test_stride_length_by_height():
      """Stride length should scale with height."""
      for height_cm, expected_range in [
          (160, (0.90, 1.20)),
          (170, (1.00, 1.35)),
          (180, (1.10, 1.50)),
      ]:
          video = create_synthetic_running_video(height_cm=height_cm)
          metrics = process_running_video(video)
          assert expected_range[0] <= metrics["stride"] <= expected_range[1]
  ```

- [ ] Verify tests pass with algorithm

- [ ] Document research sources

### Level 2: Consistency Testing (Week 1-2)

**Checklist:**

```
Test 1: Repeatability
├─ Same video analyzed twice
└─ Assert: Metrics identical

Test 2: Angle Robustness
├─ Same run, ±5° camera angle
├─ Assert: Metrics within 5% tolerance
└─ Validates: Not sensitive to angle

Test 3: Asymmetry Detection
├─ Left leg 0.35s GCT, right leg 0.45s GCT
├─ Assert: Algorithm detects >20% asymmetry
└─ Validates: Can discriminate technique

Test 4: Frame Rate Robustness
├─ 30fps video, 60fps video, 120fps video
├─ Assert: Metrics consistent across frame rates
└─ Validates: Not artifacts of sampling
```

- [ ] Add test cases:

  ```python
  def test_gct_repeatable_same_video():
      """Same video should give same GCT."""
      video = create_synthetic_running_video()
      metrics1 = process_running_video(video)
      metrics2 = process_running_video(video)
      assert abs(metrics1["gct"] - metrics2["gct"]) < 0.01

  def test_metrics_stable_across_angles():
      """Metrics should be similar from different angles."""
      base_video = create_synthetic_running_video(gct_seconds=0.40)
      tilted_video = create_synthetic_running_video(
          gct_seconds=0.40,
          camera_angle=85  # 5° tilt
      )
      m1 = process_running_video(base_video)
      m2 = process_running_video(tilted_video)
      assert abs(m1["gct"] - m2["gct"]) / m1["gct"] < 0.05  # 5% tolerance

  def test_asymmetry_detection():
      """Algorithm should detect >20% asymmetry."""
      video = create_synthetic_running_video(
          left_gct_seconds=0.35,
          right_gct_seconds=0.45
      )
      metrics = process_running_video(video)
      asymmetry = abs(metrics["left_gct"] - metrics["right_gct"]) / \
                  np.mean([metrics["left_gct"], metrics["right_gct"]]) * 100
      assert asymmetry > 20
  ```

- [ ] Verify tests pass

- [ ] Document assumptions

### Level 3: Crowdsourced Validation (Week 2-3)

**Checklist:**

- [ ] Recruit athletes (or use synthetic data)

  ```
  Athlete profiles:
  ├─ 5 elite runners (GCT <0.30s)
  ├─ 10 recreational (GCT 0.35-0.50s)
  └─ 5 beginners (GCT 0.50-0.70s)
  ```

- [ ] Collect data from athletes

  - [ ] Video recording
  - [ ] Self-reported GCT (if they know it)
  - [ ] Self-reported cadence
  - [ ] Fitness level assessment

- [ ] Add validation tests:

  ```python
  def test_metrics_correlate_with_fitness_level():
      """Metrics should match fitness level."""
      elite_video = get_elite_runner_video()
      recreational_video = get_recreational_runner_video()

      elite_metrics = process_running_video(elite_video)
      rec_metrics = process_running_video(recreational_video)

      assert elite_metrics["gct"] < rec_metrics["gct"]
      assert elite_metrics["cadence"] > rec_metrics["cadence"]

  def test_gct_error_within_tolerance():
      """Measured GCT within 15% of self-reported."""
      for athlete in test_athletes:
          video = athlete.video
          self_reported = athlete.self_reported_gct

          measured = process_running_video(video)["gct"]
          error = abs(measured - self_reported) / self_reported * 100

          assert error < 15, \
              f"{athlete.name}: {error:.1f}% error (>15%)"
  ```

- [ ] Create validation report

  - [ ] Comparison vs published ranges
  - [ ] Correlation with fitness level
  - [ ] Error analysis
  - [ ] Recommendations

### Success Criteria

✓ Published research: All metrics within 5% of expected ranges
✓ Consistency: Same video gives same metrics (repeatability \<1%)
✓ Robustness: 5% tolerance across camera angles
✓ Asymmetry: Can detect >20% asymmetry (good/poor technique)
✓ Athlete correlation: Elite \< Recreational \< Beginner (GCT)
✓ Error rate: \<15% vs self-reported metrics
✓ No lab equipment needed: All validation non-invasive

______________________________________________________________________

## REGRESSION PREVENTION: Continuous Integration (All Phases)

### CI/CD Checklist (Setup Week 1)

**File: `.github/workflows/regression-tests.yml`**

- [ ] Create regression test job

  - [ ] Runs on every push/PR
  - [ ] Compares metrics against baseline
  - [ ] Fails if regression >2%

- [ ] Create performance test job

  - [ ] Runs latency benchmarks
  - [ ] Compares against baseline
  - [ ] Fails if latency degrades >10%

- [ ] Create coverage enforcement

  - [ ] Fails if coverage drops
  - [ ] Requires 70%+ critical path coverage
  - [ ] Requires CMJ ≥80% after Task 2

**Checklist:**

- [ ] Baseline metrics snapshots created

  - [ ] `metrics_baseline.json` saved
  - [ ] Committed to repo
  - [ ] Version tracked

- [ ] Regression test suite created

  - [ ] All task regression tests implemented
  - [ ] CI job configured
  - [ ] Passing locally

- [ ] Performance monitoring set up

  - [ ] Latency benchmarks in CI
  - [ ] Memory profiling
  - [ ] Resource tracking

- [ ] Coverage gates installed

  - [ ] CMJ ≥80% required (Task 2+)
  - [ ] API ≥70% required (Task 5)
  - [ ] No decrease allowed

### Daily Checklist (Throughout Project)

- [ ] Morning: Check overnight CI results

  - [ ] All tests passing?
  - [ ] Coverage maintained?
  - [ ] Performance stable?

- [ ] Before commit: Run locally

  - [ ] `uv run pytest tests/` passing
  - [ ] `uv run pytest --cov` shows coverage
  - [ ] No performance regressions

- [ ] After merge: Monitor CI

  - [ ] Regression tests pass?
  - [ ] Coverage gates passed?
  - [ ] No flaky test failures?

### Success Criteria

✓ Zero regressions in core metrics (GCT, RSI, height)
✓ Zero regressions in API contracts
✓ Coverage maintained ≥74% (increasing per task)
✓ Performance stable (latency ±10%)
✓ All tests passing consistently
✓ CI/CD fully automated

______________________________________________________________________

## FINAL SUCCESS METRICS

### Task 2 Completion (Week 1-2)

- [ ] CMJ coverage: 62% → 80%+
- [ ] 40-50 new tests added
- [ ] All tests passing
- [ ] Code review approved

### Task 3 Completion (Week 4-6)

- [ ] Real-time latency: \<200ms P99 @ 50 clients
- [ ] WebSocket stable: 0% drops at normal load
- [ ] Load test complete: Failure mode identified
- [ ] Performance regression: \<10% acceptable

### Task 4 Completion (Week 5-7)

- [ ] Running metrics: Within published ranges
- [ ] Validation: 3-tier approach complete
- [ ] Consistency: \<5% variation across conditions
- [ ] Athlete correlation: Elite \< Rec \< Beginner

### Overall Roadmap (Month 6)

- [ ] Total coverage: 85-90% (up from 74%)
- [ ] Regressions detected: Zero in production
- [ ] Performance stable: \<±10% variance
- [ ] All 5 tasks complete and validated
- [ ] 3-sport platform operational
- [ ] Real-time demo live
- [ ] APIs accepting requests

______________________________________________________________________

**Checklist Status:** Ready for implementation
**Next Step:** Schedule Week 1 latency baseline testing
**Last Updated:** November 17, 2025
