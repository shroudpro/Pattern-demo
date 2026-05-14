import assert from "node:assert/strict";

import {
  BUTTON_ASPECT_RATIO,
  DESIGN_ASSETS,
  INTRO_SESSION_KEY,
  TRANSITION_FADE_OUT_MS,
  TRANSITION_ROLL_MS,
  TRANSITION_WAIT_FALLBACK_MS,
  buildGenerationSummary,
  getPoemPreview,
  shouldEnableDesktopRipple,
  shouldShowIntroOverlay,
  shouldShowRadialLoading,
  shouldShowTransitionSkeleton,
} from "@/lib/design/content";

assert.equal(DESIGN_ASSETS.createBackground, "/design/create_background.png");
assert.equal(DESIGN_ASSETS.buttonBackground, "/design/Button.png");
assert.equal(BUTTON_ASPECT_RATIO, "411 / 95");
assert.equal(INTRO_SESSION_KEY, "wensheng-intro-seen");
assert.equal(TRANSITION_FADE_OUT_MS, 220);
assert.equal(TRANSITION_ROLL_MS, 900);
assert.equal(TRANSITION_WAIT_FALLBACK_MS, 1800);

assert.deepEqual(getPoemPreview(["一", "二", "三", "四"]), ["一", "二", "三"]);
assert.deepEqual(getPoemPreview(["一", "二"]), ["一", "二"]);

assert.equal(shouldShowRadialLoading("idle", false), false);
assert.equal(shouldShowRadialLoading("submitting", false), true);
assert.equal(shouldShowRadialLoading("queued", false), true);
assert.equal(shouldShowRadialLoading("generating", false), true);
assert.equal(shouldShowRadialLoading("succeeded", true), true);
assert.equal(shouldShowRadialLoading("failed", false), false);
assert.equal(shouldShowIntroOverlay(null), true);
assert.equal(shouldShowIntroOverlay("1"), false);
assert.equal(shouldEnableDesktopRipple(true, false), true);
assert.equal(shouldEnableDesktopRipple(true, true), false);
assert.equal(shouldEnableDesktopRipple(false, false), false);
assert.equal(shouldShowTransitionSkeleton(true, false), true);
assert.equal(shouldShowTransitionSkeleton(false, false), false);
assert.equal(shouldShowTransitionSkeleton(true, true), false);

assert.equal(
  buildGenerationSummary({
    character: "山",
    styleLabel: "传统",
    ratioLabel: "16:9 横屏解析图",
    keywordLabels: ["山脊轮廓", "石理肌理", "雄浑"],
  }),
  "汉字“山” 传统风格 16:9 横屏解析图 山脊轮廓 / 石理肌理 / 雄浑",
);

assert.equal(
  buildGenerationSummary({
    character: "山",
    styleLabel: "现代",
    ratioLabel: "1:1 方形解析图",
    keywordLabels: [],
  }),
  "汉字“山” 现代风格 1:1 方形解析图",
);
