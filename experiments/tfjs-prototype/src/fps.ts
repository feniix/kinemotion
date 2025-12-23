/**
 * FPS counter utility
 */
export class FPSCounter {
  private lastFrameTime = performance.now();
  private frameCount = 0;
  private currentFPS = 0;

  update(): number {
    this.frameCount++;
    const time = performance.now();

    if (time - this.lastFrameTime >= 1000) {
      this.currentFPS = Math.round((this.frameCount * 1000) / (time - this.lastFrameTime));
      this.frameCount = 0;
      this.lastFrameTime = time;
    }

    return this.currentFPS;
  }

  get fps(): number {
    return this.currentFPS;
  }
}
