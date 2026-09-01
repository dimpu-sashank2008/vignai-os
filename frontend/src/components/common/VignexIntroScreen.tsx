import React, { useState, useEffect, useCallback } from 'react';
import vignanSymbol from '../../assets/vignan-symbol.png';

interface VignexIntroScreenProps {
  onComplete: () => void;
}

export const VignexIntroScreen: React.FC<VignexIntroScreenProps> = ({ onComplete }) => {
  // Phase 1: Symbol (0.0s - 2.2s)
  // Phase 2: Transition / Dissolve Symbol (2.2s - 2.8s)
  // Phase 3: VIGNAI OS Reveal (2.8s - 3.8s)
  // Phase 4: Subtitle Reveal (3.8s - 4.5s)
  // Phase 5: Tagline Reveal (4.5s - 5.5s)
  // Phase 6: Fade into App (5.5s - 6.0s)
  const [phase, setPhase] = useState<'INITIAL' | 'SYMBOL' | 'TRANSITION' | 'BRAND' | 'SUBTITLE' | 'TAGLINE' | 'EXIT'>('INITIAL');
  const [isFadingOut, setIsFadingOut] = useState<boolean>(false);

  const finishIntro = useCallback(() => {
    setIsFadingOut(true);
    setTimeout(() => {
      onComplete();
    }, 400);
  }, [onComplete]);

  useEffect(() => {
    // Check for user's reduced motion preference
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    if (prefersReducedMotion) {
      const reducedTimer = setTimeout(() => {
        finishIntro();
      }, 1200);
      return () => clearTimeout(reducedTimer);
    }

    // Standard high-end cinematic timeline:
    // 0.0s - 0.1s: Mount & black screen
    const t0 = setTimeout(() => setPhase('SYMBOL'), 100);
    // 2.2s: Symbol dissolve transition
    const t1 = setTimeout(() => setPhase('TRANSITION'), 2200);
    // 2.8s: VIGNAI OS appears
    const t2 = setTimeout(() => setPhase('BRAND'), 2800);
    // 3.8s: Subtitle appears
    const t3 = setTimeout(() => setPhase('SUBTITLE'), 3800);
    // 4.5s: Tagline appears
    const t4 = setTimeout(() => setPhase('TAGLINE'), 4500);
    // 5.5s: Initiate fade out to application
    const t5 = setTimeout(() => {
      setPhase('EXIT');
      finishIntro();
    }, 5500);

    // Keyboard listener for Escape key to skip intro
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        finishIntro();
      }
    };
    window.addEventListener('keydown', handleKeyDown);

    return () => {
      clearTimeout(t0);
      clearTimeout(t1);
      clearTimeout(t2);
      clearTimeout(t3);
      clearTimeout(t4);
      clearTimeout(t5);
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [finishIntro]);

  const isSymbolVisible = phase === 'SYMBOL';
  const isBrandVisible = phase === 'BRAND' || phase === 'SUBTITLE' || phase === 'TAGLINE' || phase === 'EXIT';
  const isSubtitleVisible = phase === 'SUBTITLE' || phase === 'TAGLINE' || phase === 'EXIT';
  const isTaglineVisible = phase === 'TAGLINE' || phase === 'EXIT';

  return (
    <div
      className={`fixed inset-0 z-[9999] flex flex-col items-center justify-center bg-[#000000] text-white select-none transition-opacity duration-500 ease-out ${
        isFadingOut ? 'opacity-0 pointer-events-none' : 'opacity-100'
      }`}
      style={{ backgroundColor: '#000000' }}
      role="dialog"
      aria-modal="true"
      aria-label="VIGNAI OS Institutional Launch Sequence"
      tabIndex={-1}
    >
      {/* Skip Button (Accessible & Low-profile) */}
      <button
        type="button"
        onClick={finishIntro}
        className="absolute top-5 right-5 z-20 px-3 py-1.5 text-xs font-mono tracking-wider text-zinc-500 hover:text-zinc-200 bg-zinc-900/40 hover:bg-zinc-800/60 border border-zinc-800/60 rounded-full transition-colors duration-200 focus:outline-none focus:ring-1 focus:ring-zinc-600 cursor-pointer"
        aria-label="Skip intro sequence"
      >
        Skip <span className="opacity-40 ml-1 text-[10px]">ESC</span>
      </button>

      {/* Subtle radial ambient atmosphere behind center */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none overflow-hidden">
        <div
          className={`h-[450px] w-[450px] rounded-full transition-all duration-1000 ease-out pointer-events-none ${
            phase === 'SYMBOL'
              ? 'bg-blue-900/15 scale-100 blur-3xl opacity-70'
              : phase === 'TRANSITION'
              ? 'bg-indigo-900/10 scale-110 blur-3xl opacity-30'
              : isBrandVisible
              ? 'bg-indigo-600/15 scale-125 blur-3xl opacity-80'
              : 'scale-75 opacity-0'
          }`}
        />
      </div>

      {/* ================================================================= */}
      {/* STAGE 1: OFFICIAL VIGNAN INSTITUTIONAL SYMBOL                     */}
      {/* ================================================================= */}
      <div
        className={`absolute inset-0 flex items-center justify-center pointer-events-none transition-all duration-700 ease-out ${
          isSymbolVisible
            ? 'opacity-100 scale-100 filter-none'
            : phase === 'TRANSITION'
            ? 'opacity-0 scale-105 blur-sm'
            : 'opacity-0 scale-95 pointer-events-none'
        }`}
        aria-hidden={!isSymbolVisible}
      >
        <div className="relative flex items-center justify-center">
          {/* Gentle soft glow halo matching symbol core */}
          <div
            className={`absolute w-36 h-36 sm:w-48 sm:h-48 md:w-56 md:h-56 rounded-full bg-blue-600/20 blur-xl transition-opacity duration-1000 ${
              isSymbolVisible ? 'opacity-80' : 'opacity-0'
            }`}
          />

          {/* Official Vignan Symbol with exact proportions */}
          <img
            src={vignanSymbol}
            alt="Official Vignan Institutional Symbol"
            className="relative z-10 w-32 h-32 sm:w-44 sm:h-44 md:w-52 md:h-52 aspect-square object-contain drop-shadow-[0_0_25px_rgba(0,120,240,0.25)] select-none"
            draggable={false}
          />
        </div>
      </div>

      {/* ================================================================= */}
      {/* STAGE 2: VIGNAI OS REVEAL                                         */}
      {/* ================================================================= */}
      <div
        className={`relative z-10 flex flex-col items-center justify-center text-center px-4 max-w-3xl transition-all duration-700 ease-out ${
          isBrandVisible ? 'opacity-100 scale-100' : 'opacity-0 scale-95 pointer-events-none'
        }`}
        aria-hidden={!isBrandVisible}
      >
        {/* Dominant Product Identity: VIGNAI OS */}
        <div className="relative">
          <div className="absolute -inset-4 bg-indigo-500/10 blur-2xl rounded-full pointer-events-none" />
          <h1
            className={`relative text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-black tracking-tight text-white transition-all duration-700 ease-out ${
              isBrandVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-3'
            }`}
          >
            VIGNAI OS
          </h1>
        </div>

        {/* Subtitle: Vignan's AI Campus Operating System */}
        <div className="mt-3 sm:mt-4">
          <p
            className={`text-xs sm:text-sm md:text-base font-semibold tracking-[0.22em] sm:tracking-[0.28em] text-indigo-400 uppercase transition-all duration-600 ease-out ${
              isSubtitleVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-2'
            }`}
          >
            Vignan's AI Campus Operating System
          </p>
        </div>

        {/* Core Tagline: UNDERSTAND. CONNECT. PREDICT. ACT. */}
        <div className="mt-4 sm:mt-6">
          <p
            className={`text-[10px] sm:text-xs md:text-sm font-medium tracking-[0.28em] sm:tracking-[0.35em] text-zinc-400 uppercase transition-all duration-600 ease-out ${
              isTaglineVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-2'
            }`}
          >
            UNDERSTAND • CONNECT • PREDICT • ACT
          </p>
        </div>
      </div>
    </div>
  );
};
