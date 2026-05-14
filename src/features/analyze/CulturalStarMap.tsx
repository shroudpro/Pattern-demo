export function CulturalStarMap() {
  return (
    <svg
      aria-hidden="true"
      className="pointer-events-none absolute inset-0 hidden h-full w-full lg:block"
      preserveAspectRatio="none"
      viewBox="0 0 1200 720"
    >
      <defs>
        <linearGradient id="star-map-line" x1="0" x2="1" y1="0" y2="1">
          <stop offset="0%" stopColor="rgba(234,224,200,0.1)" />
          <stop offset="48%" stopColor="rgba(224,178,92,0.62)" />
          <stop offset="100%" stopColor="rgba(234,224,200,0.12)" />
        </linearGradient>
        <filter id="star-map-glow">
          <feGaussianBlur result="blur" stdDeviation="3" />
          <feMerge>
            <feMergeNode in="blur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>
      <g filter="url(#star-map-glow)">
        <path className="culture-star-path culture-star-path--one" d="M600 354 C462 250 336 190 170 150" />
        <path className="culture-star-path culture-star-path--two" d="M600 354 C744 250 846 190 1030 150" />
        <path className="culture-star-path culture-star-path--three" d="M600 354 C462 482 340 538 166 574" />
        <path className="culture-star-path culture-star-path--four" d="M600 354 C760 486 880 540 1036 574" />
        <circle className="culture-star-node" cx="600" cy="354" r="5" />
        <circle className="culture-star-node" cx="170" cy="150" r="4" />
        <circle className="culture-star-node" cx="1030" cy="150" r="4" />
        <circle className="culture-star-node" cx="166" cy="574" r="4" />
        <circle className="culture-star-node" cx="1036" cy="574" r="4" />
      </g>
    </svg>
  );
}
