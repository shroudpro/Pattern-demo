import { AppStageShell } from "@/components/layout/AppStageShell";
import { ErrorState } from "@/components/shared/ErrorState";
import { PageHeader } from "@/components/shared/PageHeader";
import { AnalysisResultView } from "@/features/analyze/AnalysisResultView";
import { FINAL_ASSETS } from "@/lib/design/content";
import { AnalyzeIntroWrapper } from "@/features/analyze/AnalyzeIntroWrapper";
import { DEMO_CHARACTER_KEYS, getStaticDemoCharacter } from "@/lib/demo/static-demo-data";

interface AnalyzePageProps {
  params: Promise<{ sessionId: string }>;
}

export function generateStaticParams() {
  return DEMO_CHARACTER_KEYS.map((sessionId) => ({ sessionId: encodeURIComponent(sessionId) }));
}

export default async function AnalyzePage({ params }: AnalyzePageProps) {
  try {
    const { sessionId } = await params;
    const demo = getStaticDemoCharacter(decodeURIComponent(sessionId));

    if (!demo) {
      return <ErrorState detail="当前静态演示版仅支持：山、月。" title="分析页加载失败" />;
    }

    return (
      <>
        <AnalyzeIntroWrapper key={demo.character} analysis={demo.analysis} character={demo.character} />
        <AppStageShell backgroundImage={FINAL_ASSETS.analyzeOceanBackground} className="stage-shell--analyze" contentClassName="max-w-[1440px]">
          <div className="space-y-8">
            <PageHeader
              backHref="/create"
              description="字海聚焦目标汉字，展开字源、现代释义、文化意象和诗词关联的结构化星图。"
              descriptionClassName="text-[#e8d8b8]"
              title={`${demo.character} · 汉字文化星图`}
              titleClassName="font-[var(--font-display)] text-[#fff3dd]"
            />
            <AnalysisResultView demo={demo} />
          </div>
        </AppStageShell>
      </>
    );
  } catch (error) {
    const detail = error instanceof Error ? error.message : "分析结果加载失败。";
    return <ErrorState detail={detail} title="分析页加载失败" />;
  }
}
