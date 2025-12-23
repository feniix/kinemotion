import * as handPoseDetection from '@tensorflow-models/hand-pose-detection';
import * as tf from '@tensorflow/tfjs-core';

export interface Detectors {
  handDetector: handPoseDetection.HandDetector;
}

/**
 * Initialize hand detector with the specified backend
 */
export async function initializeDetectors(backend: string): Promise<Detectors> {
  await tf.setBackend(backend);
  await tf.ready();

  // Load Hand Detector
  const handConfig: handPoseDetection.MediaPipeHandsTfjsModelConfig = {
    runtime: 'tfjs',
    modelType: 'full',
    maxHands: 2
  };
  const handDetector = await handPoseDetection.createDetector(
    handPoseDetection.SupportedModels.MediaPipeHands,
    handConfig
  );

  return { handDetector };
}

/**
 * Dispose of detectors to free memory
 */
export function disposeDetectors(detectors: Partial<Detectors>): void {
  if (detectors.handDetector) {
    detectors.handDetector.dispose();
  }
}
