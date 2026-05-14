import { motion } from "framer-motion";

import { FINAL_ASSETS } from "@/lib/design/content";
import type { StaticDemoCharacter } from "@/lib/demo/static-demo-data";
import type { PoemAnalysis } from "@/types/analysis";

import { AnalysisOrbitCard } from "./AnalysisOrbitCard";
import { CulturalStarMap } from "./CulturalStarMap";

interface HanziOceanStageProps {
  demo: StaticDemoCharacter;
}

const OCEAN_PARTICLE_COUNT = 84;

export function HanziOceanStage({ demo }: HanziOceanStageProps) {
  const { analysis, character } = demo;
  const poems = getPoemItems(character, analysis.poems);
  const particles = buildHanziParticles(character, analysis.visualMotifs);

  return (
    <section
      className="relative min-h-[760px] overflow-hidden rounded-[8px] border border-[rgba(234,224,200,0.18)] bg-[#0c1112] shadow-[0_24px_60px_rgba(0,0,0,0.28)]"
      style={{ backgroundImage: `url(${FINAL_ASSETS.analyzeOceanBackground})`, backgroundPosition: "center", backgroundSize: "cover" }}
    >
      <div aria-hidden="true" className="absolute inset-0 bg-[linear-gradient(180deg,rgba(5,9,10,0.18)_0%,rgba(5,9,10,0.58)_100%)]" />
      <div aria-hidden="true" className="absolute inset-0 opacity-[0.16]" style={{ backgroundImage: `url(${FINAL_ASSETS.ricePaperOverlay})`, backgroundSize: "640px 640px" }} />
      <HanziOceanParticles particles={particles} />
      <CulturalStarMap />

      <div className="relative z-10 grid min-h-[760px] gap-5 p-5 lg:grid-cols-[minmax(250px,0.86fr)_minmax(320px,0.9fr)_minmax(250px,0.86fr)] lg:grid-rows-[auto_1fr_auto] lg:p-7">
        <AnalysisOrbitCard className="lg:col-start-1 lg:row-start-1" kicker="ORIGIN" title="说文解字">
          <p>{analysis.shuowenOriginal}</p>
          <p className="mt-2 text-[#d9c7a5]">{analysis.shuowenExplanation}</p>
        </AnalysisOrbitCard>

        <AnalysisOrbitCard className="lg:col-start-3 lg:row-start-1" kicker="IMAGERY" title="意象分析">
          <p>{analysis.imageryAnalysis}</p>
        </AnalysisOrbitCard>

        <div className="flex min-h-[360px] items-center justify-center [perspective:1100px] lg:col-start-2 lg:row-span-3 lg:row-start-1">
          <motion.div
            animate={{ rotateX: [8, -5, 8], rotateY: [-12, 10, -12], y: [0, -10, 0], scale: [1, 1.02, 1] }}
            className="relative flex aspect-square w-full max-w-[420px] items-center justify-center [transform-style:preserve-3d]"
            transition={{ duration: 7, ease: "easeInOut", repeat: Infinity }}
          >
            <img aria-hidden="true" alt="" className="absolute inset-0 h-full w-full object-contain opacity-95 mix-blend-screen" src={FINAL_ASSETS.analyzeFocusGlow} />
            <div aria-hidden="true" className="absolute h-[62%] w-[62%] rounded-full bg-[radial-gradient(circle,rgba(224,178,92,0.28)_0%,rgba(224,178,92,0.08)_48%,rgba(224,178,92,0)_72%)] blur-xl" />
            <div className="relative text-center">
              <p className="hanzi-focus-glyph font-[var(--font-display)] text-[112px] leading-none text-[#fff6e7] sm:text-[148px]">
                {character}
              </p>
              <p className="mx-auto mt-4 max-w-[320px] text-[15px] leading-7 text-[#eadfc9]">{analysis.subtitle}</p>
            </div>
          </motion.div>
        </div>

        <AnalysisOrbitCard className="lg:col-start-1 lg:row-start-3" kicker="MODERN" title="现代释义">
          <p>{analysis.modernMeaning}</p>
        </AnalysisOrbitCard>

        <AnalysisOrbitCard className="lg:col-start-3 lg:row-start-3" kicker="POETRY" title="诗词关联">
          <div className="analysis-hidden-scrollbar max-h-[220px] space-y-4 overflow-y-auto overflow-x-hidden pr-1">
            {poems.map((poem) => (
              <div key={`${poem.author}-${poem.title}-${poem.line}`} className="border-b border-[rgba(234,224,200,0.12)] pb-3 last:border-b-0 last:pb-0">
                <p className="text-[15px] leading-7 text-[#fff3dd]">{poem.line}</p>
                <p className="mt-1 text-[13px] text-[#c7a968]">
                  {poem.author}《{poem.title}》
                </p>
                <p className="mt-2 text-[13px] leading-6 text-[#eadfc9]">意象解析：{poem.explanation}</p>
              </div>
            ))}
          </div>
        </AnalysisOrbitCard>
      </div>
    </section>
  );
}

function HanziOceanParticles({ particles }: { particles: Array<{ value: string; left: number; top: number; size: number; delay: number; opacity: number }> }) {
  return (
    <div aria-hidden="true" className="absolute inset-0 overflow-hidden">
      {particles.map((particle, index) => (
        <span
          key={`${particle.value}-${index}`}
          className="hanzi-ocean-particle"
          style={{
            left: `${particle.left}%`,
            top: `${particle.top}%`,
            fontSize: `${particle.size}px`,
            opacity: particle.opacity,
            animationDelay: `${particle.delay}s`,
          }}
        >
          {particle.value}
        </span>
      ))}
    </div>
  );
}

function buildHanziParticles(character: string, motifs: string[]) {
  const particleSource = [character, ...motifs.join("").split("").filter(Boolean)];
  const safeSource = particleSource.length ? particleSource : [character];

  return Array.from({ length: OCEAN_PARTICLE_COUNT }, (_, index) => {
    const seed = index + 1;
    return {
      value: safeSource[index % safeSource.length],
      left: (seed * 37) % 100,
      top: (seed * 53) % 100,
      size: 18 + ((seed * 11) % 34),
      delay: ((seed * 7) % 18) / 10,
      opacity: 0.12 + (((seed * 13) % 28) / 100),
    };
  });
}

function getPoemItems(character: string, poems: PoemAnalysis[]) {
  if (poems.length >= 2) {
    return poems.slice(0, 3);
  }

  return [
    ...poems,
    {
      line: `以“${character}”入画，观其形，得其意。`,
      author: "系统",
      title: "文化解析",
      explanation: "当前汉字诗词条目不足，系统以文化摘要补充其形、意、境之间的视觉关联。",
    },
  ].slice(0, 3);
}
