import { vi } from 'vitest';

// Mock HTMLCanvasElement.getContext to suppress JSDOM warnings
// JSDOM doesn't implement canvas rendering, so we provide a minimal mock
(HTMLCanvasElement.prototype.getContext as any) = function(contextId: string) {
  if (contextId === '2d') {
    return {
      canvas: {},
      fillStyle: '',
      strokeStyle: '',
      lineWidth: 0,
      clearRect: vi.fn(),
      fillRect: vi.fn(),
      strokeRect: vi.fn(),
      beginPath: vi.fn(),
      closePath: vi.fn(),
      moveTo: vi.fn(),
      lineTo: vi.fn(),
      arc: vi.fn(),
      fill: vi.fn(),
      stroke: vi.fn(),
      drawImage: vi.fn(),
      save: vi.fn(),
      restore: vi.fn(),
      scale: vi.fn(),
      rotate: vi.fn(),
      translate: vi.fn(),
      transform: vi.fn(),
      setTransform: vi.fn(),
      resetTransform: vi.fn(),
    } as unknown as CanvasRenderingContext2D;
  }
  return null;
};
