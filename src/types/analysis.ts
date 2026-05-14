export interface PoemAnalysis {
  line: string;
  author: string;
  title: string;
  explanation: string;
}

export interface LiteraryQuote {
  text: string;
  source: string;
  keywords: string[];
}

export interface CharacterAnalysis {
  character: string;
  validated: boolean;
  subtitle: string;
  shuowenOriginal: string;
  shuowenExplanation: string;
  modernMeaning: string;
  imageryAnalysis: string;
  poems: PoemAnalysis[];
  literaryQuotes: LiteraryQuote[];
  visualMotifs: string[];
  colorPalette: string[];
  atmosphereTags: string[];
  forbiddenElements: string[];
  layoutPriority: Record<string, string>;
  backgroundPromptKeywords: string[];
  commonImages: string[];
  classicalPoems: string[];
  designKeywords: string[];
  summary: string;
}
