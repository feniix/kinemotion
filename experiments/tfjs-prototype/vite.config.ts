import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./tests/setup.ts'],
  },
  build: {
    // Increase the chunk size limit to 2MB since we are bundling large ML models
    chunkSizeWarningLimit: 2000,
    rollupOptions: {
      output: {
        manualChunks: {
          'tensorflow': [
            '@tensorflow/tfjs-core',
            '@tensorflow/tfjs-converter',
            '@tensorflow/tfjs-backend-webgl'
          ],
          'detection-models': [
            '@tensorflow-models/hand-pose-detection',
            '@mediapipe/hands'
          ]
        }
      }
    }
  }
});
