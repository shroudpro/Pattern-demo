"use client";

import { useRouteTransition } from "@/components/motion/RouteTransitionProvider";
import { TextureButton } from "@/components/shared/TextureButton";
import { DESIGN_ASSETS } from "@/lib/design/content";
import type { DemoSlug, StaticDemoCharacter } from "@/lib/demo/static-demo-data";

import { HanziOceanStage } from "./HanziOceanStage";

interface AnalysisResultViewProps {
  demo: StaticDemoCharacter;
  slug: DemoSlug;
}

export function AnalysisResultView({ demo, slug }: AnalysisResultViewProps) {
  const { startRollTransition } = useRouteTransition();

  return (
    <div className="space-y-6">
      <HanziOceanStage demo={demo} />
      <section className="rounded-[8px] border border-[rgba(234,224,200,0.2)] bg-[rgba(18,20,20,0.66)] p-5 shadow-[0_16px_36px_rgba(0,0,0,0.18)] backdrop-blur-md">
        <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_auto] lg:items-center">
          <div>
            <h2 className="font-[var(--font-display)] text-[24px] text-[#fff3dd]">解析图生成依据</h2>
            <p className="mt-2 max-w-[820px] text-[14px] leading-6 text-[#d9c7a5]">
              {demo.analysis.summary}
            </p>
            <div className="mt-4 flex flex-wrap gap-2">
              {[...demo.analysis.visualMotifs, ...demo.analysis.atmosphereTags].slice(0, 10).map((item) => (
                <span key={item} className="rounded-full border border-[rgba(234,224,200,0.26)] bg-[rgba(255,248,236,0.1)] px-3 py-1 text-[13px] text-[#fff3dd]">
                  {item}
                </span>
              ))}
            </div>
          </div>
          <TextureButton
            backgroundImage={DESIGN_ASSETS.buttonBackground}
            className="justify-self-start lg:justify-self-end"
            onClick={() => startRollTransition(`/generate/${slug}`)}
          >
            进入生成阶段
          </TextureButton>
        </div>
      </section>
    </div>
  );
}
