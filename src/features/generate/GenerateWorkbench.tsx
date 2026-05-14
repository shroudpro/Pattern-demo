"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";

import { RadialLoading } from "@/components/motion/RadialLoading";
import { TextureButton } from "@/components/shared/TextureButton";
import { DESIGN_ASSETS, shouldShowRadialLoading } from "@/lib/design/content";
import { getGenerationStatusLabel } from "@/lib/formatters/display";
import type { DemoGenerationStatus, StaticDemoCharacter } from "@/lib/demo/static-demo-data";

interface GenerateWorkbenchProps {
  demo: StaticDemoCharacter;
}

const GENERATION_STEPS = [
  { title: "提交请求", description: "正在创建静态演示生成任务。" },
  { title: "任务排队", description: "演示任务已进入队列，准备生成最终文化解析图。" },
  { title: "正在生成", description: "系统正在合成固定演示结果，请稍候。" },
  { title: "生成完成", description: "最终效果图已准备完成，可进入编辑器微调。" },
] as const;

const DEMO_TIMELINE = [
  { delay: 0, status: "submitting", stepIndex: 0 },
  { delay: 800, status: "queued", stepIndex: 1 },
  { delay: 1800, status: "generating", stepIndex: 2 },
  { delay: 4000, status: "succeeded", stepIndex: 3 },
] as const;

export function GenerateWorkbench({ demo }: GenerateWorkbenchProps) {
  const timersRef = useRef<number[]>([]);
  const [status, setStatus] = useState<DemoGenerationStatus>("idle");
  const [activeStepIndex, setActiveStepIndex] = useState<number | null>(null);
  const [hasGenerated, setHasGenerated] = useState(false);

  useEffect(() => {
    return () => {
      timersRef.current.forEach((timerId) => window.clearTimeout(timerId));
      timersRef.current = [];
    };
  }, []);

  function handleGenerate() {
    timersRef.current.forEach((timerId) => window.clearTimeout(timerId));
    timersRef.current = [];
    setHasGenerated(false);

    DEMO_TIMELINE.forEach((item) => {
      const timerId = window.setTimeout(() => {
        setStatus(item.status);
        setActiveStepIndex(item.stepIndex);
        if (item.status === "succeeded") {
          setHasGenerated(true);
        }
      }, item.delay);
      timersRef.current.push(timerId);
    });
  }

  const showRadialLoading = shouldShowRadialLoading(status, false);
  const nextEditorLink = hasGenerated ? `/editor/${demo.character}` : null;

  return (
    <div className="grid gap-6 lg:grid-cols-[minmax(0,0.8fr)_minmax(0,1.2fr)]">
      <section className="ornate-panel p-6">
        <h2 className="font-[var(--font-display)] text-[24px] text-[#4c2e18]">生成配置</h2>
        <p className="mt-2 text-[14px] leading-6 text-[#6b5336]">
          当前汉字：{demo.character}。静态演示版将保留生成过程动画，并在 4 秒后展示固定文化解析图。
        </p>
        <div className="mt-6 space-y-5">
          <div className="space-y-2">
            <label className="block text-[14px] font-medium text-[#4c2e18]">演示风格</label>
            <div className="flex gap-3">
              <button className="stage-option px-4 py-2" data-active type="button">
                传统解析图
              </button>
              <button className="stage-option px-4 py-2 opacity-60" disabled type="button">
                现代解析图
              </button>
            </div>
          </div>
          <div className="space-y-2">
            <label className="block text-[14px] font-medium text-[#4c2e18]">解析图比例</label>
            <div className="flex gap-3">
              <button className="stage-option px-4 py-2" data-active type="button">
                16:9 横屏解析图
              </button>
            </div>
          </div>
        </div>
        <div
          className="mt-6 overflow-hidden rounded-[8px] bg-center bg-cover bg-no-repeat p-4 shadow-[0_8px_24px_rgba(52,30,15,0.12)]"
          style={{ backgroundImage: `linear-gradient(rgba(255,248,236,0.72), rgba(255,248,236,0.72)), url(${DESIGN_ASSETS.promptBackground})` }}
        >
          <p className="text-[14px] font-medium text-[#4c2e18]">生成依据</p>
          <p className="mt-3 text-[14px] leading-6 text-[#5f4227]">{demo.analysis.summary}</p>
          <div className="mt-3 flex flex-wrap gap-2">
            {[...demo.analysis.visualMotifs, ...demo.analysis.atmosphereTags].slice(0, 8).map((item) => (
              <span key={item} className="rounded-full border border-[rgba(107,66,38,0.18)] bg-[rgba(255,248,236,0.66)] px-3 py-1 text-[12px] text-[#5f4227]">
                {item}
              </span>
            ))}
          </div>
        </div>
        <div className="mt-6 flex flex-wrap gap-3">
          <TextureButton backgroundImage={DESIGN_ASSETS.buttonBackground} disabled={showRadialLoading} onClick={handleGenerate} type="button">
            {hasGenerated ? "重新生成解析图" : "生成文化解析图"}
          </TextureButton>
        </div>
      </section>

      <section className="ornate-panel p-6">
        <h2 className="font-[var(--font-display)] text-[24px] text-[#4c2e18]">任务状态</h2>
        <p className="mt-2 text-[14px] text-[#6b5336]">静态演示状态流：空闲 / 提交中 / 排队中 / 生成中 / 已完成</p>
        <div className="mt-6 rounded-[8px] bg-[rgba(255,248,236,0.58)] p-4 text-[14px] text-[#4c2e18]">
          当前状态：<span className="font-medium text-[#43210e]">{getGenerationStatusLabel(status)}</span>
        </div>
        <div className="mt-4 space-y-3">
          {GENERATION_STEPS.map((step, index) => {
            const isCompleted = activeStepIndex !== null && index < activeStepIndex;
            const isActive = activeStepIndex === index && status !== "failed";
            return (
              <div
                key={step.title}
                className={`rounded-[8px] border p-4 ${
                  isActive
                    ? "border-[rgba(107,66,38,0.48)] bg-[rgba(255,248,236,0.76)]"
                    : isCompleted
                      ? "border-[rgba(106,138,101,0.48)] bg-[rgba(236,253,243,0.72)]"
                      : "border-[rgba(107,66,38,0.14)] bg-[rgba(255,248,236,0.54)]"
                }`}
              >
                <p className="text-[14px] font-medium text-[#43210e]">
                  {index + 1}. {step.title}
                </p>
                <p className="mt-1 text-[13px] text-[#6b5336]">{step.description}</p>
              </div>
            );
          })}
        </div>
        {showRadialLoading ? (
          <div className="mt-6 flex justify-center">
            <RadialLoading />
          </div>
        ) : null}
        {hasGenerated ? (
          <div className="mt-6 space-y-4">
            <div className="overflow-hidden rounded-[8px] border border-[rgba(107,66,38,0.18)] bg-[rgba(255,248,236,0.48)] p-3">
              <img alt={`${demo.character} 文化阐释效果图`} className="w-full rounded-[6px]" src={demo.outputImageUrl} />
            </div>
            {nextEditorLink ? (
              <Link
                className="texture-button"
                href={nextEditorLink}
                style={{ backgroundImage: `url(${DESIGN_ASSETS.buttonBackground})` }}
              >
                <span className="texture-button__label">进入微调导出</span>
              </Link>
            ) : null}
          </div>
        ) : (
          <p className="mt-4 text-[14px] text-[#7e6443]">尚未开始静态生成演示。</p>
        )}
      </section>
    </div>
  );
}
