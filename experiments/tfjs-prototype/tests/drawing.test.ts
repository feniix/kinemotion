import { describe, it, expect, vi, beforeEach } from 'vitest';
import { drawHands, HAND_CONNECTIONS } from '../src/drawing';
import type * as handPoseDetection from '@tensorflow-models/hand-pose-detection';

describe('HAND_CONNECTIONS', () => {
  it('should have correct structure', () => {
    expect(HAND_CONNECTIONS).toBeDefined();
    expect(HAND_CONNECTIONS.length).toBeGreaterThan(0);

    // Each connection should be a pair of indices
    HAND_CONNECTIONS.forEach(pair => {
      expect(pair).toHaveLength(2);
      expect(typeof pair[0]).toBe('number');
      expect(typeof pair[1]).toBe('number');
    });
  });

  it('should have valid keypoint indices (0-20 for MediaPipe Hands)', () => {
    HAND_CONNECTIONS.forEach(pair => {
      expect(pair[0]).toBeGreaterThanOrEqual(0);
      expect(pair[0]).toBeLessThanOrEqual(20);
      expect(pair[1]).toBeGreaterThanOrEqual(0);
      expect(pair[1]).toBeLessThanOrEqual(20);
    });
  });
});

describe('drawHands', () => {
  let mockCtx: CanvasRenderingContext2D;

  beforeEach(() => {
    // Create a mock canvas context
    mockCtx = {
      strokeStyle: '',
      fillStyle: '',
      lineWidth: 0,
      beginPath: vi.fn(),
      moveTo: vi.fn(),
      lineTo: vi.fn(),
      stroke: vi.fn(),
      arc: vi.fn(),
      fill: vi.fn(),
    } as unknown as CanvasRenderingContext2D;
  });

  it('should not throw with empty hands array', () => {
    expect(() => drawHands(mockCtx, [])).not.toThrow();
  });

  it('should draw skeleton lines for each hand', () => {
    const mockHands: handPoseDetection.Hand[] = [
      {
        score: 0.9,
        handedness: 'Right',
        keypoints: Array.from({ length: 21 }, (_, i) => ({
          x: 100 + i * 10,
          y: 100 + i * 10,
          name: `point_${i}`
        })),
        keypoints3D: []
      }
    ];

    drawHands(mockCtx, mockHands);

    // Should call beginPath for each connection
    const expectedConnectionCalls = HAND_CONNECTIONS.length;
    expect(mockCtx.beginPath).toHaveBeenCalledTimes(
      expectedConnectionCalls + 21 // connections + keypoints
    );

    // Should call stroke for each connection
    expect(mockCtx.stroke).toHaveBeenCalledTimes(expectedConnectionCalls);
  });

  it('should draw keypoints for each hand', () => {
    const mockHands: handPoseDetection.Hand[] = [
      {
        score: 0.9,
        handedness: 'Right',
        keypoints: Array.from({ length: 21 }, (_, i) => ({
          x: 100 + i * 10,
          y: 100 + i * 10,
          name: `point_${i}`
        })),
        keypoints3D: []
      }
    ];

    drawHands(mockCtx, mockHands);

    // Should call arc for each keypoint (21 per hand)
    expect(mockCtx.arc).toHaveBeenCalledTimes(21);

    // Should call fill for each keypoint
    expect(mockCtx.fill).toHaveBeenCalledTimes(21);
  });

  it('should handle multiple hands', () => {
    const mockHands: handPoseDetection.Hand[] = [
      {
        score: 0.9,
        handedness: 'Right',
        keypoints: Array.from({ length: 21 }, (_, i) => ({
          x: 100 + i * 10,
          y: 100 + i * 10,
          name: `point_${i}`
        })),
        keypoints3D: []
      },
      {
        score: 0.8,
        handedness: 'Left',
        keypoints: Array.from({ length: 21 }, (_, i) => ({
          x: 300 + i * 10,
          y: 300 + i * 10,
          name: `point_${i}`
        })),
        keypoints3D: []
      }
    ];

    drawHands(mockCtx, mockHands);

    // Should draw for both hands
    expect(mockCtx.arc).toHaveBeenCalledTimes(42); // 21 * 2
    expect(mockCtx.fill).toHaveBeenCalledTimes(42);
  });

  it('should set correct drawing styles', () => {
    const mockHands: handPoseDetection.Hand[] = [
      {
        score: 0.9,
        handedness: 'Right',
        keypoints: Array.from({ length: 21 }, (_, i) => ({
          x: 100,
          y: 100,
          name: `point_${i}`
        })),
        keypoints3D: []
      }
    ];

    drawHands(mockCtx, mockHands);

    // Should set green stroke for skeleton
    expect(mockCtx.strokeStyle).toBe('#00FF00');
    expect(mockCtx.lineWidth).toBe(4);

    // Should set red fill for keypoints
    expect(mockCtx.fillStyle).toBe('#FF0000');
  });
});
