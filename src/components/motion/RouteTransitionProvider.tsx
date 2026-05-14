"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from "react";
import { usePathname, useRouter } from "next/navigation";

import {
  TRANSITION_ARRIVE_MS,
  TRANSITION_FADE_OUT_MS,
  TRANSITION_ROLL_MS,
  TRANSITION_WAIT_FALLBACK_MS,
  shouldShowTransitionSkeleton,
} from "@/lib/design/content";
import { RollTransitionOverlay, type RouteTransitionPhase } from "@/components/motion/RollTransitionOverlay";

interface RouteTransitionContextValue {
  isTransitioning: boolean;
  startRollTransition: (href: string) => void;
}

const RouteTransitionContext = createContext<RouteTransitionContextValue | null>(null);

interface TransitionState {
  phase: RouteTransitionPhase;
  targetHref: string | null;
  routeArrived: boolean;
}

export function RouteTransitionProvider({ children }: { children: ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const timeoutsRef = useRef<number[]>([]);
  const [transitionState, setTransitionState] = useState<TransitionState>({
    phase: "idle",
    targetHref: null,
    routeArrived: false,
  });

  const clearTimers = useCallback(() => {
    timeoutsRef.current.forEach((timerId) => window.clearTimeout(timerId));
    timeoutsRef.current = [];
  }, []);

  useEffect(() => clearTimers, [clearTimers]);

  const startRollTransition = useCallback(
    (href: string) => {
      setTransitionState((current) => {
        if (current.phase !== "idle") {
          return current;
        }

        return {
          phase: "fading",
          targetHref: href,
          routeArrived: false,
        };
      });
    },
    [],
  );

  useEffect(() => {
    clearTimers();

    if (transitionState.phase === "fading") {
      const timerId = window.setTimeout(() => {
        setTransitionState((current) => ({ ...current, phase: "rolling" }));
      }, TRANSITION_FADE_OUT_MS);
      timeoutsRef.current.push(timerId);
    }

    if (transitionState.phase === "rolling" && transitionState.targetHref) {
      const targetHref = transitionState.targetHref;
      const timerId = window.setTimeout(() => {
        router.push(targetHref);
        setTransitionState((current) => ({ ...current, phase: "waiting" }));
      }, TRANSITION_ROLL_MS);
      timeoutsRef.current.push(timerId);
    }

    if (transitionState.phase === "arriving") {
      const timerId = window.setTimeout(() => {
        setTransitionState({
          phase: "idle",
          targetHref: null,
          routeArrived: false,
        });
      }, TRANSITION_ARRIVE_MS);
      timeoutsRef.current.push(timerId);
    }
  }, [clearTimers, router, transitionState.phase, transitionState.targetHref]);

  useEffect(() => {
    if (!transitionState.targetHref || transitionState.phase !== "waiting") {
      return;
    }

    if (normalizeRoutePath(pathname) === normalizeRoutePath(transitionState.targetHref)) {
      setTransitionState((current) => ({
        ...current,
        phase: "arriving",
        routeArrived: true,
      }));
    }
  }, [pathname, transitionState.phase, transitionState.targetHref]);

  useEffect(() => {
    if (transitionState.phase !== "waiting") {
      return;
    }

    const timerId = window.setTimeout(() => {
      setTransitionState((current) => {
        if (current.phase !== "waiting") {
          return current;
        }

        return {
          ...current,
          phase: "arriving",
          routeArrived: true,
        };
      });
    }, TRANSITION_WAIT_FALLBACK_MS);
    timeoutsRef.current.push(timerId);
  }, [transitionState.phase]);

  const contextValue = useMemo<RouteTransitionContextValue>(
    () => ({
      isTransitioning: transitionState.phase !== "idle",
      startRollTransition,
    }),
    [startRollTransition, transitionState.phase],
  );

  return (
    <RouteTransitionContext.Provider value={contextValue}>
      {children}
      <RollTransitionOverlay
        phase={transitionState.phase}
        showSkeleton={shouldShowTransitionSkeleton(transitionState.phase === "waiting", transitionState.routeArrived)}
      />
    </RouteTransitionContext.Provider>
  );
}

function normalizeRoutePath(value: string): string {
  const pathWithoutQuery = value.replace(/\?.*$/, "").replace(/#.*$/, "");
  const decodedPath = safeDecodeURIComponent(pathWithoutQuery);
  const withoutTrailingSlash = decodedPath.length > 1 ? decodedPath.replace(/\/+$/, "") : decodedPath;
  return withoutTrailingSlash || "/";
}

function safeDecodeURIComponent(value: string): string {
  try {
    return decodeURIComponent(value);
  } catch {
    return value;
  }
}

export function useRouteTransition() {
  const context = useContext(RouteTransitionContext);

  if (!context) {
    throw new Error("useRouteTransition 必须在 RouteTransitionProvider 内使用。");
  }

  return context;
}
