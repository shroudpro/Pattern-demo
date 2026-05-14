import type { CSSProperties } from "react";

export function RadialLoading() {
  return (
    <div aria-label="生成中" className="radial-loading" role="status">
      {Array.from({ length: 9 }).map((_, index) => (
        <span
          key={index}
          className="radial-loading__ray"
          style={
            {
              "--ray-index": index,
            } as CSSProperties
          }
        />
      ))}
    </div>
  );
}
