import { DESIGN_ASSETS } from "@/lib/design/content";

export type RouteTransitionPhase = "idle" | "fading" | "rolling" | "waiting" | "arriving";

interface RollTransitionOverlayProps {
  phase: RouteTransitionPhase;
  showSkeleton: boolean;
}

export function RollTransitionOverlay({ phase, showSkeleton }: RollTransitionOverlayProps) {
  if (phase === "idle") {
    return null;
  }

  return (
    <div aria-hidden="true" className={`roll-transition-overlay roll-transition-overlay--${phase}`}>
      <div
        className="roll-transition-overlay__blackout"
        style={{ backgroundImage: `url(${DESIGN_ASSETS.transitionBackground})` }}
      />
      {phase === "rolling" ? (
        <div className="roll-transition-overlay__clouds">
          <img alt="" className="roll-transition-overlay__cloud roll-transition-overlay__cloud--one" src={DESIGN_ASSETS.transitionCloudPrimary} />
          <img alt="" className="roll-transition-overlay__cloud roll-transition-overlay__cloud--two" src={DESIGN_ASSETS.transitionCloudSecondary} />
          <img alt="" className="roll-transition-overlay__cloud roll-transition-overlay__cloud--three" src={DESIGN_ASSETS.transitionCloudTertiary} />
        </div>
      ) : null}
      {showSkeleton ? (
        <div className="roll-transition-overlay__skeleton">
          <div className="roll-transition-overlay__skeleton-card" />
          <div className="roll-transition-overlay__skeleton-line" />
          <div className="roll-transition-overlay__skeleton-line roll-transition-overlay__skeleton-line--short" />
        </div>
      ) : null}
    </div>
  );
}
