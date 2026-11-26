import { describe, expect, it } from "vitest";
import { radioCueId } from "../src/game/radio-voice";
import recording from "../src/game/radio-en.json";
import { OPS } from "../src/sim/ops";

describe("recorded radio cues", () => {
  it("gives each operation its own briefing", () => {
    for (const op of OPS) expect(radioCueId("banner:op-start", op.title)).toBe(`op-start-${op.id}`);
  });

  it("chooses clips for variable calls without reading their captions aloud", () => {
    expect(radioCueId("banner:op-timer", "One minute to hold")).toBe("op-timer-hold");
    expect(radioCueId("banner:match-rules", "Daily Op #41")).toBe("daily-rules");
    expect(radioCueId("enemy-goliath-cannons", "Enemy Goliath: cannons down!")).toBe("enemy-goliath-weapons-down");
    expect(radioCueId("goliath-laser-up", "Goliath laser back online")).toBeNull();
    expect(radioCueId("banner:out-blue", "We're out of the fight")).toBe("out-us");
    expect(radioCueId("victory", "Red wins", true)).toBe("hq-destroyed");
    expect(radioCueId("banner:future-cue", "Unknown call")).toBeNull();
  });

  it("keeps recorded clips ordered and disjoint in the audio bank", () => {
    let end = 0;
    for (const entry of Object.values(recording.cues)) {
      const [offset, duration] = entry as [number, number];
      expect(offset).toBeGreaterThanOrEqual(end - 0.00002);
      expect(duration).toBeGreaterThan(0);
      end = offset + duration;
    }
  });
});
