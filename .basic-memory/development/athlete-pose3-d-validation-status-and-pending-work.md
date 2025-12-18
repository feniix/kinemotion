---
title: AthletePose3D Validation Status and Pending Work
type: note
permalink: development/athlete-pose3-d-validation-status-and-pending-work
---

# AthletePose3D Validation Status - Dec 18, 2025

## 🏁 Overview
The validation scripts for AthletePose3D (AP3D) have been remade after being lost from the workspace. They are currently in a "Phase 1: Infrastructure Ready" state.

## 🔗 Verified Resources
- **Repository:** https://github.com/calvinyeungck/AthletePose3D
- **License:** https://github.com/calvinyeungck/athletepose3d/blob/main/license/README.md
- **Download Link:** [Google Drive](https://drive.google.com/drive/folders/10YnMJAluiscnLkrdiluIeehNetdry5Ft?usp=sharing) (Verified Dec 18, 2025)

## 📊 Code Evaluation
- **Structural Integrity:** High. Scripts follow modular `prepare -> validate -> report` flow.
- **Scientific Validity:** Medium. Current implementation lack **Coordinate Normalization** (World mm vs Image px).
- **Temporal Alignment:** High. Uses linear interpolation to align research sequences (60/120fps) with video processing.

## 🚀 Critical Pending Tasks
1. **Coordinate Normalization:** Implement scaling (e.g., torso-length based) and Procrustes alignment.
2. **3D Angles:** Implement 3D kinematic angle calculations (currently placeholders).
3. **Data Verification:** Test `.pkl` loader against actual AP3D files once downloaded.

## 📝 Roadmap Integration
- **Status:** Non-blocking for MVP.
- **Priority:** High for scientific credibility (post-Week 3).
- **Goal:** Prove MediaPipe's "accurate" preset achieves <100mm MPJPE on athletic movements.

## 📚 Documentation
- **Methodology Guide:** `docs/validation/athletepose3d-methodology.md` (Explains the "Why" and "How" of 3D validation).
- **Validation Status:** `docs/validation-status.md` (Updated to reflect active AP3D research phase).
