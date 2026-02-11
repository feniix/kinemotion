# BiomechAgent Paper Analysis: Opportunities for Kinemotion

**Paper**: "BiomechAgent: AI-Assisted Biomechanical Analysis Through Code-Generating Agents" (Cotton & Leonard, Jan 2026, arXiv:2602.06975)

**Date**: February 2026

**Relevance**: Direct — Kinemotion faces the same gap between raw metric output and actionable coaching insights.

## Problem Statement

Markerless motion capture produces data that clinicians and coaches cannot analyze without programming expertise. BiomechAgent demonstrates that wrapping biomechanical analysis in a natural language interface dramatically improves accessibility. Kinemotion has the exact same gap: coaches upload videos and get raw metrics (0.45m jump height, 2.1 RSI) but must interpret them manually.

## Key Findings & Kinemotion Relevance

### 1. Specialized Tools Beat Generic LLMs

BiomechAgent struggled on spatiotemporal tasks without specialized tools — 5% accuracy on gait event detection. With GaitTransformer: 63%. Generic LLMs cannot replace validated algorithms.

**Implication**: Our analysis modules (CMJ backward search, drop jump forward search, SJ squat hold detection) are analogous to specialized tools. Any AI interpretation layer should USE our algorithms as tools, never replicate them in an LLM.

### 2. Domain-Specific Prompts Outperform Generic Prompts

Biomechanics-specific system prompts (formulas, expected ranges, clinical standards) significantly improved accuracy.

**Our advantage**: We already have this knowledge encoded in `core/validation.py` (MetricBounds), `*/validation_bounds.py`, and `docs/guides/coach-quick-start.md`.

### 3. System 1 + System 2 Architecture

BiomechGPT (fast, trained) + BiomechAgent (deliberate, code-based) are synergistic. This maps directly to:

- **System 1**: Kinemotion's deterministic algorithms (pose detection, phase detection, metric calculation)
- **System 2**: Interpretation layer (explain metrics, compare to norms, suggest training)

### 4. VLMs for Plot Interpretation (Future)

Vision Language Models achieved 66% accuracy on kinematic plot interpretation. Our debug overlay videos could be interpreted by VLMs in the future.

## Implementation Strategy (Tiered)

### Tier 1: Rule-Based Interpretations (Implemented)

**A. Normative Benchmarking in UI**
Surface existing normative data from `coach-quick-start.md` and validation bounds directly in the ResultsDisplay component. Show performance categories and population comparisons.

**B. Coaching Interpretations**
Transform raw metrics into coaching language using rule-based logic on our existing MetricBounds. No LLM required — deterministic and fast.

### Tier 2: LLM-Powered Chat (Future)

Allow coaches to ask follow-up questions about results with a structured prompt containing metrics + athlete profile + normative data.

### Tier 3: Full Agent Architecture (Future)

Code-generating agent for ad-hoc analysis, historical comparisons, custom visualizations.

## What We Should NOT Do

1. **Don't replace our algorithms with LLMs** — the paper explicitly validates this
2. **Don't over-engineer early** — start rule-based, validate with coaches
3. **Don't ignore privacy** — route metrics (not video) to any LLM layer

## References

- Cotton, R.J. & Leonard, T. (2026). BiomechAgent: AI-Assisted Biomechanical Analysis Through Code-Generating Agents. arXiv:2602.06975.
