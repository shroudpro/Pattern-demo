export function createNebulaParticles(
  count: number,
  width: number,
  height: number
): Float32Array {
  const positions = new Float32Array(count * 3);
  
  for (let i = 0; i < count; i++) {
    const radius = Math.random() * (Math.max(width, height) * 0.8);
    const angle = Math.random() * Math.PI * 2;
    
    const spiralAngle = angle + radius * 0.002;
    
    const x = Math.cos(spiralAngle) * radius;
    const y = Math.sin(spiralAngle) * radius;
    
    const zSpread = 1000 * (1 - radius / (Math.max(width, height) * 0.8) + 0.1);
    const z = (Math.random() - 0.5) * Math.min(1000, zSpread);
    
    positions[i * 3] = x;
    positions[i * 3 + 1] = y;
    positions[i * 3 + 2] = Math.max(-500, Math.min(500, z));
  }
  
  return positions;
}
