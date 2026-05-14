/**
 * Sample pixel positions from a hanzi character rendered on an offscreen canvas.
 *
 * Uses a fixed-size offscreen canvas (1024x1024) rather than window dimensions
 * to ensure consistent font rendering across all navigation modes. The sampled
 * positions are then scaled to fill the target width/height.
 *
 * Returns synchronously — the caller is responsible for retrying if the result
 * is empty (e.g. when CJK glyphs haven't been rasterized yet during SPA nav).
 */
export function createHanziParticles(
  text: string,
  width: number,
  height: number,
  maxParticles: number = 20000
): Float32Array {
  // Use a fixed canvas size for reliable font rendering.
  // Large window dimensions (1920x1080) can cause font rendering issues
  // in some browsers during SPA transitions.
  const canvasSize = 1024;
  const canvas = document.createElement('canvas');
  canvas.width = canvasSize;
  canvas.height = canvasSize;
  const ctx = canvas.getContext('2d', { willReadFrequently: true });
  
  if (!ctx) return new Float32Array();

  ctx.clearRect(0, 0, canvasSize, canvasSize);
  const fontSize = Math.floor(canvasSize * 0.75);
  ctx.font = `bold ${fontSize}px serif, "SimSun", "Noto Serif CJK SC", sans-serif`;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillStyle = '#ffffff';
  ctx.fillText(text, canvasSize / 2, canvasSize / 2);

  const imageData = ctx.getImageData(0, 0, canvasSize, canvasSize);
  const data = imageData.data;
  
  const validPixels: {x: number, y: number}[] = [];
  const step = 2; 
  
  for (let y = 0; y < canvasSize; y += step) {
    for (let x = 0; x < canvasSize; x += step) {
      const alpha = data[(y * canvasSize + x) * 4 + 3];
      if (alpha > 50) { 
        // Scale from canvas coordinates to target screen coordinates.
        // Center the character within the target dimensions.
        const scale = Math.min(width, height) / canvasSize;
        validPixels.push({
          x: (x - canvasSize / 2) * scale,
          y: -(y - canvasSize / 2) * scale
        });
      }
    }
  }

  const shuffled = validPixels.sort(() => 0.5 - Math.random());
  const selected = shuffled.slice(0, maxParticles);
  
  const positions = new Float32Array(selected.length * 3);
  
  selected.forEach((pixel, i) => {
    positions[i * 3] = pixel.x;
    positions[i * 3 + 1] = pixel.y;
    positions[i * 3 + 2] = (Math.random() - 0.5) * 150;
  });

  return positions;
}
