// Generic Keypoint Interface compatible with TF.js models
export interface Point3D {
  x: number;
  y: number;
  z?: number;
  score?: number;
  name?: string;
}

export class KeypointSmoother {
  private prevObjects: { keypoints: Point3D[] }[] = [];
  private readonly alpha: number;

  constructor(alpha = 0.5) {
    this.alpha = alpha;
  }

  smooth<T extends { keypoints: Point3D[] }>(objects: T[]): T[] {
    if (objects.length === 0) {
      this.prevObjects = [];
      return objects;
    }

    const smoothedObjects = objects.map((obj, i) => {
      const prev = this.prevObjects[i];
      if (!prev) return obj;

      const smoothedKeypoints = obj.keypoints.map((kp, kIndex) => {
        const prevKp = prev.keypoints[kIndex];
        return {
          ...kp,
          x: this.alpha * kp.x + (1 - this.alpha) * prevKp.x,
          y: this.alpha * kp.y + (1 - this.alpha) * prevKp.y,
          z: (kp.z !== undefined && prevKp.z !== undefined)
             ? this.alpha * kp.z + (1 - this.alpha) * prevKp.z
             : kp.z
        };
      });

      return { ...obj, keypoints: smoothedKeypoints };
    });

    this.prevObjects = smoothedObjects;
    return smoothedObjects as T[];
  }

  reset() {
    this.prevObjects = [];
  }
}
