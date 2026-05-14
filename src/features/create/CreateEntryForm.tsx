"use client";

import { useState } from "react";

import { useRouteTransition } from "@/components/motion/RouteTransitionProvider";
import { TextureButton } from "@/components/shared/TextureButton";
import { isSupportedDemoCharacter } from "@/lib/demo/static-demo-data";
import { DESIGN_ASSETS } from "@/lib/design/content";
import { isSingleCharacter, RECOMMENDED_CHARACTERS, S_GRADE_CHARACTERS } from "@/lib/constants/characters";

export function CreateEntryForm() {
  const { startRollTransition } = useRouteTransition();
  const [character, setCharacter] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const normalizedCharacter = character.trim();
    if (!isSingleCharacter(normalizedCharacter)) {
      setErrorMessage("请输入 1 个汉字。");
      return;
    }

    setSubmitting(true);
    setErrorMessage("");

    try {
      if (!isSupportedDemoCharacter(normalizedCharacter)) {
        setErrorMessage(`当前静态演示版仅支持：${S_GRADE_CHARACTERS.join("、")}。`);
        setSubmitting(false);
        return;
      }

      startRollTransition(`/analyze/${normalizedCharacter}`);
    } catch {
      setErrorMessage("演示页跳转失败，请重新选择山或月。");
      setSubmitting(false);
    }
  }

  return (
    <div className="max-w-[780px]">
      <form className="relative overflow-hidden rounded-[8px] shadow-[0_18px_40px_rgba(52,30,15,0.18)]" onSubmit={handleSubmit}>
        <div
          aria-hidden="true"
          className="absolute inset-0 bg-center bg-cover bg-no-repeat"
          style={{ backgroundImage: `url(${DESIGN_ASSETS.createInputBackground})` }}
        />
        <div aria-hidden="true" className="absolute inset-0 bg-[rgba(243,229,200,0.18)]" />
        <div className="relative flex min-h-[500px] flex-col justify-between p-6 sm:p-8">
          <div className="space-y-5">
            <div className="space-y-2">
              <p className="text-[14px] tracking-[0.12em] text-[#7f5e40]">以一字起意</p>
              <label className="block font-[var(--font-display)] text-[24px] text-[#4c2e18] sm:text-[32px]" htmlFor="character-input">
                输入一个汉字，开启文化解析
              </label>
              <p className="max-w-[430px] text-[14px] leading-6 text-[#6b4226]">
                一字一世界，万象由此生。探索它的字源、意象、诗意与视觉形态。
              </p>
            </div>
            <div className="group relative">
              <button
                aria-label="查看常见传统汉字提示"
                className="inline-flex h-7 w-7 items-center justify-center rounded-full border border-[rgba(107,66,38,0.3)] bg-[rgba(255,248,236,0.6)] text-[14px] font-semibold text-[#6b4226]"
                type="button"
              >
                问
              </button>
              <div className="pointer-events-none absolute left-10 top-1/2 z-10 hidden w-[320px] -translate-y-1/2 rounded-[8px] border border-[rgba(107,66,38,0.18)] bg-[rgba(255,250,241,0.96)] p-3 text-[12px] leading-5 text-[#5f4227] shadow-[0_8px_24px_rgba(0,0,0,0.08)] group-hover:block">
                S 级演示字：
                <span className="ml-1">{S_GRADE_CHARACTERS.join("、")}</span>
              </div>
            </div>
            <div className="max-w-[360px] space-y-4">
              <input
                id="character-input"
                className="ornate-input px-4 py-4 text-[24px] sm:text-[32px]"
                maxLength={1}
                onChange={(event) => setCharacter(event.target.value)}
                placeholder="例如：山"
                value={character}
              />
              {errorMessage ? <p className="text-[14px] text-[#b42318]">{errorMessage}</p> : null}
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-4">
            <TextureButton backgroundImage={DESIGN_ASSETS.buttonBackground} disabled={submitting} type="submit">
              {submitting ? "解析中..." : "生成文化解析"}
            </TextureButton>
            <p className="text-[14px] text-[#6b4226]">精品字库：{RECOMMENDED_CHARACTERS.slice(0, 12).join("、")}</p>
          </div>
        </div>
      </form>
    </div>
  );
}
