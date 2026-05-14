interface Ripple {
  id: number;
  x: number;
  y: number;
  size: number;
}

interface BackgroundRippleLayerProps {
  ripples: Ripple[];
}

export function BackgroundRippleLayer({ ripples }: BackgroundRippleLayerProps) {
  return (
    <div aria-hidden="true" className="background-ripple-layer">
      {ripples.map((ripple) => (
        <span
          key={ripple.id}
          className="background-ripple-layer__item"
          style={{
            left: ripple.x,
            top: ripple.y,
            width: ripple.size,
            height: ripple.size,
          }}
        />
      ))}
    </div>
  );
}
