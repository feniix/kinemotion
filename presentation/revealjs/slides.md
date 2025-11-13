---
title: Kinemotion
theme: black
revealOptions:
  transition: slide
  controls: true
  progress: true
  center: true
  hash: true
  width: 1280
  height: 720
  margin: 0.04
  minScale: 0.2
  maxScale: 2.0
permalink: presentation/revealjs/slides
---

# **Kinemotion**

### Video-Based Kinematic Analysis for Athletic Performance

#### A Hobby Project Exploration

**Presenter**: Sebastian Otaegui
**Date**: November 13, 2025

*"Transform properly recorded smartphone videos into actionable athletic performance data"*

Note: Welcome everyone. Quick show of hands about video analysis experience. Remember to check if screen is visible to all. This is a hobby project - set informal tone.

---

## Current Jump Analysis Landscape

### Expensive Lab Equipment

- **Force plates**: $10,000-50,000 (gold standard)
- **3D motion capture**: $100,000+ setup costs
- **Jump mats**: $500-2,000, limited metrics

Note: Each tool serves different needs. Personal experience: needed something between mobile apps and research tools. Motivation: combine best of both worlds.

---

### Existing Software Solutions

#### My Jump Lab (Phone App)

- ✅ Widespread adoption, automated
- ✅ iOS/Android support, premium features
- ✅ Research validated (Haynes et al., 2019)
- ⚡ Mobile-first design
- ⚡ Best for quick field assessments

#### Tracker (opensourcephysics.org)

- ✅ Research-grade precision
- ✅ Very powerful analysis capabilities
- ⚡ Designed for physics education
- ⚡ Manual control over every parameter

---

### The Opportunity

> Space for: Open-source solution optimized for athletic performance analysis

Note: Respect existing solutions while showing the gap. Transition: "So I built Kinemotion to explore this space..."

---

## Kinemotion: Where It Fits

### What Makes Kinemotion Different

| Aspect | My Jump Lab | Tracker | **Kinemotion** |
|--------|-------------|---------|----------------|
| **Automation** | Fully Automated | Manual | **Fully automated** |
| **Open Source** | No | Yes | **Yes (MIT)** |
| **Learning Curve** | Low | Very High | **Low** |
| **Batch Processing** | No | No | **Yes** |
| **Extensibility** | No | Limited | **API + CLI** |

Note: My Jump Lab is research-validated. Kinemotion uses research-based methods but awaits validation. Each tool has its place - Kinemotion fills a specific gap in the open-source space. Community can contribute and adapt.

---

### Technical Advantages

- **MediaPipe AI**: 33 body landmarks tracked automatically
- **Auto-tuning**: Adapts to video quality/framerate
- **Multiple algorithms**: Forward search (drop), backward search (CMJ)
- **Sub-frame interpolation**: Precision beyond frame boundaries

Note: Focus on what we learned from using these tools.

---

## Technical Architecture

### How It Works

```text
Video Input → Pose Detection → Kinematic Analysis → Metrics Output
```

### Technical Stack

- **Core**: Python 3.12, NumPy, OpenCV
- **AI/ML**: MediaPipe Pose (Google) - tracks 33 body points
- **Signal Processing**: Savitzky-Golay filter - smooths noisy pose data
- **Analysis**: Derivative kinematics - velocity/acceleration from position
- **Quality**: Type-safe, CI/CD pipeline, automated testing

Note: Pose detection is NOISY - show jitter example if time. S-G filter = removes noise, keeps peaks (aerospace example). This took considerable time to get right.

---

### Algorithm Strategy: Forward Search

**Key Insight**: Start with the most reliable event for each jump type

**Drop Jump → Forward Search**

```text
Landing (box) → Takeoff → Landing (ground)
     ↓           ↓            ↓
  [Start]    [Search →]    [Search →]
```

**Why Forward Search?**

- Landing from box = high-impact event (easy to detect)
- Clear acceleration signature at contact
- Search forward from reliable starting point

Note: This algorithmic choice is critical. Drop jump has clear landing event from box. The impact creates an unmistakable signal in the position data. Starting from the most reliable event improves detection accuracy.

---

### Algorithm Strategy: Backward Search

**CMJ → Backward Search**

```text
Standing ← Lowest Point ← Takeoff ← Peak
      ↓        ↓            ↓        ↓
[Search ←] [Search ←]  [Search ←] [Start]
```

**Why Backward Search?**

- Peak (apex) = most reliable turning point (velocity = 0)
- No clear ground contact to detect (starts on floor)
- Search backward from peak to find takeoff, then phases

**Key Difference:**

- Drop jump: Clear landing event → forward search
- CMJ: Clear peak event → backward search

Note: Took considerable experimentation to realize backward search works better for CMJ. The peak is unambiguous - it's where vertical velocity becomes zero. Working backward from there is more robust than trying to detect the subtle start of countermovement.

---

## Jump Analysis Types

### Recording Requirements

**Both jump types require:**

- **Camera Angle**: 45° preferred, sagittal acceptable
- **Frame Rate**: 60+ fps preferred, 30 fps minimum
- **Distance**: 2-5 meters from subject
- **Lens**: Standard or telephoto (never wide angle)
- **Lighting**: Good visibility of full body

Note: These requirements apply to both drop jumps and CMJs. Emphasize 45-degree angle preference. Sagittal = side view (anatomical term for lateral perspective showing body profile).

---

## Drop Jump Analysis

### What We Measure

**Key Metrics:**

- Ground Contact Time (<250ms for fast SSC)
- Flight Time
- Reactive Strength Index (RSI)
- Jump Height from flight time

**Algorithm:** Forward search from box landing

**Use Cases:**

- Plyometric training assessment
- Return-to-sport testing
- Reactive strength monitoring

Note: Forward search algorithm detailed in previous slide. RSI is the gold standard for plyometric assessment. Fast SSC (stretch-shortening cycle) is defined as GCT <250ms. Trained athletes typically achieve 150-250ms.

---

## Counter Movement Jump (CMJ)

### What We Measure

**Key Metrics:**

- Jump Height (flight time method)
- Countermovement Depth
- Triple Extension angles
- Phase Durations (eccentric/concentric)

**Algorithm:** Backward search from peak

**Use Cases:**

- Basketball/volleyball performance
- ACL injury prevention screening
- Lower body power assessment

Note: Backward search - find peak first, work backward. Triple extension is unique to CMJ analysis. More complex than drop jump.

---

## Live Demo Scenarios

<div style="font-size: 0.85em;">

*See It In Action*

### Demo 1: Single Video Analysis

```bash
kinemotion dropjump-analyze sample_data/IMG_5809.MOV
```

### Demo 2: Debug Visualization

```bash
kinemotion dropjump-analyze sample_data/IMG_5809.MOV --output debug.mp4
```

</div>

Note: Demo 1: Show real-time processing speed. Demo 2: Point out pose tracking, phase detection. Time check: 8-10 minutes total for demos.

---

<div style="font-size: 0.85em;">

### Demo 3: Batch Processing

```python
from kinemotion import process_dropjump_videos_bulk, DropJumpVideoConfig

configs = [DropJumpVideoConfig(video_path=str(v)) for v in video_files]
results = process_dropjump_videos_bulk(configs=configs, max_workers=4)
```

### Demo 4: Python API Integration

```python
from kinemotion import process_dropjump_video

metrics = process_dropjump_video("sample_data/IMG_5809.MOV")
print(f"Jump Height: {metrics.jump_height:.3f}m")
print(f"GCT: {metrics.ground_contact_time * 1000:.0f}ms")
print(f"RSI: {metrics.jump_height / metrics.ground_contact_time:.2f}")
```

</div>

Note: Demo 3: Emphasize batch capabilities for teams. Demo 4: Show extensibility for custom workflows. Have backup videos ready if live demo fails.

---

## Real-World Results

<div style="font-size: 0.85em;">

### Code Quality Metrics

- **Type Safety**: 100% (pyright strict)
- **Code Duplication**: < 3%
- **Automated Testing**: 206 comprehensive tests
- **CI/CD**: GitHub Actions + SonarCloud

### Processing Performance

- Processing speed: ~3.5x video length (M1 Pro, 1080p@60fps)
- Examples: 2s video = 8s, 5s video = 17s, 7s video = 25s
- Batch 100 videos: ~4-5 minutes (4 workers, parallel)
- *Performance varies with resolution and hardware*

</div>

Note: Emphasize engineering quality (type safety, testing). Processing speed enables real-world use.

---

### Important Disclaimer

⚠️ **Not yet validated against force plates**

- Consistent measurements ✓
- Relative tracking ✓
- Absolute accuracy: Under development

### Development Status

🔬 **Ongoing Refinement Required**

- Detection errors still occur in some scenarios
- Need extensive field testing with diverse athletes
- Gathering more video samples across conditions
- Continuous algorithm fine-tuning in progress

Note: Be transparent about validation status and current limitations. Detection isn't perfect - occasional errors with occlusion, lighting, or unusual movements. Need more real-world data to improve robustness. This is active development, not a finished product.

---

## Integration & Adoption

<div style="font-size: 0.75em;">

### Installation

```bash
pip install kinemotion
```

### Two Ways to Use

**1. Command Line** (coaches, researchers)

```bash
# Single video
kinemotion cmj-analyze sample_data/IMG_5813.MOV

# Batch with CSV summary
kinemotion cmj-analyze sample_data/*.MOV --batch --csv-summary results.csv
```

**2. Python API** (developers, automation)

```python
from kinemotion import process_cmj_video
metrics = process_cmj_video("sample_data/IMG_5813.MOV")
```

</div>

Note: Simple pip install - no complex setup. CLI includes JSON output for each video and optional CSV summary for batch processing. Python API for custom workflows and integrations.

---

## Key Lessons Learned

- **Pose estimation is noisy**: MediaPipe requires careful filtering
- **Physics helps validate**: Biomechanical constraints catch errors
- **Edge cases are endless**: Occlusion, lighting, unusual movements
- **Open source accelerates**: Building on proven research and tools

Note: Brief mention of challenges. Can elaborate if audience asks questions. Keep moving to maintain momentum.

---

## Code Architecture Deep Dive

<div style="font-size: 0.9em;">

### Modular Design

```python
kinemotion/
├── core/           # Shared algorithms
├── dropjump/       # Drop jump specific
├── cmj/            # CMJ specific
└── api.py          # Public interface
```

### Key Design Decisions

- **Separation of concerns**: Jump types as plugins
- **Dependency injection**: Configurable processors
- **Type safety**: Full typing with pyright
- **Testability**: 206 tests, mocked video I/O

</div>

Note: Protocol pattern enables new jump types. Each jump type is self-contained. Core algorithms are shared.

---

### Extensibility Example

<div style="font-size: 0.9em;">

```python
class JumpAnalyzer(Protocol):
    def detect_phases(self, positions: NDArray) -> Phases
    def calculate_metrics(self, phases: Phases) -> Metrics
```

</div>

Note: This is illustrative code showing the design pattern, not exact implementation. Type safety catches errors at development time. Show GitHub if audience is interested. Mention PR welcome for new movements.

---

## Research Foundation

### Built on Peer-Reviewed Methods

| Technology | Validation |
|------------|------------|
| **Pose Estimation** | MediaPipe validated for sports (Yamaki, 2025; Lyu, 2025) |
| **Jump Height** | Flight time method refined (Nishioka, 2024) |
| **Signal Processing** | Savitzky-Golay filtering (Crenna, 2021) |
| **RSI Metric** | Meta-analysis across studies (Ramirez-Campillo, 2023) |

Note: All technical choices backed by recent research (2021-2025). Not reinventing the wheel - applying and combining proven methods. Can provide full citations if audience interested.

---

## Open Source & Reproducible

### Why This Matters

✓ **Transparent methodology** - All algorithms documented and visible

✓ **Community verification** - Anyone can validate the methods

✓ **Peer-reviewed foundations** - Built on established research

✓ **MIT License** - Free to use, modify, and extend

### Collaboration Welcome

GitHub: github.com/feniix/kinemotion

Note: Open source is critical for scientific tools. Allows independent validation, community improvements, and adaptation for specific use cases. Encourages collaboration over competition.

---

## Future Roadmap

<div style="font-size: 0.9em;">

### Immediate Priorities

- **Field testing & validation**: Gather diverse video samples
- **Algorithm refinement**: Reduce detection errors
- **Edge case handling**: Improve robustness across conditions

### Near Term

- **Multi-jump detection**: Analyze 3-6 jumps in a single video
  - Foundation for continuous movement analysis
- Web interface prototype

</div>

Note: Focus on validation first. Near-term features build on current foundation. Emphasize this is active development.

---

## Long Term Vision

<div style="font-size: 0.9em;">

### Expanding Capabilities

- **Force plate validation study**: Establish accuracy benchmarks
- **Sprint analysis** (stride length, frequency, mechanics)
  - Builds on multi-event detection
- Additional movements (squats, Olympic lifts)
- Real-time processing capability
- Mobile app development
- Automated athlete progress tracking
- AI coaching recommendations

</div>

Note: These are aspirational goals. Open to community input on priorities. Emphasize this is a learning project.

---

## Questions & Discussion

### Get Involved

**GitHub**: github.com/feniix/kinemotion
**PyPI**: `pip install kinemotion`

### Let's Talk

- Your experience with jump analysis tools?
- Ideas for improvements or new movements?
- Questions about the methods?

Note: Open to collaboration and feedback. Be ready for technical questions about algorithms, validation, or implementation. Encourage audience to try it and provide feedback.
