import { ErrorState } from "@/components/shared/ErrorState";
import { AppStageShell } from "@/components/layout/AppStageShell";
import { PageHeader } from "@/components/shared/PageHeader";
import { FabricEditorShell } from "@/features/editor/FabricEditorShell";
import { getStaticDemoCharacter, isDemoSlug, getCharacterBySlug } from "@/lib/demo/static-demo-data";
import { FINAL_ASSETS } from "@/lib/design/content";

interface EditorPageProps {
  params: Promise<{ slug: string }>;
}

export function generateStaticParams() {
  return [{ slug: "shan" }, { slug: "yue" }];
}

export default async function EditorPage({ params }: EditorPageProps) {
  try {
    const { slug } = await params;

    if (!isDemoSlug(slug)) {
      return <ErrorState detail="当前静态演示版仅支持：山、月。" title="编辑器加载失败" />;
    }

    const character = getCharacterBySlug(slug);
    const demo = getStaticDemoCharacter(character);

    if (!demo) {
      return <ErrorState detail="当前静态演示版仅支持：山、月。" title="编辑器加载失败" />;
    }

    return (
      <AppStageShell backgroundImage={FINAL_ASSETS.editorWorkspaceBackground} contentClassName="stage-shell__content--editor-wide">
        <div className="space-y-8">
          <PageHeader
            backHref={`/generate/${slug}`}
            description="以生成出的最终文化解析图为底图，添加少量注释并导出可用于展示的 PNG 成品。"
            descriptionClassName="text-[#5f4227]"
            title={`${demo.character} · 解析图微调`}
            titleClassName="font-[var(--font-display)] text-[#4c2e18]"
          />
          <FabricEditorShell demo={demo} />
        </div>
      </AppStageShell>
    );
  } catch (error) {
    const detail = error instanceof Error ? error.message : "编辑器加载失败。";
    return <ErrorState detail={detail} title="编辑器加载失败" />;
  }
}
