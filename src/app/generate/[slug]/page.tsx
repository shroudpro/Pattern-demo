import { ErrorState } from "@/components/shared/ErrorState";
import { AppStageShell } from "@/components/layout/AppStageShell";
import { PageHeader } from "@/components/shared/PageHeader";
import { GenerateWorkbench } from "@/features/generate/GenerateWorkbench";
import { getStaticDemoCharacter, isDemoSlug, getCharacterBySlug } from "@/lib/demo/static-demo-data";
import { FINAL_ASSETS } from "@/lib/design/content";

interface GeneratePageProps {
  params: Promise<{ slug: string }>;
}

export function generateStaticParams() {
  return [{ slug: "shan" }, { slug: "yue" }];
}

export default async function GeneratePage({ params }: GeneratePageProps) {
  try {
    const { slug } = await params;

    if (!isDemoSlug(slug)) {
      return <ErrorState detail="当前静态演示版仅支持：山、月。" title="生成页加载失败" />;
    }

    const character = getCharacterBySlug(slug);
    const demo = getStaticDemoCharacter(character);

    if (!demo) {
      return <ErrorState detail="当前静态演示版仅支持：山、月。" title="生成页加载失败" />;
    }

    return (
      <AppStageShell backgroundImage={FINAL_ASSETS.globalDarkBackground}>
        <div className="space-y-8">
          <PageHeader
            backHref={`/analyze/${slug}`}
            description="选择解析图风格与比例，系统将直接生成接近成品展示的汉字文化阐释效果图。"
            descriptionClassName="text-[#eadfc7]"
            title={`${demo.character} · 生成配置`}
            titleClassName="font-[var(--font-display)] text-[#fff4df]"
          />
          <GenerateWorkbench demo={demo} slug={slug} />
        </div>
      </AppStageShell>
    );
  } catch (error) {
    const detail = error instanceof Error ? error.message : "生成页加载失败。";
    return <ErrorState detail={detail} title="生成页加载失败" />;
  }
}
