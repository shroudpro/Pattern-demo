import { CreateEntryForm } from "@/features/create/CreateEntryForm";
import { AppStageShell } from "@/components/layout/AppStageShell";
import { PageHeader } from "@/components/shared/PageHeader";
import { DESIGN_ASSETS, FINAL_ASSETS } from "@/lib/design/content";

export default function CreatePage() {
  return (
    <AppStageShell
      backgroundImage={FINAL_ASSETS.createHeroBackground}
      contentClassName="flex min-h-screen flex-col justify-center"
      decorativeLayer={<img alt="" className="stage-cloud" src={DESIGN_ASSETS.cloud} />}
    >
      <div className="max-w-[1280px] space-y-10">
        <PageHeader
          className="space-y-5"
          description="AI 汉字文化意象可视化系统"
          descriptionClassName="max-w-[560px] text-[16px] leading-7 text-[#5f4227]"
          title="字象万千"
          titleClassName="font-[var(--font-display)] text-[32px] text-[#4c2e18] drop-shadow-[0_3px_10px_rgba(255,248,236,0.35)] lg:text-[56px]"
        />
        <CreateEntryForm />
      </div>
    </AppStageShell>
  );
}
