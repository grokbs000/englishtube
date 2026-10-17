/**
 * Karaoke Clock & Continuous Synchronization Engine (60 FPS)
 * High-precision audio-visual interpolation, smart countdowns, and zero-allocation DOM updates.
 */

export interface SubtitleCue {
  start: number;
  duration: number;
  en: string;
  zh: string;
  text?: string;
}

export class KaraokeClockEngine {
  private lastKnownYtTime: number = 0;
  private lastSyncPerfTime: number = 0;
  private perceptualOffsetMs: number = 80; // 80ms auditory-visual lead compensation
  private activeCueIndex: number = -1;
  private isPaused: boolean = true;

  /**
   * Samples YouTube Iframe current time and interpolates continuous 60fps clock.
   * Eliminates 250ms discrete polling jitter using performance.now().
   */
  public getExactPlaybackTime(rawYtCurrentTime: number, isPlaying: boolean): number {
    const now = performance.now();
    this.isPaused = !isPlaying;

    if (this.isPaused) {
      this.lastKnownYtTime = rawYtCurrentTime;
      this.lastSyncPerfTime = now;
      return rawYtCurrentTime;
    }

    // Only update sync anchor when YouTube player emits a genuine new second/millisecond value
    if (Math.abs(rawYtCurrentTime - this.lastKnownYtTime) > 0.001) {
      this.lastKnownYtTime = rawYtCurrentTime;
      this.lastSyncPerfTime = now;
    }

    // High precision interpolation
    const elapsedSeconds = (now - this.lastSyncPerfTime) / 1000;
    // Bound interpolation delta to max 0.4s to prevent runaway drifts on tab backgrounding
    const interpolated = this.lastKnownYtTime + Math.min(elapsedSeconds, 0.4);
    
    // Perceptual lead compensation
    return Math.max(0, interpolated + this.perceptualOffsetMs / 1000);
  }

  /**
   * Determines active subtitle cue, smart intro countdown, or interlude countdown.
   */
  public evaluateStageState(
    currentTime: number,
    cues: SubtitleCue[]
  ): {
    cue: SubtitleCue | null;
    cueIndex: number;
    countdownText: string | null;
    isIntro: boolean;
    isInterlude: boolean;
  } {
    if (!cues || cues.length === 0) {
      return { cue: null, cueIndex: -1, countdownText: null, isIntro: false, isInterlude: false };
    }

    const firstStart = cues[0].start;

    // 1. Smart Intro Countdown
    if (currentTime < firstStart - 0.5) {
      const remainingSeconds = Math.max(1, Math.ceil(firstStart - currentTime));
      return {
        cue: null,
        cueIndex: -1,
        countdownText: `🎵 (前奏演奏中 · 倒數 ${remainingSeconds} 秒)`,
        isIntro: true,
        isInterlude: false
      };
    }

    // 2. Active Cue Match
    let matchedIndex = -1;
    for (let i = 0; i < cues.length; i++) {
      const c = cues[i];
      if (currentTime >= c.start && currentTime < c.start + c.duration) {
        matchedIndex = i;
        break;
      }
    }

    if (matchedIndex !== -1) {
      this.activeCueIndex = matchedIndex;
      return {
        cue: cues[matchedIndex],
        cueIndex: matchedIndex,
        countdownText: null,
        isIntro: false,
        isInterlude: false
      };
    }

    // 3. Smart Interlude Countdown between cues
    for (let i = 0; i < cues.length - 1; i++) {
      const currentEnd = cues[i].start + cues[i].duration;
      const nextStart = cues[i + 1].start;
      const gap = nextStart - currentEnd;

      if (gap > 4.5 && currentTime >= currentEnd && currentTime < nextStart - 0.8) {
        const remainingSeconds = Math.max(1, Math.ceil(nextStart - currentTime));
        return {
          cue: null,
          cueIndex: -1,
          countdownText: `🎵 (間奏音樂演奏中 · 倒數 ${remainingSeconds} 秒)`,
          isIntro: false,
          isInterlude: true
        };
      }
    }

    // Default to last active cue or standby
    const fallbackCue = this.activeCueIndex >= 0 ? cues[this.activeCueIndex] : null;
    return {
      cue: fallbackCue,
      cueIndex: this.activeCueIndex,
      countdownText: null,
      isIntro: false,
      isInterlude: false
    };
  }

  /**
   * Zero-Allocation Word Level Highlight Class Differ
   */
  public updateWordHighlight(
    container: HTMLElement,
    wordSpans: HTMLSpanElement[],
    activeWordIndex: number
  ): void {
    for (let i = 0; i < wordSpans.length; i++) {
      const span = wordSpans[i];
      const hasActive = span.classList.contains('karaoke-word-active');
      const shouldBeActive = i === activeWordIndex;
      const shouldBePassed = i < activeWordIndex;

      if (shouldBeActive && !hasActive) {
        span.classList.add('karaoke-word-active');
      } else if (!shouldBeActive && hasActive) {
        span.classList.remove('karaoke-word-active');
      }

      const hasPassed = span.classList.contains('karaoke-word-passed');
      if (shouldBePassed && !hasPassed) {
        span.classList.add('karaoke-word-passed');
      } else if (!shouldBePassed && hasPassed) {
        span.classList.remove('karaoke-word-passed');
      }
    }
  }
}
