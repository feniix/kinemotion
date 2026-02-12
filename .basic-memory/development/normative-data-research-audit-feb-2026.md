---
title: Normative Data Research Audit - Feb 2026
type: note
permalink: development/normative-data-research-audit-feb-2026
tags:
- audit
- normative-data
- research
- validation
---

# Normative Data Research Validation Audit

**Date:** 2026-02-12
**File:** `backend/src/kinemotion_backend/services/normative_data.py`

## Verification Results

| Metric | Confidence | Source | Status |
|---|---|---|---|
| Jump Height | HIGH | TopEndSports/NSCA exact match | Verified |
| GCT | HIGH | Flanagan & Comyns (2008) 250ms SSC | Verified |
| CM Depth | HIGH | McHugh (2024), Mandic (2015) | Verified |
| RSI | MODERATE | Synthesized (no gold-standard exists) | Provenance comment added |
| Peak Velocity | MODERATE | McMahon (2017) sex differences | Provenance comment added |
| Age Factors | MOD-HIGH | Alvero-Cruz et al. (2021) | Citation fixed |
| Training Factors | MODERATE | Internal derivation (transparent) | Already documented |

## Key Findings
- Jump height norms are EXACT matches to published normative tables
- McMahon (2017) male peak velocity 2.67±0.18 m/s falls in our "above_average" (2.4-3.0) — correct for university athletes
- No published RSI normative classification table exists (confirmed by Science for Sport, Output Sports)
- Alvero-Cruz et al. (2021, Frontiers in Physiology) is the correct citation for age decline
- All coaching tips follow established S&C programming principles
- All 15 cross-metric insight keys have accurate frontend translations

## No Value Changes Needed
All numeric values in normative_data.py are either directly from research or defensible syntheses.
