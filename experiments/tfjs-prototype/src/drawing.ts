import * as handPoseDetection from '@tensorflow-models/hand-pose-detection';

// Hand connections (MediaPipe Hands)
export const HAND_CONNECTIONS = [
  [0, 1], [1, 2], [2, 3], [3, 4],         // Thumb
  [0, 5], [5, 6], [6, 7], [7, 8],         // Index
  [0, 9], [9, 10], [10, 11], [11, 12],    // Middle
  [0, 13], [13, 14], [14, 15], [15, 16],  // Ring
  [0, 17], [17, 18], [18, 19], [19, 20],  // Pinky
  [5, 9], [9, 13], [13, 17], [0, 17]      // Palm
];

export function drawHands(
  ctx: CanvasRenderingContext2D,
  hands: handPoseDetection.Hand[]
) {
  hands.forEach(hand => {
    // Skeleton
    ctx.strokeStyle = '#00FF00'; // Green
    ctx.lineWidth = 4;
    HAND_CONNECTIONS.forEach((pair) => {
      const i = pair[0];
      const j = pair[1];
      const kp1 = hand.keypoints[i];
      const kp2 = hand.keypoints[j];
      ctx.beginPath();
      ctx.moveTo(kp1.x, kp1.y);
      ctx.lineTo(kp2.x, kp2.y);
      ctx.stroke();
    });

    // Points
    ctx.fillStyle = '#FF0000'; // Red
    hand.keypoints.forEach((kp) => {
      ctx.beginPath();
      ctx.arc(kp.x, kp.y, 4, 0, 2 * Math.PI);
      ctx.fill();
    });
  });
}
