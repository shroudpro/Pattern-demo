'use client';

import React, { useState, useEffect } from 'react';
import { HanziParticleCanvas } from './HanziParticleCanvas';
import type { CharacterAnalysis, LiteraryQuote } from '@/types/analysis';

interface HanziParticleIntroProps {
  analysis: CharacterAnalysis;
  character: string;
  onComplete: () => void;
}

const QUOTE_ANCHORS = [
  { left: "21%", top: "19%", maxWidth: "300px", driftX: "10px", driftY: "-12px" },
  { left: "78%", top: "19%", maxWidth: "320px", driftX: "-12px", driftY: "-10px" },
  { left: "20%", top: "42%", maxWidth: "280px", driftX: "12px", driftY: "9px" },
  { left: "84%", top: "42%", maxWidth: "280px", driftX: "-10px", driftY: "12px" },
  { left: "24%", top: "68%", maxWidth: "300px", driftX: "9px", driftY: "-10px" },
  { left: "80%", top: "68%", maxWidth: "310px", driftX: "-13px", driftY: "8px" },
  { left: "38%", top: "18%", maxWidth: "260px", driftX: "8px", driftY: "11px" },
  { left: "67%", top: "18%", maxWidth: "260px", driftX: "-8px", driftY: "10px" },
];

const FAR_DUST_GLYPHS = [
  "山", "水", "月", "云", "风", "竹", "茶", "龙",
  "礼", "和", "梦", "光", "川", "泉", "松", "石",
  "青", "岚", "渊", "照", "归", "远", "静", "清",
];

export function HanziParticleIntro({ analysis, character, onComplete }: HanziParticleIntroProps) {
  const [progress, setProgress] = useState(0);
  const [isIdle, setIsIdle] = useState(false);
  const [isFadingOut, setIsFadingOut] = useState(false);
  const [isWaking, setIsWaking] = useState(false);
  const [hasStarted, setHasStarted] = useState(false);
  const [reducedMotion, setReducedMotion] = useState(false);

  useEffect(() => {
    setReducedMotion(window.matchMedia('(prefers-reduced-motion: reduce)').matches);
  }, []);

  const handleWake = () => {
    if (reducedMotion) {
      setProgress(1);
      setIsIdle(true);
      setHasStarted(true);
      return;
    }
    
    setHasStarted(true);
    setIsWaking(true);
    let startTime: number | null = null;
    const duration = 4000; 
    let frameId: number;
    
    const animate = (timestamp: number) => {
      if (!startTime) startTime = timestamp;
      const elapsed = timestamp - startTime;
      
      let p = elapsed / duration;
      if (p >= 1) {
        p = 1;
        setProgress(p);
        setIsIdle(true);
        setIsWaking(false);
      } else {
        setProgress(p);
        frameId = requestAnimationFrame(animate);
      }
    };
    
    frameId = requestAnimationFrame(animate);
  };

  const handleEnter = () => {
    setIsFadingOut(true);
    setTimeout(() => {
      onComplete();
    }, 800);
  };

  const literaryQuotes = analysis.literaryQuotes.slice(0, 8);
  const shouldShowLiteraryLayer = isIdle && progress >= 1;

  return (
    <div className={`hanzi-particle-universe fixed inset-0 z-[100] transition-opacity duration-[800ms] ${isFadingOut ? 'opacity-0 pointer-events-none' : 'opacity-100'}`}>
      <div className="hanzi-particle-universe__dust" aria-hidden="true">
        {FAR_DUST_GLYPHS.map((glyph, index) => (
          <span
            key={`${glyph}-${index}`}
            className="hanzi-particle-universe__dust-glyph"
            style={{
              left: `${8 + ((index * 17) % 86)}%`,
              top: `${7 + ((index * 29) % 84)}%`,
              fontSize: `${12 + ((index * 7) % 26)}px`,
              animationDelay: `${(index % 12) * -1.7}s`,
              ['--dust-drift-x' as string]: `${index % 2 === 0 ? 18 : -22}px`,
              ['--dust-drift-y' as string]: `${index % 3 === 0 ? -16 : 14}px`,
            } as React.CSSProperties}
          >
            {index % 5 === 0 ? character : glyph}
          </span>
        ))}
      </div>
      <HanziParticleCanvas key={character} character={character} progress={progress} isIdle={isIdle} />

      {shouldShowLiteraryLayer && (
        <div className="hanzi-literary-layer" aria-hidden="true">
          <p className="hanzi-literary-layer__shuowen">{analysis.shuowenOriginal}</p>
          {literaryQuotes.map((quote, index) => {
            const anchor = QUOTE_ANCHORS[index % QUOTE_ANCHORS.length];

            return (
              <p
                key={`${quote.text}-${quote.source}-${index}`}
                className="hanzi-literary-layer__quote"
                style={{
                  left: anchor.left,
                  top: anchor.top,
                  maxWidth: anchor.maxWidth,
                  animationDelay: `${index * 0.12}s, ${2.6 + index * 0.12}s`,
                  ['--quote-drift-x' as string]: anchor.driftX,
                  ['--quote-drift-y' as string]: anchor.driftY,
                } as React.CSSProperties}
              >
                <span>{renderHighlightedQuoteText(quote, character)}</span>
                <span className="hanzi-literary-layer__source">-{formatQuoteSource(quote.source)}</span>
              </p>
            );
          })}
        </div>
      )}
      
      <div className="absolute inset-0 z-[4] flex flex-col items-center justify-between pointer-events-none pb-20 pt-10">
        <div /> {/* Spacer */}
        
        {!hasStarted && !isWaking && (
           <div className="flex flex-col items-center pointer-events-auto mt-auto">
             <button 
               onClick={handleWake}
               className="px-8 py-3 rounded-full border border-white/20 text-[#e8d8b8] bg-black/40 backdrop-blur-sm hover:bg-white/10 transition-colors font-serif tracking-widest text-lg"
             >
               唤醒汉字
             </button>
           </div>
        )}
      
        {isIdle && (
          <div className="flex flex-col items-center gap-3 pointer-events-auto mt-auto">
             <button 
               onClick={handleEnter}
               className="px-8 py-3 rounded-full border border-white/20 text-[#e8d8b8] bg-black/40 backdrop-blur-sm hover:bg-white/10 transition-colors font-serif tracking-widest"
             >
               进入文化星图
             </button>
             <p className="text-white/60 font-serif tracking-widest text-sm animate-pulse">
               移动鼠标，扰动汉字粒子
             </p>
          </div>
        )}
      </div>
    </div>
  );
}

function formatQuoteSource(source: string): string {
  const normalized = source.replace(/[《》]/g, "·").replace(/·+/g, "·").replace(/^·|·$/g, "");
  return `《${normalized || "古典诗文"}》`;
}

function renderHighlightedQuoteText(quote: LiteraryQuote, character: string) {
  const keywords = Array.from(new Set([character, ...quote.keywords].filter(Boolean))).sort((a, b) => b.length - a.length);
  if (!keywords.length) {
    return quote.text;
  }

  const pattern = new RegExp(`(${keywords.map(escapeRegExp).join("|")})`, "g");
  return quote.text.split(pattern).map((part, index) => {
    if (!part) return null;
    const isKeyword = keywords.includes(part);
    return isKeyword ? (
      <strong key={`${part}-${index}`}>{part}</strong>
    ) : (
      <React.Fragment key={`${part}-${index}`}>{part}</React.Fragment>
    );
  });
}

function escapeRegExp(value: string): string {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}
