/**
 * VIGNEX Global Search Deep-Linking & Spotlight Utility
 * Provides cross-route navigation, element location polling, smooth scrolling,
 * and temporary 3.5s spotlight highlight.
 */

export interface DeepLinkOptions {
  targetId?: string;
  tabKey?: string;
  durationMs?: number;
}

/**
 * Triggers the VIGNEX Spotlight highlight on a DOM element by ID.
 * Polls for element existence (to accommodate async React rendering) up to maxWaitMs.
 */
export function triggerSpotlight(targetId: string, durationMs: number = 3500, maxWaitMs: number = 3000): Promise<boolean> {
  return new Promise((resolve) => {
    if (!targetId) {
      resolve(false);
      return;
    }

    const startTime = Date.now();
    const cleanId = targetId.startsWith('#') ? targetId.slice(1) : targetId;

    const interval = setInterval(() => {
      const el = document.getElementById(cleanId);
      const elapsed = Date.now() - startTime;

      if (el) {
        clearInterval(interval);

        // Check reduced motion preference
        const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

        // Smooth scroll to center
        el.scrollIntoView({
          behavior: prefersReducedMotion ? 'auto' : 'smooth',
          block: 'center',
          inline: 'nearest',
        });

        // Apply spotlight class
        el.classList.add('vignex-spotlight-active');

        // Clean up after durationMs
        setTimeout(() => {
          el.classList.remove('vignex-spotlight-active');
        }, durationMs);

        resolve(true);
      } else if (elapsed >= maxWaitMs) {
        clearInterval(interval);
        console.warn(`[VIGNEX Search] Target element #${cleanId} not found within ${maxWaitMs}ms`);
        resolve(false);
      }
    }, 40);
  });
}
