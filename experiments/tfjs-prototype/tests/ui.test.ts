import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { createUI } from '../src/ui';

describe('createUI', () => {
  beforeEach(() => {
    document.body.innerHTML = '<div id="app"></div>';
  });

  afterEach(() => {
    document.body.innerHTML = '';
  });

  it('should create all required UI elements', () => {
    const ui = createUI(640, 480);

    expect(ui.video).toBeDefined();
    expect(ui.canvas).toBeDefined();
    expect(ui.backendSelect).toBeDefined();
    expect(ui.handsToggle).toBeDefined();
    expect(ui.smoothToggle).toBeDefined();
    expect(ui.fpsEl).toBeDefined();
    expect(ui.statusEl).toBeDefined();
  });

  it('should set correct dimensions on video and canvas', () => {
    const ui = createUI(640, 480);

    // Check attributes because JSDOM might not reflect layout properties perfectly
    expect(ui.canvas.getAttribute('width')).toBe('640');
    expect(ui.canvas.getAttribute('height')).toBe('480');
  });

  it('should initialize toggles to correct defaults', () => {
    const ui = createUI(640, 480);

    expect(ui.handsToggle.checked).toBe(true);
    expect(ui.smoothToggle.checked).toBe(true);
  });
});
