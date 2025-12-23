/**
 * Camera setup and management
 */
export async function setupCamera(
  video: HTMLVideoElement,
  width: number,
  height: number
): Promise<void> {
  const stream = await navigator.mediaDevices.getUserMedia({
    video: { width, height }
  });

  video.srcObject = stream;

  await new Promise<void>((resolve) => {
    video.onloadedmetadata = () => {
      video.play();
      resolve();
    };
  });
}
