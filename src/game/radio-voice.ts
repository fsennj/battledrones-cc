import { sfx, type AudioEngine } from "./audio";
import recording from "./radio-en.json";

const cues = recording.cues;
type CueId = keyof typeof cues;
const isCue = (key: string): key is CueId => Object.hasOwn(cues, key);

/** Captions retain names, counts and locations. The recorded radio keeps calls short. */
export function radioCueId(rawKey: string, text: string, spectator = false): CueId | null {
  const key = rawKey.replace(/^banner:/, "");
  if (key === "op-start") {
    const id = `op-start-${text.toLowerCase().trim().replace(/[^a-z0-9]+/g, "-")}`;
    return isCue(id) ? id : null;
  }
  if (key === "op-timer" && /hold/i.test(text)) return "op-timer-hold";
  if (key === "match-rules" && /^daily op/i.test(text)) return "daily-rules";
  if (spectator && (key === "victory" || key === "defeat")) return "hq-destroyed";
  if (isCue(key)) return key;
  if (key.startsWith("opener-")) return "opener";
  if (key.startsWith("kill-")) return "kill-unit";
  if (key.startsWith("out-")) return /^we.re out/i.test(text) ? "out-us" : "out-team";
  if (/^(hq-(attack|fell)|goliath-(attack|build|soon|field|dig)|air|drop|structure-killed)-(blue|red|purple|green)$/.test(key)) {
    const teamCue = key.replace(/-(blue|red|purple|green)$/, "-team");
    return isCue(teamCue) ? teamCue : null;
  }
  if (/^goliath-(airborne|dropped)-(blue|red|purple|green)$/.test(key)) {
    return key.startsWith("goliath-airborne") ? "goliath-airborne" : "goliath-dropped";
  }
  if (/^(enemy-)?goliath-(mortars|laser|cannons)(-|\+|$)/.test(key)) {
    const up = /back online/i.test(text);
    // A single repaired weapon is named in its caption. A plural clip would misstate it.
    if (up && !key.includes("+")) return null;
    return key.startsWith("enemy-")
      ? up ? "enemy-goliath-weapons-up" : "enemy-goliath-weapons-down"
      : up ? "goliath-weapons-up" : "goliath-weapons-down";
  }
  return null;
}

function speechAllowed(): boolean {
  return sfx.enabled("voice") && sfx.settings.speech && !sfx.linkMode;
}

class RadioVoice {
  private bank: AudioBuffer | null = null;
  private loading = false;
  private retryAt = 0;
  private source: AudioBufferSourceNode | null = null;

  /** A mission briefing can wait for the first gesture and decode. Combat warnings use chirps. */
  get waiting(): boolean {
    return speechAllowed() && !this.bank && Date.now() >= this.retryAt;
  }

  warm(engine = sfx.engine): void {
    if (typeof window === "undefined" || !engine || !speechAllowed() || this.bank || this.loading || Date.now() < this.retryAt) return;
    this.loading = true;
    const abort = new AbortController();
    const timeout = window.setTimeout(() => abort.abort(), 8000);
    void fetch(`${import.meta.env.BASE_URL}assets/audio/${recording.file}`, { signal: abort.signal })
      .then((response) => {
        if (!response.ok) throw new Error("radio audio unavailable");
        return response.arrayBuffer();
      })
      .then((bytes) => engine.ctx.decodeAudioData(bytes))
      .then((bank) => { this.bank = bank; })
      .catch(() => { this.retryAt = Date.now() + 15000; })
      .finally(() => {
        window.clearTimeout(timeout);
        this.loading = false;
      });
  }

  /** Schedule one recorded line on the existing voice bus. Returns its seconds or null. */
  play(key: CueId | null, delayS: number, onEnd: () => void): number | null {
    const engine: AudioEngine | null = sfx.engine;
    if (!key || !engine || !speechAllowed() || (typeof document !== "undefined" && document.hidden)) return null;
    if (!this.bank) {
      this.warm(engine);
      return null;
    }
    const [offset, duration] = cues[key] as [number, number];
    if (offset + duration > this.bank.duration + 0.025) return null;
    this.cancel();
    const src = engine.ctx.createBufferSource();
    src.buffer = this.bank;
    src.connect(engine.voiceIn);
    src.onended = () => {
      if (this.source !== src) return;
      this.source = null;
      src.disconnect();
      onEnd();
    };
    this.source = src;
    src.start(engine.ctx.currentTime + delayS, offset, duration);
    return delayS + duration;
  }

  cancel(): void {
    const src = this.source;
    if (!src) return;
    this.source = null;
    src.onended = null;
    src.stop();
    src.disconnect();
  }
}

export const radioVoice = new RadioVoice();
sfx.onReady((engine) => radioVoice.warm(engine));
sfx.onChange(() => {
  if (speechAllowed()) radioVoice.warm();
  else radioVoice.cancel();
});

if (typeof document !== "undefined")
  document.addEventListener("visibilitychange", () => {
    if (document.hidden) radioVoice.cancel();
  });
