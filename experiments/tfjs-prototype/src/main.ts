import * as handPoseDetection from '@tensorflow-models/hand-pose-detection';
import * as tf from '@tensorflow/tfjs-core';
import '@tensorflow/tfjs-backend-webgl';

import { VIDEO_WIDTH, VIDEO_HEIGHT } from './config';
import { setupCamera } from './camera';
import { initializeDetectors, disposeDetectors, type Detectors } from './detectors';
import { createUI } from './ui';
import { KeypointSmoother } from './smoother';
import { drawHands } from './drawing';
import { FPSCounter } from './fps';

async function main() {
  // 1. Create UI
  const ui = createUI(VIDEO_WIDTH, VIDEO_HEIGHT);

  // 2. Setup Camera
  try {
    await setupCamera(ui.video, VIDEO_WIDTH, VIDEO_HEIGHT);
  } catch (e) {
    ui.statusEl.textContent = `Camera error: ${e}`;
    ui.statusEl.style.color = 'red';
    return;
  }

  // 3. State
  let detectors: Partial<Detectors> = {};
  let rafId: number;
  let isInitializing = false;

  const handSmoother = new KeypointSmoother(0.5);
  const fpsCounter = new FPSCounter();

  // 4. Initialize Detectors
  async function init() {
    if (isInitializing) return;
    isInitializing = true;

    if (rafId) cancelAnimationFrame(rafId);

    disposeDetectors(detectors);
    detectors = {};

    const backendName = ui.backendSelect.value;
    ui.statusEl.textContent = `Setting ${backendName}...`;
    ui.statusEl.style.color = 'yellow';
    ui.backendSelect.disabled = true;

    try {
      ui.statusEl.textContent = `Loading models...`;
      detectors = await initializeDetectors(backendName);

      ui.statusEl.textContent = `Ready (${tf.getBackend()})`;
      ui.statusEl.style.color = 'lime';

      handSmoother.reset();
      render();
    } catch (e) {
      ui.statusEl.textContent = `Error: ${e}`;
      ui.statusEl.style.color = 'red';
      console.error(e);
    } finally {
      isInitializing = false;
      ui.backendSelect.disabled = false;
    }
  }

  // 5. Render Loop
  async function render() {
    const { handDetector } = detectors;
    if (!handDetector) return;

    if (ui.video.readyState < 2) {
      rafId = requestAnimationFrame(render);
      return;
    }

    try {
      // Create tensor
      const imageTensor = tf.browser.fromPixels(ui.video);

      // Run enabled detectors
      let hands: handPoseDetection.Hand[] = [];

      if (ui.handsToggle.checked) {
        hands = await handDetector.estimateHands(imageTensor, { flipHorizontal: false });
      }

      imageTensor.dispose();

      // Smooth
      if (ui.smoothToggle.checked && hands.length > 0) {
        hands = handSmoother.smooth(hands);
      }

      // Draw
      ui.ctx.clearRect(0, 0, ui.canvas.width, ui.canvas.height);
      ui.ctx.drawImage(ui.video, 0, 0, VIDEO_WIDTH, VIDEO_HEIGHT);

      if (hands.length > 0) drawHands(ui.ctx, hands);

    } catch (e) {
      console.error(e);
    }

    // Update FPS
    const fps = fpsCounter.update();
    ui.fpsEl.textContent = `FPS: ${fps}`;

    rafId = requestAnimationFrame(render);
  }

  // 6. Event Listeners
  ui.backendSelect.addEventListener('change', () => init());

  // 7. Start
  init();
}

main().catch(console.error);
