---
title: RTMPose Keypoint Compatibility for Kinemotion
type: note
permalink: research/rtmpose-keypoint-compatibility-for-kinemotion
tags:
- rtmpose
- keypoints
- migration
- coco
- compatibility
---

# RTMPose Keypoint Compatibility for Kinemotion

## Summary

Analysis of whether RTMPose supports all keypoints used by kinemotion for CMJ and drop jump analysis.

## Key Findings

- [RTMPose COCO 17] [missing] [heel and foot_index landmarks]
- [RTMPose COCO 26] [supports] [all kinemotion landmarks including heel and big_toe]
- [Kinemotion] [uses] [13 landmarks for jump analysis]
- [Migration] [requires] [only index mapping changes, no algorithm changes]

## Kinemotion Landmark Usage

From `src/kinemotion/core/pose.py`:
- nose, shoulders, hips, knees, ankles → CoM estimation, triple extension
- heel, foot_index → Ankle angle calculation (plantarflexion)

## RTMPose Model Options
| Model | Keypoints | Format | Kinemotion Compatible? |
|-------|-----------|--------|----------------------|
| Body 17 | COCO standard | COCO | ⚠️ Partial (missing foot detail) |
| Body 26 | Extended with feet | **Halpe** | ✅ Full compatibility |
| Wholebody 133 | Full body + hands + face | COCO-WholeBody | ✅ Overkill |

**Important:** "COCO 26" does not exist as a standard. The 26-keypoint format is called **Halpe** (from AlphaPose/Halpe-FullBody dataset).


## Recommendation

Use RTMPose 26-keypoint model:
```python
body = Body(pose='body26', mode='balanced')
```

## Related

- [RTMPose Comparison](rtmpose-rtmlib-media-pipe-comparison-summary) - Full technical comparison
- [Real-Time Pose](real-time-pose-estimation-summary) - Real-time options including RTMO
