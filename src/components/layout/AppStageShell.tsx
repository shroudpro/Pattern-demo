"use client";

import { useEffect, useRef, useState, type PointerEvent, type ReactNode } from "react";
import clsx from "clsx";

import { BackgroundRippleLayer } from "@/components/motion/BackgroundRippleLayer";
import { shouldEnableDesktopRipple } from "@/lib/design/content";
import { useRouteTransition } from "@/components/motion/RouteTransitionProvider";

interface AppStageShellProps {
  backgroundImage: string;
  children: ReactNode;
  decorativeLayer?: ReactNode;
  className?: string;
  contentClassName?: string;
}

interface RippleEntry {
  id: number;
  x: number;
  y: number;
  size: number;
}

export function AppStageShell({
  backgroundImage,
  children,
  decorativeLayer,
  className,
  contentClassName,
}: AppStageShellProps) {
  const { isTransitioning } = useRouteTransition();
  const [hasFinePointer, setHasFinePointer] = useState(false);
  const [ripples, setRipples] = useState<RippleEntry[]>([]);
  const lastMoveRef = useRef(0);

  useEffect(() => {
    const mediaQuery = window.matchMedia("(hover: hover) and (pointer: fine)");
    const syncPointer = () => setHasFinePointer(mediaQuery.matches);
    syncPointer();
    mediaQuery.addEventListener("change", syncPointer);
    return () => mediaQuery.removeEventListener("change", syncPointer);
  }, []);

  function appendRipple(event: PointerEvent<HTMLElement>, size: number) {
    if (isTransitioning) {
      return;
    }

    const blockedSurface = Boolean((event.target as HTMLElement | null)?.closest("[data-stage-surface='content']"));
    if (!shouldEnableDesktopRipple(hasFinePointer, blockedSurface)) {
      return;
    }

    const nextRipple: RippleEntry = {
      id: Date.now() + Math.random(),
      x: event.clientX,
      y: event.clientY,
      size,
    };

    setRipples((current) => [...current, nextRipple]);
    window.setTimeout(() => {
      setRipples((current) => current.filter((item) => item.id !== nextRipple.id));
    }, 900);
  }

  function handlePointerMove(event: PointerEvent<HTMLElement>) {
    const now = Date.now();
    if (now - lastMoveRef.current < 150) {
      return;
    }
    lastMoveRef.current = now;
    appendRipple(event, 84);
  }

  function handlePointerDown(event: PointerEvent<HTMLElement>) {
    appendRipple(event, 120);
  }

  return (
    <main
      className={clsx("stage-shell", isTransitioning ? "stage-shell--transitioning" : null, className)}
      onPointerDown={handlePointerDown}
      onPointerMove={handlePointerMove}
    >
      <div aria-hidden="true" className="stage-shell__background" style={{ backgroundImage: `url(${backgroundImage})` }} />
      <div aria-hidden="true" className="stage-shell__veil" />
      <BackgroundRippleLayer ripples={ripples} />
      {decorativeLayer ? <div className="stage-shell__decorative">{decorativeLayer}</div> : null}
      <div className={clsx("stage-shell__content", contentClassName)} data-stage-surface="content">
        {children}
      </div>
    </main>
  );
}
