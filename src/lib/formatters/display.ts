import type { GenerationStatus, RatioPreset, ScenePreset, StylePreset } from "@/types/generation";

const STYLE_LABELS: Record<StylePreset, string> = {
  traditional: "传统",
  modern: "现代",
};

const SCENE_LABELS: Record<ScenePreset, string> = {
  poster: "海报",
  package: "包装",
};

const RATIO_LABELS: Record<RatioPreset, string> = {
  "16:9": "16:9 横屏解析图",
  "1:1": "1:1 方形解析图",
  "9:16": "9:16 竖屏解析图",
};

const GENERATION_STATUS_LABELS: Record<GenerationStatus, string> = {
  idle: "空闲",
  submitting: "提交中",
  queued: "排队中",
  generating: "生成中",
  succeeded: "已完成",
  failed: "失败",
};

const ANALYSIS_STATUS_LABELS: Record<string, string> = {
  completed: "已完成",
};

const EDITOR_SAVE_STATUS_LABELS: Record<string, string> = {
  idle: "空闲",
  saving: "保存中",
  saved: "已保存",
  error: "保存失败",
};

const FONT_FAMILY_LABELS: Record<string, string> = {
  "Microsoft YaHei": "微软雅黑",
  SimSun: "宋体",
  SimHei: "黑体",
  KaiTi: "楷体",
  FangSong: "仿宋",
  serif: "衬线体",
  "sans-serif": "无衬线",
};

const KEYWORD_PHRASE_LABELS: Record<string, string> = {
  "spring bloom": "春日盛放",
  "petal cloud": "花瓣云团",
  "soft pink": "柔粉",
  festive: "节庆感",
  verdant: "葱茏",
  layered: "层叠",
  "stone texture": "石理肌理",
  "ridge contour": "山脊轮廓",
  majestic: "雄浑",
  calm: "静定",
  luminous: "清辉",
  "crescent arc": "弯月弧线",
  "silver glow": "银辉",
  quiet: "清寂",
  rhythm: "节律",
  swirling: "回旋流动",
  "auspicious cloud": "祥云",
  "soft contour": "柔和轮廓",
  floating: "浮动",
  airy: "空灵",
};

const KEYWORD_TOKEN_LABELS: Record<string, string> = {
  spring: "春",
  bloom: "盛放",
  petal: "花瓣",
  cloud: "云",
  soft: "柔",
  pink: "粉",
  festive: "节庆",
  verdant: "葱郁",
  layered: "层叠",
  stone: "石",
  texture: "肌理",
  ridge: "山脊",
  contour: "轮廓",
  majestic: "雄浑",
  calm: "静定",
  luminous: "清辉",
  crescent: "弯月",
  arc: "弧线",
  silver: "银",
  glow: "辉光",
  quiet: "清寂",
  rhythm: "节律",
  swirling: "回旋",
  auspicious: "吉祥",
  floating: "浮动",
  airy: "空灵",
  modern: "现代",
  traditional: "传统",
};

export function getStylePresetLabel(stylePreset: StylePreset): string {
  return STYLE_LABELS[stylePreset];
}

export function getScenePresetLabel(scenePreset: ScenePreset): string {
  return SCENE_LABELS[scenePreset];
}

export function getRatioPresetLabel(ratioPreset: RatioPreset): string {
  return RATIO_LABELS[ratioPreset];
}

export function getGenerationStatusLabel(status: GenerationStatus): string {
  return GENERATION_STATUS_LABELS[status];
}

export function getAnalysisStatusLabel(status: string): string {
  return ANALYSIS_STATUS_LABELS[status] ?? status;
}

export function getEditorSaveStatusLabel(status: string): string {
  return EDITOR_SAVE_STATUS_LABELS[status] ?? status;
}

export function getFontFamilyLabel(fontFamily: string): string {
  return FONT_FAMILY_LABELS[fontFamily] ?? fontFamily;
}

export function getDesignKeywordLabel(keyword: string): string {
  const normalizedKeyword = keyword.trim().toLowerCase();
  if (!normalizedKeyword) {
    return keyword;
  }

  const phraseLabel = KEYWORD_PHRASE_LABELS[normalizedKeyword];
  if (phraseLabel) {
    return phraseLabel;
  }

  const tokens = normalizedKeyword.split(/[\s-]+/).filter(Boolean);
  const translatedTokens = tokens.map((token) => KEYWORD_TOKEN_LABELS[token] ?? token);
  return translatedTokens.join("");
}
