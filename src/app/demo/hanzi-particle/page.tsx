'use client';

import React, { useState } from 'react';
import { HanziParticleCanvas } from '@/features/analyze/HanziParticleCanvas';

export default function HanziParticleDemo() {
  const [character, setCharacter] = useState('山');
  const [progress, setProgress] = useState(0);
  const [isIdle, setIsIdle] = useState(false);
  const [animating, setAnimating] = useState(false);

  const handleWake = () => {
    if (animating) return;
    setAnimating(true);
    
    let startTime: number | null = null;
    const duration = 4000;
    
    const animate = (timestamp: number) => {
      if (!startTime) startTime = timestamp;
      const elapsed = timestamp - startTime;
      
      let p = elapsed / duration;
      if (p >= 1) {
        setProgress(1);
        setIsIdle(true);
        setAnimating(false);
      } else {
        setProgress(p);
        requestAnimationFrame(animate);
      }
    };
    
    requestAnimationFrame(animate);
  };

  const handleReset = () => {
    setProgress(0);
    setIsIdle(false);
    setAnimating(false);
  };

  return (
    <div className="hanzi-particle-universe fixed inset-0 overflow-hidden">
      <HanziParticleCanvas key={character} character={character} progress={progress} isIdle={isIdle} />
      
      <div className="absolute bottom-10 left-1/2 z-[4] flex -translate-x-1/2 flex-col items-center gap-6">
        <p className="text-[#e5d5b5]/60 text-sm tracking-widest font-light pointer-events-none">
          移动鼠标，扰动汉字粒子
        </p>
        
        <div className="flex gap-4">
          <button 
            onClick={() => { setCharacter('山'); handleReset(); }}
            className={`px-6 py-2 border rounded transition-colors ${character === '山' ? 'border-[#e5d5b5] text-[#e5d5b5] bg-[#e5d5b5]/10' : 'border-[#e5d5b5]/30 text-[#e5d5b5]/60 hover:border-[#e5d5b5]/60'}`}
          >
            山
          </button>
          <button 
            onClick={() => { setCharacter('水'); handleReset(); }}
            className={`px-6 py-2 border rounded transition-colors ${character === '水' ? 'border-[#e5d5b5] text-[#e5d5b5] bg-[#e5d5b5]/10' : 'border-[#e5d5b5]/30 text-[#e5d5b5]/60 hover:border-[#e5d5b5]/60'}`}
          >
            水
          </button>
        </div>
        
        <div className="flex gap-4">
          <button 
            onClick={handleWake}
            disabled={animating || progress === 1}
            className="px-8 py-2 bg-[#e5d5b5] text-[#0f1115] rounded hover:bg-[#fdfbf7] disabled:opacity-50 transition-colors"
          >
            唤醒汉字
          </button>
          <button 
            onClick={handleReset}
            className="px-8 py-2 bg-transparent border border-[#e5d5b5]/30 text-[#e5d5b5] rounded hover:bg-[#e5d5b5]/10 transition-colors"
          >
            重置星云
          </button>
        </div>
      </div>
    </div>
  );
}
