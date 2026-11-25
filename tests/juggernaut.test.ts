import { describe, expect, it } from "vitest";
import { TICK_RATE, UNITS } from "../src/sim/balance";
import { step } from "../src/sim/sim";
import type { World } from "../src/sim/types";
import { createWorld, spawnBuilding, spawnUnit } from "../src/sim/world";

const run = (w: World, seconds: number) => {
  for (let i = 0; i < seconds * TICK_RATE; i++) step(w, []);
};
const shots = (w: World, seconds: number) => {
  let n = 0;
  for (let i = 0; i < seconds * TICK_RATE; i++) {
    step(w, []);
    n += w.fx.filter((f) => f.type === "shot").length;
  }
  return n;
};

describe("Juggernaut", () => {
  it("is built at the Fab Plant, behind the Tech Lab", () => {
    const w = createWorld(32, 24);
    spawnBuilding(w, "hq", "blue", 2, 2);
    spawnBuilding(w, "hq", "red", 28, 20);
    const fab = spawnBuilding(w, "fab-plant", "blue", 8, 2);
    w.factions.blue.scrap = 5000;
    step(w, [{ type: "produce", faction: "blue", buildingId: fab.id, unit: "juggernaut" }]);
    expect(fab.queue).toHaveLength(0); // no Tech Lab yet
    spawnBuilding(w, "tech-lab", "blue", 12, 2);
    step(w, [{ type: "produce", faction: "blue", buildingId: fab.id, unit: "juggernaut" }]);
    expect(fab.queue).toHaveLength(1);
    run(w, UNITS.juggernaut.buildTime + 5);
    expect([...w.units.values()].some((u) => u.faction === "blue" && u.kind === "juggernaut")).toBe(true);
  });

  it("out-ranges the Mortar: it hits a target 12 tiles away that a Mortar cannot reach", () => {
    const reach = (kind: "mortar" | "juggernaut") => {
      const w = createWorld(40, 24);
      spawnUnit(w, kind, "blue", 4.5, 10.5);
      const victim = spawnUnit(w, "harvester", "red", 16.5, 10.5);
      run(w, 12);
      return { hp: victim.hp, w };
    };
    expect(reach("mortar").hp).toBe(UNITS.harvester.hp);
    expect(reach("juggernaut").hp).toBeLessThan(UNITS.harvester.hp);
  });

  it("cannot fire inside its minimum range", () => {
    const w = createWorld(24, 24);
    spawnUnit(w, "juggernaut", "blue", 10.5, 10.5);
    const v = spawnUnit(w, "harvester", "red", 12.5, 10.5); // 2 tiles: inside minRange 4
    expect(shots(w, 8)).toBe(0);
    expect(v.hp).toBe(UNITS.harvester.hp);
  });

  it("is a ground-only gun: it ignores aircraft", () => {
    const w = createWorld(40, 24);
    spawnUnit(w, "juggernaut", "blue", 4.5, 10.5);
    const wasp = spawnUnit(w, "wasp", "red", 12.5, 10.5);
    expect(shots(w, 8)).toBe(0);
    expect(wasp.hp).toBe(UNITS.wasp.hp);
  });
});
