/**
 * The radio announcer: a commander's voice for the moments that matter
 * ("Warning: our HQ is under attack", "Enemy aircraft detected", "Double
 * kill"). It reads out every announce() banner and the radio-only lines that
 * BattleCallouts (callouts.ts) detects in the fx stream, one at a time
 * through RadioQueue: most important first, ≥ 2.5 s apart, stale lines
 * dropped.
 *
 * Delivery: a short squelch and a recorded English line on the voice bus,
 * followed by an over click. Chirps mode and unavailable clips use the
 * two-tone code. The HUD keeps the full names and details in its captions.
 */
import type { Faction, FxEvent, World } from "../sim/types";
import { onAnnounce, announce, type Announcement, type AnnounceTone } from "./announce";
import { sfx } from "./audio";
import { radioCueId, radioVoice } from "./radio-voice";
import { BattleCallouts, RadioQueue, isEndLine, speakable, type RadioCueKey, type RadioLine } from "./callouts";

/** Speech voice settings. */
export const SPEECH = {
  rate: 1.08,
  /** Gap between the squelch and the first word, ms. */
  leadMs: 130,
  /** Music duck while a line plays, dB. */
  duckDb: 5
} as const;

/** Rough spoken length of a line, seconds (for the music duck and the busy timeout). */
export function lineSeconds(text: string, rate: number = SPEECH.rate): number {
  const words = text.split(/\s+/).filter(Boolean).length;
  return 0.35 + (words * 0.34) / rate;
}

// ----------------------------------------------------------- radio sounds --

/** Radio squelch: a band-passed noise burst and a 1.2 kHz key-up beep. */
function squelch(open: boolean): void {
  const e = sfx.engine;
  if (!e) return;
  const { ctx, voiceIn, noise } = e;
  const t = ctx.currentTime + 0.01;
  const out = ctx.createGain();
  out.gain.value = 0.5;
  out.connect(voiceIn);
  const src = ctx.createBufferSource();
  src.buffer = noise;
  const bp = ctx.createBiquadFilter();
  bp.type = "bandpass";
  bp.frequency.value = open ? 1700 : 2300;
  bp.Q.value = 1.1;
  const g = ctx.createGain();
  const dur = open ? 0.08 : 0.05;
  g.gain.setValueAtTime(0, t);
  g.gain.linearRampToValueAtTime(0.28, t + 0.004);
  g.gain.exponentialRampToValueAtTime(0.002, t + dur);
  src.connect(bp).connect(g).connect(out);
  src.start(t, Math.random() * 1.5, dur + 0.02);
  if (open) {
    const o = ctx.createOscillator();
    o.type = "sine";
    o.frequency.value = 1200;
    const og = ctx.createGain();
    og.gain.setValueAtTime(0, t + 0.03);
    og.gain.linearRampToValueAtTime(0.1, t + 0.035);
    og.gain.setValueAtTime(0.1, t + 0.075);
    og.gain.linearRampToValueAtTime(0, t + 0.085);
    o.connect(og).connect(out);
    o.start(t + 0.03);
    o.stop(t + 0.1);
  }
  setTimeout(() => out.disconnect(), 400);
}

/** The two-tone code that stands in for words: falling for warnings, rising for good news. */
export const CODES: Record<AnnounceTone, number[]> = {
  bad: [988, 740, 988, 740],
  good: [740, 988],
  epic: [659, 880, 1319],
  info: [880, 880]
};

function code(tone: AnnounceTone, priority: number): number {
  const e = sfx.engine;
  if (!e) return 0;
  const { ctx, voiceIn } = e;
  // only the urgent warnings get the long four-note pattern
  const notes = tone === "bad" && priority > 1 ? CODES.bad.slice(0, 2) : CODES[tone];
  const t0 = ctx.currentTime + SPEECH.leadMs / 1000;
  const step = 0.11;
  const out = ctx.createGain();
  out.gain.value = 0.5;
  out.connect(voiceIn);
  notes.forEach((f, i) => {
    const t = t0 + i * step;
    const o = ctx.createOscillator();
    o.type = "square";
    o.frequency.value = f;
    const lp = ctx.createBiquadFilter();
    lp.type = "lowpass";
    lp.frequency.value = 2400;
    const g = ctx.createGain();
    g.gain.setValueAtTime(0, t);
    g.gain.linearRampToValueAtTime(0.09, t + 0.005);
    g.gain.setValueAtTime(0.09, t + step * 0.7);
    g.gain.linearRampToValueAtTime(0, t + step * 0.85);
    o.connect(lp).connect(g).connect(out);
    o.start(t);
    o.stop(t + step);
  });
  const len = SPEECH.leadMs / 1000 + notes.length * step;
  setTimeout(() => out.disconnect(), (len + 0.3) * 1000);
  return len;
}

/**
 * A quick sample after the Voice setting changes (pause menu): "Radio check"
 * in words or the radio code in Chirps mode.
 */
export function radioCheck(): void {
  if (!sfx.enabled("voice")) return;
  squelch(true);
  const seconds = radioVoice.play("radio-check", SPEECH.leadMs / 1000, () => squelch(false));
  if (seconds === null) code("info", 2);
}

// ------------------------------------------------------------ announcer --

export interface AnnouncerHooks {
  world: World;
  player: Faction;
  spectator: boolean;
  /** Is the tile point inside the camera view? */
  onScreen(x: number, y: number): boolean;
  /** Show a radio caption (for lines no toast or banner already shows). */
  caption(line: RadioLine): void;
}

/** One delivered line, for debugging and the per-minute measurements. */
export interface RadioLogEntry {
  t: number;
  key: string;
  text: string;
  how: "speech" | "code" | "silent";
}

let active: Announcer | null = null;

/** Outside cues for the announcer (the HUD's "not enough scrap", a refused placement). */
export function radioCue(key: RadioCueKey): void {
  active?.cue(key);
}

/** The voice of the match: one per GameScene. */
export class Announcer {
  readonly callouts: BattleCallouts;
  private queue = new RadioQueue();
  /** Render seconds (stops while paused). */
  private clock = 0;
  private simT = 0;
  private busyUntil = 0;
  private briefingUntil = 0;
  private interruptBriefing = false;
  private ended = false;
  private pendingBriefing: RadioLine | null = null;
  private offAnnounce: () => void;
  readonly log: RadioLogEntry[] = [];

  constructor(private h: AnnouncerHooks) {
    this.callouts = new BattleCallouts({
      world: h.world, player: h.player, spectator: h.spectator, onScreen: h.onScreen,
      radio: (l) => this.push(l),
      announce
    });
    // every banner is read out too (its text is on screen, so no caption)
    this.offAnnounce = onAnnounce((a) => this.announced(a));
    active = this;
  }

  /** This tick's sim events at sim time `t`. */
  events(fx: readonly FxEvent[], t: number): void {
    this.simT = t;
    this.callouts.events(fx, t);
  }

  cue(key: RadioCueKey): void {
    this.callouts.cue(key, this.simT);
  }

  /** Banners: read out what the HUD shows. */
  private announced(a: Announcement): void {
    if (this.ended && a.priority !== 0) return;
    const text = a.say ?? speakable(a.text);
    if (!text) return;
    const line = { key: `banner:${a.key}`, text, priority: a.priority ?? 2, tone: a.tone ?? "info", caption: false };
    if (a.key === "op-start" && radioVoice.waiting) this.pendingBriefing = line;
    else this.push(line);
  }

  push(line: RadioLine): void {
    if (this.ended) return;
    if (line.priority <= 1 && this.clock < this.briefingUntil) {
      radioVoice.cancel();
      this.briefingUntil = this.busyUntil = 0;
      this.interruptBriefing = true;
    }
    if (isEndLine(line)) {
      // the last word: nothing else waits or talks over it
      this.ended = true;
      this.pendingBriefing = null;
      this.queue.clear();
      radioVoice.cancel();
      this.busyUntil = 0;
      this.queue.push(line, this.clock);
      return;
    }
    this.queue.push(line, this.clock);
  }

  /** Call every frame with the real frame delta (ms). */
  update(deltaMs: number, paused: boolean): void {
    if (paused) return; // lines wait (and don't age) while the game is paused
    this.clock += deltaMs / 1000;
    if (this.pendingBriefing && !radioVoice.waiting) {
      this.push(this.pendingBriefing);
      this.pendingBriefing = null;
    }
    const busy = this.clock < this.busyUntil;
    // the final line goes out at once; everything else respects the gap
    const line = this.queue.next(this.clock, busy, this.ended || this.interruptBriefing);
    if (line) {
      this.interruptBriefing = false;
      this.deliver(line);
    }
  }

  private deliver(line: RadioLine): void {
    if (line.caption) this.h.caption(line);
    const voiceOn = sfx.enabled("voice") && !!sfx.engine;
    let how: RadioLogEntry["how"] = "silent";
    if (voiceOn) {
      squelch(true);
      const clip = radioCueId(line.key, line.text, this.h.spectator);
      const seconds = radioVoice.play(clip, SPEECH.leadMs / 1000, () => {
        if (sfx.enabled("voice")) squelch(false);
      });
      how = seconds === null ? "code" : "speech";
      const length = seconds ?? code(line.tone, line.priority);
      this.busyUntil = this.clock + length + 0.2;
      if (seconds !== null && line.key === "banner:op-start") this.briefingUntil = this.busyUntil;
      sfx.duck(SPEECH.duckDb, length);
    }
    this.log.push({ t: Math.round(this.simT * 10) / 10, key: line.key, text: line.text, how });
    if (this.log.length > 400) this.log.splice(0, 100);
  }

  destroy(): void {
    this.offAnnounce();
    radioVoice.cancel();
    this.queue.clear();
    if (active === this) active = null;
  }
}
