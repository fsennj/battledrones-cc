import { describe, expect, it } from "vitest";
import { BUILDINGS, ECONOMY, TICK_RATE } from "../src/sim/balance";
import { step } from "../src/sim/sim";
import { createWorld, spawnBuilding } from "../src/sim/world";

type W = ReturnType<typeof createWorld>;

/** A turret at half health in a bare world, long since hit (no recent damage). */
function hurtTurret(scrap: number) {
  const w = createWorld(24, 24);
  spawnBuilding(w, "hq", "blue", 2, 2);
  spawnBuilding(w, "hq", "red", 18, 18);
  const t = spawnBuilding(w, "turret", "blue", 8, 3);
  t.hp = BUILDINGS.turret.hp / 2;
  t.damagedTick = -1000;
  w.factions.blue.scrap = scrap;
  return { w, t };
}
const seconds = (w: W, n: number) => {
  for (let i = 0; i < n * TICK_RATE; i++) step(w, []);
};
const repair = (id: number) => ({ type: "repair" as const, faction: "blue" as const, buildingId: id });

describe("building repair", () => {
  it("mends a building for scrap, per second, and switches itself off at full health", () => {
    const { w, t } = hurtTurret(1000);
    const control = hurtTurret(1000); // the same world with no repair ordered: its scrap shows what the HQ trickle adds
    step(w, [repair(t.id)]);
    step(control.w, []);
    expect(t.repairing).toBe(true);
    const hp0 = control.t.hp; // (the repairing one already mended its first second)
    seconds(w, 5);
    seconds(control.w, 5);
    expect(t.hp).toBeGreaterThan(hp0);
    expect(control.t.hp).toBe(hp0);
    seconds(w, 60);
    seconds(control.w, 60);
    expect(t.hp).toBe(BUILDINGS.turret.hp);
    expect(t.repairing).toBe(false);
    // half a bar cost about the repair share of the price (rounded up each second)
    const paid = control.w.factions.blue.scrap - w.factions.blue.scrap;
    const exact = BUILDINGS.turret.cost * ECONOMY.repairCost * 0.5;
    expect(paid).toBeGreaterThanOrEqual(exact - 1);
    expect(paid).toBeLessThan(exact + 15);
  });

  it("pauses while the building is under fire and when scrap runs short, then carries on", () => {
    const rich = hurtTurret(5000);
    const poor = hurtTurret(0);
    step(rich.w, [repair(rich.t.id)]);
    step(poor.w, [repair(poor.t.id)]);
    seconds(rich.w, 3);
    seconds(poor.w, 3);
    expect(poor.t.repairing).toBe(true); // short of scrap it stays on…
    expect(poor.t.hp).toBeLessThan(rich.t.hp); // …but mends slower than a funded one
    // a hit freezes it for ECONOMY.repairQuiet seconds
    const hp1 = rich.t.hp;
    rich.t.damagedTick = rich.w.tick;
    seconds(rich.w, 1);
    expect(rich.t.hp).toBe(hp1);
    seconds(rich.w, ECONOMY.repairQuiet + 2);
    expect(rich.t.hp).toBeGreaterThan(hp1);
  });

  it("toggles off, ignores undamaged and enemy buildings, and the HQ can be repaired", () => {
    const { w, t } = hurtTurret(1000);
    step(w, [repair(t.id)]);
    step(w, [repair(t.id)]);
    expect(t.repairing).toBe(false);
    step(w, [{ type: "repair", faction: "red", buildingId: t.id }]); // not theirs
    expect(t.repairing).toBeFalsy();
    const hq = [...w.buildings.values()].find((b) => b.kind === "hq" && b.faction === "blue")!;
    step(w, [repair(hq.id)]); // full health: nothing to repair
    expect(hq.repairing).toBeFalsy();
    hq.hp = BUILDINGS.hq.hp / 2;
    hq.damagedTick = -1000;
    step(w, [repair(hq.id)]);
    expect(hq.repairing).toBe(true);
  });
});
