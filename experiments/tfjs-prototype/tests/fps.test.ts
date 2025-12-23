import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { FPSCounter } from '../src/fps';

describe('FPSCounter', () => {
  let counter: FPSCounter;
  let now = 0;

  beforeEach(() => {
    now = 0;
    vi.spyOn(performance, 'now').mockImplementation(() => now);
    counter = new FPSCounter();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('should initialize with 0 fps', () => {
    expect(counter.fps).toBe(0);
  });

  it('should return 0 fps before 1 second has passed', () => {
    counter.update();
    now = 500;
    expect(counter.update()).toBe(0);
  });

  it('should calculate fps correctly after 1 second', () => {
    // Simulate 30 frames in 1 second
    for (let i = 0; i < 30; i++) {
      counter.update();
      now += 1000 / 30; // Advance time slightly for each frame (optional but realistic)
    }

    // Ensure we are past 1000ms
    now = 1001;

    const fps = counter.update(); // 31st frame triggers update
    // 31 frames / 1.001s ~= 30.96 -> 31
    expect(fps).toBeGreaterThan(0);
    expect(Math.abs(fps - 31)).toBeLessThanOrEqual(1);
  });

  it('should reset frame count after each second', () => {
    // First second
    for (let i = 0; i < 30; i++) {
      counter.update();
    }
    now = 1001;
    counter.update(); // Trigger update

    // Second second
    const startNow = now;
    for (let i = 0; i < 60; i++) {
      counter.update();
    }
    now = startNow + 1001;
    const fps = counter.update();

    // 61 frames / 1.001s ~= 60.9 -> 61
    expect(Math.abs(fps - 61)).toBeLessThanOrEqual(1);
  });
});
