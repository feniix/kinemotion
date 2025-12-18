# AthletePose3D Validation Methodology

This document outlines the theoretical and technical methodology for validating Kinemotion using the AthletePose3D (AP3D) dataset, specifically focusing on **Coordinate Normalization** and **3D Joint Angle Calculation** in monocular video analysis.

## 1. Overview

Validating a monocular (single-camera) pose estimation system against a 3D gold-standard dataset like AthletePose3D requires more than simple point comparison. To achieve research-grade results, we must account for perspective, distance, and the inherent limitations of 2D image data.

## 2. Coordinate Normalization (Pixels to MM)

### Why it matters for Monocular Video

In monocular video, the same movement (e.g., a 50cm jump) results in different pixel displacements depending on:

1. **Camera Distance:** An athlete further away produces fewer pixels per cm.
1. **Resolution:** 1080p vs. 4K changes the pixel count for the same physical movement.

### Methodology: Procrustes Alignment

To compare MediaPipe landmarks (normalized `[0, 1]` or pixel coordinates) with AP3D ground truth (world coordinates in `mm`), we use **Procrustes Analysis** (specifically the **Kabsch Algorithm**).

- **Process:**
  1. **Translation:** Center both point clouds (MediaPipe and Ground Truth) at the same origin (e.g., the midpoint of the hips).
  1. **Scaling:** Calculate a global scaling factor based on stable anatomical anchors (e.g., torso length or hip width) averaged over the entire sequence.
  1. **Rotation:** Apply a rotation matrix to align the orientations of the two models.
- **Result:** This yields a unit-invariant **MPJPE (Mean Per Joint Position Error)** that tells us how many physical millimeters the system is off by, regardless of camera placement.

### Implementation Difficulty: Medium

- **Math:** Standard linear algebra.
- **Challenge:** Bone length jitter. MediaPipe bone lengths can "stretch" during fast movements; the normalization must use robust averaging to prevent the scale from shifting frame-by-frame.

## 3. 3D Joint Angle Calculation

### Why it matters for Monocular Video

Traditional 2D analysis measures angles "flat" on the screen. This is subject to **Perspective Error (Foreshortening)**:

- A 90° knee bend viewed from a 45° angle might appear as 70° or 110° in 2D.
- **3D Reconstruction:** By using MediaPipe's estimated Z-depth, we can reconstruct the true anatomical angle.

### Methodology: Vector Analysis in 3D

We calculate the angle $\\theta$ between two 3D vectors (e.g., Thigh and Shank) using the dot product:

$$\\cos(\\theta) = \\frac{\\mathbf{A} \\cdot \\mathbf{B}}{|\\mathbf{A}| |\\mathbf{B}|}$$

Where:

- $\\mathbf{A}$ is the vector from Knee to Hip.
- $\\mathbf{B}$ is the vector from Knee to Ankle.

### Implementation Difficulty: Medium-Hard

- **The Math:** Straightforward.
- **The Challenge: Depth Noise.** MediaPipe's Z-axis (depth) is its most unstable dimension. Small errors in depth (e.g., 2-3cm) can cause massive swings in the resulting 3D angle (15°+).
- **Solution:** Requires advanced signal processing (Savitzky-Golay filtering or Kalman filters) applied to the 3D vectors before angle calculation to ensure the metrics are stable enough for coaching feedback.

## 4. Strategic ROI

| Feature           | Strategic Value             | Marketing Claim                                        |
| :---------------- | :-------------------------- | :----------------------------------------------------- |
| **Normalization** | Proof of absolute accuracy. | "Validated to within ±X mm of gold-standard research." |
| **3D Angles**     | Perspective invariance.     | "Accurate biomechanical angles from any camera view."  |

## 5. Summary

Implementing these methodologies moves Kinemotion from a qualitative analysis tool to a **quantitative biomechanical instrument**. While 2D analysis is sufficient for the Phase 1 MVP, these 3D refinements are the foundation for Phase 2 research-grade validation.
