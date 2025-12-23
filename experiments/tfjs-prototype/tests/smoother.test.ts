import { describe, it, expect } from 'vitest';
import { KeypointSmoother } from '../src/smoother';
import type * as handPoseDetection from '@tensorflow-models/hand-pose-detection';

describe('KeypointSmoother', () => {
  it('should initialize correctly', () => {
    const smoother = new KeypointSmoother(0.5);
    expect(smoother).toBeDefined();
  });

  it('should return original keypoints for the first frame', () => {
    const smoother = new KeypointSmoother(0.5);
    const mockHands: handPoseDetection.Hand[] = [
      {
        score: 0.9,
        handedness: 'Right',
        keypoints: [{ x: 100, y: 100, name: 'wrist' }],
        keypoints3D: [{ x: 100, y: 100, z: 0, name: 'wrist' }]
      }
    ];

    const smoothed = smoother.smooth(mockHands);
    expect(smoothed[0].keypoints[0].x).toBe(100);
    expect(smoothed[0].keypoints[0].y).toBe(100);
  });

  it('should smooth keypoints over time', () => {
    const alpha = 0.5;
    const smoother = new KeypointSmoother(alpha);

    // Frame 1
    const hands1: handPoseDetection.Hand[] = [
      {
        score: 0.9,
        handedness: 'Right',
        keypoints: [{ x: 100, y: 100, name: 'wrist' }],
        keypoints3D: [{ x: 100, y: 100, z: 0, name: 'wrist' }]
      }
    ];
    smoother.smooth(hands1);

    // Frame 2: Move to 200, 200
    const hands2: handPoseDetection.Hand[] = [
      {
        score: 0.9,
        handedness: 'Right',
        keypoints: [{ x: 200, y: 200, name: 'wrist' }],
        keypoints3D: [{ x: 200, y: 200, z: 0, name: 'wrist' }]
      }
    ];
    const smoothed2 = smoother.smooth(hands2);

    // Expected: 0.5 * 200 + 0.5 * 100 = 150
    expect(smoothed2[0].keypoints[0].x).toBe(150);
    expect(smoothed2[0].keypoints[0].y).toBe(150);
  });

  it('should reset state', () => {
    const smoother = new KeypointSmoother(0.5);
    const hands1: handPoseDetection.Hand[] = [
      {
        score: 0.9,
        handedness: 'Right',
        keypoints: [{ x: 100, y: 100, name: 'wrist' }],
        keypoints3D: [{ x: 100, y: 100, z: 0, name: 'wrist' }]
      }
    ];
    smoother.smooth(hands1);

    smoother.reset();

    const hands2: handPoseDetection.Hand[] = [
      {
        score: 0.9,
        handedness: 'Right',
        keypoints: [{ x: 200, y: 200, name: 'wrist' }],
        keypoints3D: [{ x: 200, y: 200, z: 0, name: 'wrist' }]
      }
    ];
    const smoothed2 = smoother.smooth(hands2);

    // Should be treated as new frame (no smoothing with previous 100)
    expect(smoothed2[0].keypoints[0].x).toBe(200);
  });

  it('should handle multiple objects (hands)', () => {
    const smoother = new KeypointSmoother(0.5);

    // Frame 1: 2 hands
    const hands1: handPoseDetection.Hand[] = [
      {
        score: 0.9,
        handedness: 'Right',
        keypoints: [{ x: 100, y: 100, name: 'wrist' }],
        keypoints3D: [{ x: 100, y: 100, z: 0, name: 'wrist' }]
      },
      {
        score: 0.8,
        handedness: 'Left',
        keypoints: [{ x: 300, y: 300, name: 'wrist' }],
        keypoints3D: [{ x: 300, y: 300, z: 0, name: 'wrist' }]
      }
    ];
    smoother.smooth(hands1);

    // Frame 2: 2 hands moved
    const hands2: handPoseDetection.Hand[] = [
      {
        score: 0.9,
        handedness: 'Right',
        keypoints: [{ x: 200, y: 200, name: 'wrist' }],
        keypoints3D: [{ x: 200, y: 200, z: 0, name: 'wrist' }]
      },
      {
        score: 0.8,
        handedness: 'Left',
        keypoints: [{ x: 400, y: 400, name: 'wrist' }],
        keypoints3D: [{ x: 400, y: 400, z: 0, name: 'wrist' }]
      }
    ];
    const smoothed2 = smoother.smooth(hands2);

    // Both hands should be smoothed
    expect(smoothed2[0].keypoints[0].x).toBe(150); // 0.5 * 200 + 0.5 * 100
    expect(smoothed2[1].keypoints[0].x).toBe(350); // 0.5 * 400 + 0.5 * 300
  });

  it('should handle object count changes (hand dropout)', () => {
    const smoother = new KeypointSmoother(0.5);

    // Frame 1: 2 hands
    const hands1: handPoseDetection.Hand[] = [
      {
        score: 0.9,
        handedness: 'Right',
        keypoints: [{ x: 100, y: 100, name: 'wrist' }],
        keypoints3D: [{ x: 100, y: 100, z: 0, name: 'wrist' }]
      },
      {
        score: 0.8,
        handedness: 'Left',
        keypoints: [{ x: 300, y: 300, name: 'wrist' }],
        keypoints3D: [{ x: 300, y: 300, z: 0, name: 'wrist' }]
      }
    ];
    smoother.smooth(hands1);

    // Frame 2: Only 1 hand (right hand dropped out)
    const hands2: handPoseDetection.Hand[] = [
      {
        score: 0.8,
        handedness: 'Left',
        keypoints: [{ x: 400, y: 400, name: 'wrist' }],
        keypoints3D: [{ x: 400, y: 400, z: 0, name: 'wrist' }]
      }
    ];
    const smoothed2 = smoother.smooth(hands2);

    // First hand (index 0) should be smoothed with previous first hand
    expect(smoothed2[0].keypoints[0].x).toBe(250); // 0.5 * 400 + 0.5 * 100
  });

  it('should handle z-coordinate smoothing', () => {
    const smoother = new KeypointSmoother(0.5);

    // Frame 1: with z
    const hands1: handPoseDetection.Hand[] = [
      {
        score: 0.9,
        handedness: 'Right',
        keypoints: [{ x: 100, y: 100, z: 10, name: 'wrist' }],
        keypoints3D: [{ x: 100, y: 100, z: 10, name: 'wrist' }]
      }
    ];
    smoother.smooth(hands1);

    // Frame 2: z changed
    const hands2: handPoseDetection.Hand[] = [
      {
        score: 0.9,
        handedness: 'Right',
        keypoints: [{ x: 200, y: 200, z: 30, name: 'wrist' }],
        keypoints3D: [{ x: 200, y: 200, z: 30, name: 'wrist' }]
      }
    ];
    const smoothed2 = smoother.smooth(hands2);

    expect(smoothed2[0].keypoints[0].z).toBe(20); // 0.5 * 30 + 0.5 * 10
  });

  it('should handle missing z-coordinate', () => {
    const smoother = new KeypointSmoother(0.5);

    // Frame 1: with z
    const hands1: handPoseDetection.Hand[] = [
      {
        score: 0.9,
        handedness: 'Right',
        keypoints: [{ x: 100, y: 100, z: 10, name: 'wrist' }],
        keypoints3D: [{ x: 100, y: 100, z: 10, name: 'wrist' }]
      }
    ];
    smoother.smooth(hands1);

    // Frame 2: no z
    const hands2: handPoseDetection.Hand[] = [
      {
        score: 0.9,
        handedness: 'Right',
        keypoints: [{ x: 200, y: 200, name: 'wrist' }],
        keypoints3D: [{ x: 200, y: 200, z: 0, name: 'wrist' }]
      }
    ];
    const smoothed2 = smoother.smooth(hands2);

    // z should be undefined (not smoothed)
    expect(smoothed2[0].keypoints[0].z).toBeUndefined();
  });

  it('should preserve additional properties', () => {
    const smoother = new KeypointSmoother(0.5);

    const hands1: handPoseDetection.Hand[] = [
      {
        score: 0.9,
        handedness: 'Right',
        keypoints: [{ x: 100, y: 100, name: 'wrist', score: 0.95 }],
        keypoints3D: [{ x: 100, y: 100, z: 0, name: 'wrist' }]
      }
    ];
    smoother.smooth(hands1);

    const hands2: handPoseDetection.Hand[] = [
      {
        score: 0.85,
        handedness: 'Right',
        keypoints: [{ x: 200, y: 200, name: 'wrist', score: 0.92 }],
        keypoints3D: [{ x: 200, y: 200, z: 0, name: 'wrist' }]
      }
    ];
    const smoothed2 = smoother.smooth(hands2);

    // Hand-level properties preserved
    expect(smoothed2[0].score).toBe(0.85);
    expect(smoothed2[0].handedness).toBe('Right');

    // Keypoint-level properties preserved
    expect(smoothed2[0].keypoints[0].name).toBe('wrist');
    expect(smoothed2[0].keypoints[0].score).toBe(0.92);
  });

  it('should handle alpha = 1 (no smoothing, current frame only)', () => {
    const smoother = new KeypointSmoother(1.0);

    const hands1: handPoseDetection.Hand[] = [
      {
        score: 0.9,
        handedness: 'Right',
        keypoints: [{ x: 100, y: 100, name: 'wrist' }],
        keypoints3D: [{ x: 100, y: 100, z: 0, name: 'wrist' }]
      }
    ];
    smoother.smooth(hands1);

    const hands2: handPoseDetection.Hand[] = [
      {
        score: 0.9,
        handedness: 'Right',
        keypoints: [{ x: 200, y: 200, name: 'wrist' }],
        keypoints3D: [{ x: 200, y: 200, z: 0, name: 'wrist' }]
      }
    ];
    const smoothed2 = smoother.smooth(hands2);

    // alpha = 1: 1.0 * 200 + 0.0 * 100 = 200
    expect(smoothed2[0].keypoints[0].x).toBe(200);
  });

  it('should handle alpha = 0 (no smoothing, previous frame only)', () => {
    const smoother = new KeypointSmoother(0.0);

    const hands1: handPoseDetection.Hand[] = [
      {
        score: 0.9,
        handedness: 'Right',
        keypoints: [{ x: 100, y: 100, name: 'wrist' }],
        keypoints3D: [{ x: 100, y: 100, z: 0, name: 'wrist' }]
      }
    ];
    smoother.smooth(hands1);

    const hands2: handPoseDetection.Hand[] = [
      {
        score: 0.9,
        handedness: 'Right',
        keypoints: [{ x: 200, y: 200, name: 'wrist' }],
        keypoints3D: [{ x: 200, y: 200, z: 0, name: 'wrist' }]
      }
    ];
    const smoothed2 = smoother.smooth(hands2);

    // alpha = 0: 0.0 * 200 + 1.0 * 100 = 100
    expect(smoothed2[0].keypoints[0].x).toBe(100);
  });
});
