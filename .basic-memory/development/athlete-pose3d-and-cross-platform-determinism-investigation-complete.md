---
title: AthletePose3D and Cross-Platform Determinism Investigation Complete
type: note
permalink: development/athlete-pose3-d-and-cross-platform-determinism-investigation-complete
tags:
- athletepose3d
- determinism
- cross-platform
- investigation-complete
- m1-vs-intel
- version-sync
---

# AthletePose3D & Cross-Platform Determinism Investigation - Complete

**Date:** 2025-12-08 | **Duration:** 8 hours | **Status:** COMPLETE

## Executive Summary

**Original Goal:** Use AthletePose3D to make MediaPipe more deterministic

**Key Discovery:** MediaPipe IS deterministic. Problem was version mismatch + acceptable cross-platform variance.

**Results:**
- M1 & Intel both 100% deterministic on same platform ✅
- Version mismatch fixed: v0.30.0 → v0.38.0 ✅
- Remaining 5.6% cross-platform variance is normal (ARM vs x86) ✅
- AthletePose3D dataset prepared (5,154 videos) ✅

## Test Results

**M1 Determinism:** RSI = 3.7186533116576643 (5 runs, identical)
**Intel Determinism:** RSI = 4.059785924241584 (5 runs, identical)
**Cross-Platform:** 5.6% variance (acceptable)

**MediaPipe Landmarks:** 0.048% difference (negligible)
**Flight Time:** 0.1% difference (excellent)
**Contact Time:** 6% difference (event detection sensitivity)

## Root Causes

1. **Version Mismatch (FIXED):** Backend had v0.30.0, local v0.38.0 → 9% variance
2. **CPU Architecture:** ARM vs x86 floating-point → 5.6% variance (normal)
3. **Event Detection:** Amplifies tiny differences (0.048% → 6%)

## Solution Implemented

- Deleted backend/uv.lock
- Changed Docker context to root
- Backend uses workspace lock with kinemotion from source
- Both platforms now identical v0.38.0

## Files

**Test Scripts:**
- scripts/test_rsi_m1_vs_intel.sh
- scripts/test_*determinism*.sh

**Dataset:** data/athletepose3d/ (5,154 videos)

**Endpoints:** /determinism/* added to backend

## Recommendation

Accept 5.6% cross-platform variance as normal. Both platforms are deterministic and scientifically valid. Proceed with MVP.

## Lesson

Always check version matching FIRST before building complex infrastructure! Could have identified root cause in 5 minutes instead of 8 hours.
