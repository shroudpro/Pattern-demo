import type { GenerationStatus } from "@/types/generation";

export const BUTTON_ASPECT_RATIO = "411 / 95";
export const INTRO_SESSION_KEY = "wensheng-intro-seen";
export const TRANSITION_FADE_OUT_MS = 220;
export const TRANSITION_ROLL_MS = 900;
export const TRANSITION_ARRIVE_MS = 420;
export const TRANSITION_WAIT_FALLBACK_MS = 1800;

export const DESIGN_ASSETS = {
  analyzeBackground: "/design/analyze_background.png",
  transitionCloudPrimary: "/design/cloud.png",
  transitionCloudSecondary: "/design/cloud2.jpeg",
  transitionCloudTertiary: "/design/cloud3.jpeg",
  transitionBackground: "/design/background.png",
  buttonBackground: "/design/Button.png",
  cardBackground: "/design/card.png",
  cardSecondaryBackground: "/design/card2.png",
  cloud: "/design/cloud.png",
  createBackground: "/design/create_background.png",
  createInputBackground: "/design/creat_input_background.png",
  promptBackground: "/design/OIP-C.png",
  poem: "/design/poem.png",
  stageBackground: "/design/3_background.png",
  summaryBackground: "/design/C1.png",
  wordBackground: "/design/Word_background.png",
} as const;

export const FINAL_ASSETS = {
  globalDarkBackground: "/img/A1.png",
  ricePaperOverlay: "/img/A2.png",
  createHeroBackground: "/img/B1.png",
  analyzeOceanBackground: "/img/C1.png",
  analyzeFocusGlow: "/img/C2-new.png",
  traditionalInfographic16x9: "/img/D1.png",
  modernInfographic16x9: "/img/D2.png",
  editorWorkspaceBackground: "/img/E1.png",
  shanInfographicDemo: "/img/F1.png",
} as const;

interface BuildGenerationSummaryInput {
  character: string;
  styleLabel: string;
  ratioLabel: string;
  keywordLabels: string[];
}

export function getPoemPreview(poems: string[]): string[] {
  return poems.slice(0, 3);
}

export function shouldShowIntroOverlay(sessionFlag: string | null): boolean {
  return sessionFlag !== "1";
}

export function shouldEnableDesktopRipple(hasFinePointer: boolean, isBlockedSurface: boolean): boolean {
  return hasFinePointer && !isBlockedSurface;
}

export function shouldShowTransitionSkeleton(isWaitingForRoute: boolean, hasArrived: boolean): boolean {
  return isWaitingForRoute && !hasArrived;
}

export function shouldShowRadialLoading(status: GenerationStatus, isCreatingProject: boolean): boolean {
  return isCreatingProject || status === "submitting" || status === "queued" || status === "generating";
}

export function buildGenerationSummary({
  character,
  styleLabel,
  ratioLabel,
  keywordLabels,
}: BuildGenerationSummaryInput): string {
  const summaryParts = [`汉字“${character}”`, `${styleLabel}风格`, ratioLabel];
  const keywordSummary = keywordLabels.filter(Boolean).join(" / ");

  if (keywordSummary) {
    summaryParts.push(keywordSummary);
  }

  return summaryParts.join(" ");
}
