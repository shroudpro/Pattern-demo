'use client';

import React, { useState } from 'react';
import { HanziParticleIntro } from './HanziParticleIntro';
import type { CharacterAnalysis } from '@/types/analysis';

export function AnalyzeIntroWrapper({ analysis, character }: { analysis: CharacterAnalysis; character: string }) {
  const [showIntro, setShowIntro] = useState(true);

  if (!showIntro) return null;

  return (
    <HanziParticleIntro 
      analysis={analysis}
      character={character} 
      onComplete={() => setShowIntro(false)} 
    />
  );
}
