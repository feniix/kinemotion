/**
 * UI generation and DOM element management
 */

export interface UIElements {
  video: HTMLVideoElement;
  canvas: HTMLCanvasElement;
  ctx: CanvasRenderingContext2D;
  statusEl: HTMLElement;
  fpsEl: HTMLElement;
  backendSelect: HTMLSelectElement;
  handsToggle: HTMLInputElement;
  smoothToggle: HTMLInputElement;
}

export function createUI(width: number, height: number): UIElements {
  const app = document.querySelector<HTMLDivElement>('#app')!;

  app.innerHTML = `
    <div style="position: relative; width: ${width}px; margin: 0 auto;">
      <h1>TF.js Tracking</h1>
      <div style="margin-bottom: 10px; background: #333; padding: 10px; border-radius: 4px;">
        <label>Backend: <select id="backend-select">
          <option value="webgl">WebGL</option>
        </select></label>

        <label style="margin-left: 10px;">Hands: <input type="checkbox" id="hands-toggle" checked></label>
        <label style="margin-left: 10px;">Smooth: <input type="checkbox" id="smooth-toggle" checked></label>

        <div style="margin-top: 5px;">
           <span id="status" style="font-weight: bold; color: yellow;">Initializing...</span>
        </div>
      </div>
      <div style="position: relative;">
        <div id="fps" style="position: absolute; top: 10px; left: 10px; color: lime; font-weight: bold; font-family: monospace; background: rgba(0,0,0,0.5); padding: 4px;">FPS: 0</div>
        <video id="video" playsinline style="transform: scaleX(-1); width: ${width}px; height: ${height}px; display: none;"></video>
        <canvas id="output" width="${width}" height="${height}" style="transform: scaleX(-1); width: ${width}px; height: ${height}px; border: 1px solid #333;"></canvas>
      </div>
    </div>
  `;

  const video = document.getElementById('video') as HTMLVideoElement;
  const canvas = document.getElementById('output') as HTMLCanvasElement;
  const ctx = canvas.getContext('2d')!;
  const statusEl = document.getElementById('status')!;
  const fpsEl = document.getElementById('fps')!;
  const backendSelect = document.getElementById('backend-select') as HTMLSelectElement;
  const handsToggle = document.getElementById('hands-toggle') as HTMLInputElement;
  const smoothToggle = document.getElementById('smooth-toggle') as HTMLInputElement;

  return {
    video,
    canvas,
    ctx,
    statusEl,
    fpsEl,
    backendSelect,
    handsToggle,
    smoothToggle
  };
}
