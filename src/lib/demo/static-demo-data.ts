import type { CharacterAnalysis } from "@/types/analysis";

export type DemoCharacterKey = "山" | "月";

/** 用于路由路径的英文 slug，避免中文 URL 编码兼容问题 */
export type DemoSlug = "shan" | "yue";

export const DEMO_SLUG_TO_CHARACTER: Record<DemoSlug, DemoCharacterKey> = {
  shan: "山",
  yue: "月",
};

export const DEMO_CHARACTER_TO_SLUG: Record<DemoCharacterKey, DemoSlug> = {
  山: "shan",
  月: "yue",
};

export function isDemoSlug(value: string): value is DemoSlug {
  return value === "shan" || value === "yue";
}

export function getCharacterBySlug(slug: DemoSlug): DemoCharacterKey {
  return DEMO_SLUG_TO_CHARACTER[slug];
}

export function getSlugByCharacter(character: DemoCharacterKey): DemoSlug {
  return DEMO_CHARACTER_TO_SLUG[character];
}

export type DemoGenerationStatus = "idle" | "submitting" | "queued" | "generating" | "succeeded" | "failed";

export interface StaticDemoCharacter {
  character: DemoCharacterKey;
  analysis: CharacterAnalysis;
  outputImageUrl: string;
  canvasWidth: number;
  canvasHeight: number;
}

export const DEMO_CHARACTER_KEYS: DemoCharacterKey[] = ["山", "月"];

export const STATIC_DEMO_CHARACTERS: Record<DemoCharacterKey, StaticDemoCharacter> = {
  山: {
    character: "山",
    outputImageUrl: "/img/山.png",
    canvasWidth: 1672,
    canvasHeight: 941,
    analysis: {
      character: "山",
      validated: true,
      subtitle: "高峻、静穆、归隐与精神高度",
      shuowenOriginal: "山，宣也。宣气散，生万物，有石而高。",
      shuowenExplanation: "《说文解字》将山解释为天地之气宣散、生发万物之处，强调其高起、有石、聚气的特征。",
      modernMeaning: "山指地面上由岩石、土壤构成的高大隆起，也常象征稳定、崇高、阻隔、归隐与精神高度。",
      imageryAnalysis:
        "山的意象具有多层结构。作为自然物，它代表高峻、厚重、稳定与空间纵深；作为人格象征，它常被用来表达坚毅、沉静、不可动摇的精神品质；作为审美对象，它与云、水、松、月共同构成中国山水画中的核心视觉秩序；作为文化符号，它连接隐逸传统、宗教修行、文人理想和家国疆域。",
      poems: [
        {
          line: "会当凌绝顶，一览众山小。",
          author: "杜甫",
          title: "望岳",
          explanation: "写出登临高处后的胸襟与气势。",
        },
        {
          line: "空山新雨后，天气晚来秋。",
          author: "王维",
          title: "山居秋暝",
          explanation: "呈现山中清寂、雨后澄明的审美境界。",
        },
        {
          line: "相看两不厌，只有敬亭山。",
          author: "李白",
          title: "独坐敬亭山",
          explanation: "将山转化为可对望、可寄情的精神对象。",
        },
      ],
      literaryQuotes: [
        { text: "高山仰止，景行行止。", source: "诗经·小雅·车舝", keywords: ["山", "高山"] },
        { text: "会当凌绝顶，一览众山小。", source: "杜甫《望岳》", keywords: ["山"] },
        { text: "空山新雨后，天气晚来秋。", source: "王维《山居秋暝》", keywords: ["山"] },
        { text: "相看两不厌，只有敬亭山。", source: "李白《独坐敬亭山》", keywords: ["山"] },
        { text: "采菊东篱下，悠然见南山。", source: "陶渊明《饮酒》", keywords: ["山"] },
        { text: "千山鸟飞绝，万径人踪灭。", source: "柳宗元《江雪》", keywords: ["山"] },
        { text: "不识庐山真面目，只缘身在此山中。", source: "苏轼《题西林壁》", keywords: ["山"] },
        { text: "山重水复疑无路，柳暗花明又一村。", source: "陆游《游山西村》", keywords: ["山"] },
      ],
      visualMotifs: ["层峦", "云气", "石脉", "松树", "远山", "留白"],
      colorPalette: ["墨黑", "石青", "云白", "黛绿"],
      atmosphereTags: ["高远", "静穆", "厚重", "空灵"],
      forbiddenElements: ["现代城市高楼", "卡通山峰", "英文大字"],
      layoutPriority: { imagery: "high", shuowen: "medium", poems: "medium" },
      backgroundPromptKeywords: ["layered mountains", "mist", "stone texture", "pine", "rice paper"],
      commonImages: ["层峦", "云气", "石脉", "松树", "远山", "留白"],
      classicalPoems: ["会当凌绝顶，一览众山小。", "空山新雨后，天气晚来秋。", "相看两不厌，只有敬亭山。"],
      designKeywords: ["layered mountains", "mist", "stone texture", "pine", "rice paper"],
      summary: "山适合转译为层峦、石脉、云气与留白共同构成的文化解析图，重点呈现高远空间感和沉静精神性。",
    },
  },
  月: {
    character: "月",
    outputImageUrl: "/img/月.png",
    canvasWidth: 1672,
    canvasHeight: 941,
    analysis: {
      character: "月",
      validated: true,
      subtitle: "清辉、思念、圆缺与时间节律",
      shuowenOriginal: "月，阙也。大阴之精。象形。",
      shuowenExplanation: "月字以弧形轮廓呈现月体盈亏，古义强调阴柔、周期和夜空秩序。",
      modernMeaning: "月指地球的天然卫星，也常象征团圆、思念、清辉、静夜和时间循环。",
      imageryAnalysis:
        "月在汉字文化中连接天体秩序与人间情感。它既是夜色中的光源，也承载故乡、亲友、团圆和孤独等情绪。视觉转译应突出弧线、圆轮、银辉、云影与夜色留白，避免把月做成单纯装饰符号。",
      poems: [
        {
          line: "举头望明月，低头思故乡。",
          author: "李白",
          title: "静夜思",
          explanation: "以望月触发乡愁，是月意象最典型的情感表达。",
        },
        {
          line: "海上生明月，天涯共此时。",
          author: "张九龄",
          title: "望月怀远",
          explanation: "以同一轮明月连接远方之人。",
        },
      ],
      literaryQuotes: [
        { text: "举头望明月，低头思故乡。", source: "李白《静夜思》", keywords: ["月"] },
        { text: "海上生明月，天涯共此时。", source: "张九龄《望月怀远》", keywords: ["月"] },
        { text: "明月松间照，清泉石上流。", source: "王维《山居秋暝》", keywords: ["月"] },
        { text: "春江潮水连海平，海上明月共潮生。", source: "张若虚《春江花月夜》", keywords: ["月"] },
        { text: "露从今夜白，月是故乡明。", source: "杜甫《月夜忆舍弟》", keywords: ["月"] },
        { text: "月出惊山鸟，时鸣春涧中。", source: "王维《鸟鸣涧》", keywords: ["月"] },
        { text: "人有悲欢离合，月有阴晴圆缺。", source: "苏轼《水调歌头》", keywords: ["月"] },
        { text: "秦时明月汉时关，万里长征人未还。", source: "王昌龄《出塞》", keywords: ["月"] },
      ],
      visualMotifs: ["满月", "弯月", "月华", "云影", "松间", "夜色"],
      colorPalette: ["银白", "玄青", "雾蓝", "淡金"],
      atmosphereTags: ["清寂", "思念", "澄明", "柔和"],
      forbiddenElements: ["科幻星球", "卡通月亮", "英文星座"],
      layoutPriority: { poems: "high", imagery: "medium", shuowen: "medium" },
      backgroundPromptKeywords: ["moonlight", "silver glow", "night sky", "cloud veil", "pine shadow"],
      commonImages: ["满月", "弯月", "月华", "云影", "松间", "夜色"],
      classicalPoems: ["举头望明月，低头思故乡。", "海上生明月，天涯共此时。", "明月松间照，清泉石上流。"],
      designKeywords: ["moonlight", "silver glow", "night sky", "cloud veil", "pine shadow"],
      summary: "月适合生成清辉环绕、圆缺呼应的解析图，以诗词和情绪层为视觉重点。",
    },
  },
};

export function isSupportedDemoCharacter(value: string): value is DemoCharacterKey {
  return DEMO_CHARACTER_KEYS.includes(value as DemoCharacterKey);
}

export function getStaticDemoCharacter(value: string): StaticDemoCharacter | null {
  if (!isSupportedDemoCharacter(value)) {
    return null;
  }

  return STATIC_DEMO_CHARACTERS[value];
}
