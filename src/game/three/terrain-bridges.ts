import * as THREE from "three";
import { Terrain, type World } from "../../sim/types";
import { ModelBuilder, type Vec3 } from "./builder";
import { hash } from "./terrain-props";

/**
 * Bridges. Each connected run of bridge tiles becomes one bridge laid along
 * its crossing's own axis, like the painted art's: a main deck of planks (or
 * steel plates) down the middle, reaching bank to bank, with the rest
 * of the run's tiles decked a step lower round it as side bays — so every
 * bridge tile is decked and nothing past them is (hovercraft skim the water
 * right beside it). Kerbs and rails follow the run's outline where it meets
 * the water; piles and piers drop into the river, abutments meet the banks.
 * A run slanted off the grid (a diagonal crossing) is only a staircase of
 * tiles, so it's laid as the one straight deck those tiles approximate,
 * railed down both sides, rather than decked tile by tile.
 */

/** A bridge's main deck: a rectangle in its crossing's frame. */
export interface DeckSpan {
  cx: number;
  cz: number;
  /** Unit vector along the crossing. */
  ux: number;
  uz: number;
  /** Half its length along the crossing, half its width across. */
  hl: number;
  hw: number;
}

/** The main deck's walking surface (vehicles ride at 0.02); the side bays sit a step lower. */
const TOP = 0.035;
const BAY = 0.022;
/** Sampling step (tiles) when fitting the main deck to the run. */
const S = 0.05;
const N4 = [[1, 0], [-1, 0], [0, 1], [0, -1]] as const;

const _c = new THREE.Color();

/** A connected run of bridge tiles, read as one crossing (see bridgeRuns). */
export interface BridgeRun {
  /** Its tiles (row-major indices). */
  tiles: number[];
  /** Its centroid. */
  mx: number;
  mz: number;
  /** The crossing's angle and unit vector along it. */
  ang: number;
  ux: number;
  uz: number;
  /**
   * Slanted off the grid (its diagonal, say): its tiles only approximate a straight deck in
   * stair-steps, so it's laid as that one straight deck, not tile by tile. The deck: centred
   * `mid` along the axis from the centroid, `hl` long and `hw` wide (halves).
   */
  slant: boolean;
  mid: number;
  hl: number;
  hw: number;
}

/** Open, dry bank a deck may reach onto: never water (hovercraft ride there), rock, trees or salvage. */
const dryBank = (t: number) => t === Terrain.Ground || t === Terrain.Road || t === Terrain.Rough;

/**
 * Every connected run of bridge tiles in a row-major W×H grid, with its crossing's axis: from bank
 * to bank (not the run's own shape: a short run over a narrow river can be wider than it is long),
 * to the nearest 45°. A slanted (diagonal) run's deck is as wide
 * as √(12·var + 1) of its tiles' offsets across the axis — exact for a clean band of tiles at any
 * angle, since a unit square's spread across any line has variance 1/12 — and reaches along the
 * axis wherever its cross-section is mostly bridge or bank. The 3D bridges and the painted ground
 * (terrain-paint.ts) both lay out their decks from this.
 */
export function bridgeRuns(g: ArrayLike<number>, W: number, H: number): { runOf: Int32Array; runs: BridgeRun[] } {
  const T = (tx: number, ty: number) => (tx >= 0 && ty >= 0 && tx < W && ty < H ? g[ty * W + tx]! : -1);
  const runOf = new Int32Array(W * H).fill(-1);
  const runs: BridgeRun[] = [];
  for (let start = 0; start < W * H; start++) {
    if (runOf[start]! >= 0 || g[start] !== Terrain.Bridge) continue;
    const id = runs.length;
    // flood the connected run
    const tiles: number[] = [];
    const stack = [start];
    runOf[start] = id;
    while (stack.length) {
      const i = stack.pop()!;
      tiles.push(i);
      const tx = i % W;
      const ty = (i - tx) / W;
      for (const [dx, dy] of N4) {
        const n = (ty + dy) * W + tx + dx;
        if (T(tx + dx, ty + dy) !== Terrain.Bridge || runOf[n]! >= 0) continue;
        runOf[n] = id;
        stack.push(n);
      }
    }
    let mx = 0;
    let mz = 0;
    for (const i of tiles) {
      mx += (i % W) + 0.5;
      mz += Math.floor(i / W) + 0.5;
    }
    mx /= tiles.length;
    mz /= tiles.length;
    // the bridge runs between its banks, with the river either side: the axis along which the land
    // touching the run spreads most, net of how the water touching it spreads
    const bank = [0, 0, 0, 0];
    const wet = [0, 0, 0, 0];
    const seen = new Set<number>();
    for (const i of tiles)
      for (let dy = -1; dy <= 1; dy++)
        for (let dx = -1; dx <= 1; dx++) {
          const nx = (i % W) + dx;
          const ny = Math.floor(i / W) + dy;
          const t = T(nx, ny);
          if (t < 0 || t === Terrain.Bridge || t === Terrain.Rock || t === Terrain.Shallows || seen.has(ny * W + nx)) continue;
          seen.add(ny * W + nx);
          const m = t === Terrain.Water || t === Terrain.Deep ? wet : bank;
          const ddx = nx + 0.5 - mx;
          const ddz = ny + 0.5 - mz;
          m[0]! += ddx * ddx;
          m[1]! += ddz * ddz;
          m[2]! += ddx * ddz;
          m[3]!++;
        }
    const cov = (k: number) => bank[k]! / Math.max(1, bank[3]!) - wet[k]! / Math.max(1, wet[3]!);
    // ...squared to the grid or its diagonal, the only ways tiles lay a clean straight band (a short
    // run over a narrow river is too square to say more precisely, and the maps lay no other)
    const fit = bank[3]! > 1 ? 0.5 * Math.atan2(2 * cov(2), cov(0) - cov(1)) : 0;
    const ang = Math.round(fit / (Math.PI / 4)) * (Math.PI / 4);
    const ux = Math.cos(ang);
    const uz = Math.sin(ang);
    const run: BridgeRun = { tiles, mx, mz, ang, ux, uz, slant: Math.abs(Math.sin(2 * ang)) > 0.5, mid: 0, hl: 0, hw: 0 };
    runs.push(run);
    if (!run.slant) continue;
    let vv = 0;
    let a0 = Infinity;
    let a1 = -Infinity;
    for (const i of tiles) {
      const dx = (i % W) + 0.5 - mx;
      const dz = Math.floor(i / W) + 0.5 - mz;
      const v = -dx * uz + dz * ux;
      vv += v * v;
      a0 = Math.min(a0, dx * ux + dz * uz);
      a1 = Math.max(a1, dx * ux + dz * uz);
    }
    const hw = Math.sqrt((12 * vv) / tiles.length + 1) / 2;
    // the slices across the deck that are mostly this run, dry bank or the shallows by it, with some
    // run in them; the deck is the longest unbroken stretch of them
    const NV = 9;
    let best0 = 0;
    let best1 = -1;
    let from = NaN;
    let last = NaN;
    for (let u = a0 - 1; u <= a1 + 1 + S / 2; u += S) {
      let mine = 0;
      let dry = 0;
      for (let j = 0; j < NV; j++) {
        const v = -hw + ((j + 0.5) * 2 * hw) / NV;
        const tx = Math.floor(mx + u * ux - v * uz);
        const ty = Math.floor(mz + u * uz + v * ux);
        if (T(tx, ty) === Terrain.Bridge && runOf[ty * W + tx] === id) mine++;
        else if (dryBank(T(tx, ty)) || T(tx, ty) === Terrain.Shallows) dry++;
      }
      const ok = mine > 0 && mine + dry >= NV * 0.5 && u <= a1 + 1;
      if (ok && from !== from) from = u;
      if (ok) last = u;
      if ((!ok || u + S > a1 + 1 + S / 2) && from === from) {
        if (last - from > best1 - best0) [best0, best1] = [from, last];
        from = NaN;
      }
    }
    if (best1 - best0 < 1) {
      run.slant = false;
      continue;
    }
    run.mid = (best0 + best1) / 2;
    run.hl = (best1 - best0) / 2 + S / 2;
    run.hw = hw;
  }
  return { runOf, runs };
}

/** Every bridge on the map, one merged model geometry (null if none), and their main decks. */
export function bridgeGeometry(w: World, colour: number, steel: boolean): { geo: THREE.BufferGeometry | null; spans: DeckSpan[] } {
  const W = w.width;
  const H = w.height;
  const T = (tx: number, ty: number) => (tx >= 0 && ty >= 0 && tx < W && ty < H ? w.terrain[ty * W + tx]! : -1);
  const dry = dryBank;
  const { runOf, runs } = bridgeRuns(w.terrain, W, H);
  const b = new ModelBuilder({ grade: 0.14 });
  const spans: DeckSpan[] = [];
  const base = new THREE.Color(colour);
  const tone = (k: number) => _c.copy(base).multiplyScalar(k).getHex();
  for (let run = 0; run < runs.length; run++) {
    const { tiles, mx, mz, ang, ux, uz } = runs[run]!;
    if (runs[run]!.slant) {
      slantedBridge(b, runs[run]!, spans, tone, steel);
      continue;
    }
    const mine = (tx: number, ty: number) => T(tx, ty) === Terrain.Bridge && runOf[ty * W + tx] === run;
    // the run's extent along and across the axis, over every tile corner
    let a0 = Infinity;
    let a1 = -Infinity;
    let across = 0;
    for (const i of tiles) {
      const tx = i % W;
      const ty = Math.floor(i / W);
      for (const [cx, cz] of [[tx, ty], [tx + 1, ty], [tx, ty + 1], [tx + 1, ty + 1]] as const) {
        const along = (cx - mx) * ux + (cz - mz) * uz;
        a0 = Math.min(a0, along);
        a1 = Math.max(a1, along);
        across = Math.max(across, Math.abs(-(cx - mx) * uz + (cz - mz) * ux));
      }
    }
    // what lies under a point (along, across) of the crossing's frame: 2 this run, 1 dry bank, 0 neither
    const under = (u: number, v: number) => {
      const tx = Math.floor(mx + u * ux - v * uz);
      const ty = Math.floor(mz + u * uz + v * ux);
      return mine(tx, ty) ? 2 : dry(T(tx, ty)) ? 1 : 0;
    };
    // the main deck: the widest band down the axis that covers only the run and dry bank,
    // reaching from end to end if it can (a little shy of the ends if that buys real width)
    const nu = Math.round((a1 - a0) / S);
    const reach = new Float32Array(nu + 1);
    let best = { score: -Infinity, c: 0, h: 0, t: 0 };
    for (let ci = -4; ci <= 4; ci++) {
      const c = ci * 0.1;
      for (let k = 0; k <= nu; k++) {
        const u = a0 + k * S;
        let r = under(u, c) ? 0 : -1;
        while (r >= 0 && r < 1.6 && under(u, c + r + S) && under(u, c - r - S)) r += S;
        reach[k] = r;
      }
      for (let ti = 0; ti <= 8; ti++) {
        const k0 = ti * 2;
        let h = Infinity;
        for (let k = k0; k <= nu - k0; k++) h = Math.min(h, reach[k]!);
        const score = h - ti * 0.05 - Math.abs(c) * 0.1;
        if (score > best.score) best = { score, c, h, t: k0 * S };
      }
    }
    const hw = best.h - 0.03;
    const main = hw >= 0.4;
    const b0 = a0 + best.t;
    const b1 = a1 - best.t;
    const hl = main ? (b1 - b0) / 2 : 0;
    const mid = (b0 + b1) / 2;
    const cx = mx + ux * mid - uz * best.c;
    const cz = mz + uz * mid + ux * best.c;
    if (main) spans.push({ cx, cz, ux, uz, hl, hw });
    // a point in the main deck's frame, in the world
    const P = (u: number, y: number, v: number): Vec3 => [cx + u * ux - v * uz, y, cz + u * uz + v * ux];
    const yaw: { rot: Vec3 } = { rot: [0, -ang, 0] };
    // 2 main deck, 1 side bay (the run's own tiles round it), 0 neither
    const kind = (u: number, v: number) => (main && Math.abs(u) <= hl && Math.abs(v) <= hw ? 2 : under(u + mid, v + best.c) === 2 ? 1 : 0);

    // the run's tiles: a timber (or steel) bed a step under the main deck
    for (const i of tiles) b.box(1, 0.16, 1, [(i % W) + 0.5, -0.08, Math.floor(i / W) + 0.5], tone(0.52));
    if (main) {
      // the main deck's own slab, a hair above the bed so the two never fight
      b.box(hl * 2, 0.13, hw * 2, P(0, 0.012 - 0.065, 0), tone(0.55), yaw);
      // its edges: a dark timber stringer, or hazard paint on steel
      for (const s of [-1, 1]) {
        if (steel)
          for (let k = 0; k < Math.floor(hl * 4); k++)
            b.box(0.13, 0.006, 0.07, P(-hl + 0.125 + k * 0.25, TOP + 0.003, s * (hw - 0.05)), k % 2 ? 0x2b2d30 : 0xc89a2a, yaw);
        else b.box(hl * 2, 0.012, 0.07, P(0, TOP + 0.002, s * (hw - 0.035)), tone(0.56), yaw);
      }
      // abutments where it meets each bank (their tops under the deck, so nothing is coplanar)
      for (const s of [-1, 1]) bridgeSeat(b, P, yaw, s * hl, hw, steel);
      // piers into the river, a cap beam across under each
      const piers = Math.max(1, Math.round((hl * 2) / 1.8));
      for (let k = 0; k < piers; k++) {
        const u = -hl + (k + 0.5) * ((hl * 2) / piers);
        bridgePier(b, P, yaw, u, hw, steel);
      }
    }
    // planks (or plates) across the crossing, over the main deck and the side bays alike; each is
    // laid only where it's decked right across, so none overhangs the water
    const len = main ? hl * 2 : a1 - a0;
    const nP = Math.max(4, Math.round(len / (steel ? 0.45 : 0.21)));
    const pitch = len / nP;
    const pw = pitch - (steel ? 0.04 : 0.035);
    const from = Math.floor((a0 - mid + (main ? hl : len / 2)) / pitch) - 1;
    const to = Math.ceil((a1 - mid + (main ? hl : len / 2)) / pitch) + 1;
    for (let k = from; k <= to; k++) {
      const u = -(main ? hl : len / 2) + (k + 0.5) * pitch;
      let runStart = 0;
      let runKind = 0;
      const nv = Math.ceil((across + 0.6) / S) * 2;
      for (let j = 0, v = -(nv / 2) * S; j <= nv; j++, v += S) {
        let kd = j === nv ? 0 : 2;
        for (let q = -2; q <= 2 && kd; q++) kd = Math.min(kd, kind(u + q * (pw / 4 + 0.01), v));
        if (kd === runKind) continue;
        // (from its first decked sample to its last, so a square-cut end never pokes past a corner)
        const end = v - S;
        if (runKind && end - runStart > 0.06) {
          const top = runKind === 2 ? TOP : BAY;
          const bot = runKind === 2 ? 0.012 : 0.002;
          deckPanel(b, P, yaw, tone, steel, k, u, pw, runStart, end, bot, top, runKind === 2);
        }
        runStart = v;
        runKind = kd;
      }
    }
    // kerbs and rails along the run's outline wherever it meets the water (not where it joins the bank)
    const corners = new Map<number, { x: number; z: number }>();
    const KW = 0.09;
    for (const i of tiles) {
      const tx = i % W;
      const ty = Math.floor(i / W);
      for (const [dx, dy] of N4) {
        const t = T(tx + dx, ty + dy);
        if (mine(tx + dx, ty + dy) || dry(t)) continue;
        const along = dy !== 0; // the edge runs along x
        const ex = tx + 0.5 + dx * (0.5 - KW / 2);
        const ez = ty + 0.5 + dy * (0.5 - KW / 2);
        bridgeRail(b, (u, y, v) => along ? [ex + u, y, ez + v] : [ex - v, y, ez + u], { rot: [0, along ? 0 : -Math.PI / 2, 0] }, 1, tone, steel);
        // the edge's two ends get posts
        const ends = along
          ? [[tx, ty + (dy > 0 ? 1 : 0)], [tx + 1, ty + (dy > 0 ? 1 : 0)]]
          : [[tx + (dx > 0 ? 1 : 0), ty], [tx + (dx > 0 ? 1 : 0), ty + 1]];
        for (const [vx, vz] of ends) corners.set(vz! * (W + 1) + vx!, { x: vx!, z: vz! });
      }
    }
    for (const { x, z } of corners.values()) {
      // nudge each post into the deck (away from the water round the corner)
      let ox = 0;
      let oz = 0;
      let n = 0;
      for (const [qx, qz] of [[-1, -1], [0, -1], [-1, 0], [0, 0]] as const)
        if (mine(x + qx, z + qz)) {
          ox += qx * 2 + 1;
          oz += qz * 2 + 1;
          n++;
        }
      const px = x + Math.sign(ox) * KW * 0.55;
      const pz = z + Math.sign(oz) * KW * 0.55;
      bridgePost(b, px, pz, tone, steel);
      // a pile under each outer corner, down into the river
      if (n === 1) b.box(0.13, 0.9, 0.13, [x + Math.sign(ox) * 0.12, -0.55, z + Math.sign(oz) * 0.12], steel ? 0x2a2a2c : 0x4a3a2c);
    }
  }
  // Recessed approach lights mark the usable width of each crossing. The steel
  // housings and amber lenses join the deck's mesh and existing fog material.
  for (const { cx, cz, ux, uz, hl, hw } of spans) {
    if (hw < 0.23 || hl < 0.35) continue;
    const rot: Vec3 = [0, -Math.atan2(uz, ux), 0];
    for (const end of [-1, 1]) {
      const u = end * (hl - 0.23);
      for (const side of [-1, 1]) {
        const v = side * (hw - 0.14);
        const x = cx + u * ux - v * uz;
        const z = cz + u * uz + v * ux;
        b.box(0.24, 0.045, 0.13, [x, TOP + 0.022, z], 0x33383c, { rot });
        b.box(0.17, 0.013, 0.074, [x, TOP + 0.049, z], 0xffbd65, { rot, glow: 0.88 });
      }
    }
  }
  return { geo: b.empty ? null : b.build(), spans };
}

/**
 * A slanted run's bridge: one straight deck of planks (or plates) across it, with kerbs and rails
 * down both sides, abutments at the banks and piers into the river. Its tiles' stair-stepped
 * corners past the deck are left to the river (a hovercraft skims them; anything else standing
 * there stands on the deck's edge).
 */
function slantedBridge(b: ModelBuilder, r: BridgeRun, spans: DeckSpan[], tone: (k: number) => number, steel: boolean): void {
  const { ux, uz, hl, hw } = r;
  const cx = r.mx + ux * r.mid;
  const cz = r.mz + uz * r.mid;
  spans.push({ cx, cz, ux, uz, hl, hw });
  const P = (u: number, y: number, v: number): Vec3 => [cx + u * ux - v * uz, y, cz + u * uz + v * ux];
  const yaw: { rot: Vec3 } = { rot: [0, -r.ang, 0] };
  // the slab, its top just under the planks
  b.box(hl * 2, 0.13, hw * 2, P(0, 0.012 - 0.065, 0), tone(0.55), yaw);
  // planks (or plates) right across it, each its own tone
  const nP = Math.max(4, Math.round((hl * 2) / (steel ? 0.45 : 0.21)));
  const pitch = (hl * 2) / nP;
  const pw = pitch - (steel ? 0.04 : 0.035);
  const KW = 0.09;
  for (let k = 0; k < nP; k++) deckPanel(b, P, yaw, tone, steel, k, -hl + (k + 0.5) * pitch, pw, KW - hw, hw - KW, 0.012, TOP, true);
  for (const s of [-1, 1]) {
    const v = s * (hw - KW / 2);
    bridgeRail(b, (u, y, across) => P(u, y, v + across), yaw, hl * 2, tone, steel);
    const nPost = Math.max(1, Math.round(hl * 2));
    for (let k = 0; k <= nPost; k++) {
      const [x, , z] = P(-hl + 0.05 + (k * (hl * 2 - 0.1)) / nPost, 0, v);
      bridgePost(b, x, z, tone, steel, yaw);
    }
    bridgeSeat(b, P, yaw, s * hl, hw, steel);
  }
  const piers = Math.max(1, Math.round((hl * 2) / 1.8));
  for (let k = 0; k < piers; k++) {
    const u = -hl + (k + 0.5) * ((hl * 2) / piers);
    bridgePier(b, P, yaw, u, hw, steel);
  }
}

type BridgePoint = (u: number, y: number, v: number) => Vec3;
type BridgeYaw = { rot: Vec3 };

/** A flat, skewable strip in the deck plane, baked into the same mesh as its panel. */
function deckStrip(b: ModelBuilder, p: BridgePoint, y: number, a: number, start: number, z: number, end: number, width: number, hex: number): void {
  const d = width / 2;
  const left = p(a - d, y, start);
  const right = p(a + d, y, start);
  const farLeft = p(z - d, y, end);
  const farRight = p(z + d, y, end);
  const geo = new THREE.BufferGeometry();
  geo.setAttribute("position", new THREE.Float32BufferAttribute([...left, ...farLeft, ...farRight, ...left, ...farRight, ...right], 3));
  b.add(geo, [0, 0, 0], hex);
}

function deckPanel(
  b: ModelBuilder, p: BridgePoint, yaw: BridgeYaw, tone: (k: number) => number, steel: boolean,
  k: number, u: number, width: number, start: number, end: number, bottom: number, top: number, main: boolean
): void {
  if (width <= 0 || end <= start) return;
  const length = end - start;
  const tint = (steel ? 0.93 + hash(k, 3) * 0.17 : 0.88 + hash(k, 3) * 0.44) * (main ? 1 : 0.72);
  const hex = steel ? _c.setHex(0x677174).multiplyScalar(tint).getHex() : tone(tint);
  b.block(width, top - bottom, length, p(u, (top + bottom) / 2, (start + end) / 2), hex, { ...yaw, bevel: 0.008, edge: 1.26 });
  if (length < 0.25 || width < 0.08) return;
  if (steel) {
    const joint = _c.setHex(hex).multiplyScalar(0.64).getHex();
    const rib = _c.setHex(hex).multiplyScalar(1.32).getHex();
    const railU = u - width * 0.27;
    deckStrip(b, p, top + 0.001, railU, start + 0.025, railU, end - 0.025, 0.022, joint);
    deckStrip(b, p, top + 0.001, railU + 0.033, start + 0.03, railU + 0.033, end - 0.03, 0.015, rib);
    for (const v of [start + 0.065, end - 0.065])
      b.cyl(0.023, 0.026, 0.014, 5, p(u + width * 0.24, top + 0.006, v), rib);
    return;
  }
  // Two broken grain lines per board, in the direction of the wood fibres.
  for (const side of [-1, 1]) {
    const grain = u + width * (0.15 + hash(k, 10 + side) * 0.13) * side;
    const a = start + length * (0.06 + hash(k, 20 + side) * 0.28);
    const z = end - length * (0.06 + hash(k, 30 + side) * 0.28);
    deckStrip(b, p, top + 0.001, grain, a, grain - side * 0.012, z, 0.017, tone(tint * (side > 0 ? 0.66 : 1.24)));
  }
  if (k % 3 === 0)
    for (const v of [start + 0.065, end - 0.065])
      deckStrip(b, p, top + 0.002, u, v - 0.022, u, v + 0.022, 0.032, 0x3a3934);
}

function bridgeRail(b: ModelBuilder, p: BridgePoint, yaw: BridgeYaw, len: number, tone: (k: number) => number, steel: boolean): void {
  if (steel) {
    b.block(len, 0.072, 0.09, p(0, 0.036, 0), 0x343638, { ...yaw, bevel: 0.009 });
    const stripes = Math.max(2, Math.round(len / 0.25));
    const step = len / stripes;
    for (let k = 0; k < stripes; k++) {
      const u = -len / 2 + (k + 0.5) * step;
      deckStrip(b, p, 0.073, u - 0.035, -0.035, u + 0.035, 0.035, step * 0.52, 0xcaa045);
    }
    b.block(len, 0.045, 0.054, p(0, 0.33, 0), 0x677478, { ...yaw, bevel: 0.008, edge: 1.4 });
    b.box(len, 0.029, 0.038, p(0, 0.19, 0), 0x495152, yaw);
    return;
  }
  b.block(len, 0.075, 0.09, p(0, 0.0375, 0), tone(0.56), { ...yaw, bevel: 0.008 });
  b.block(len, 0.055, 0.064, p(0, 0.24, 0), tone(0.83), { ...yaw, bevel: 0.008, edge: 1.35 });
  // Oblique braces under the top rail give the timber span a distinct profile.
  const bays = Math.max(1, Math.round(len));
  const step = len / bays;
  for (let k = 0; k < bays; k++) {
    const u = -len / 2 + (k + 0.5) * step;
    const slope = (k % 2 ? -1 : 1) * Math.atan2(0.15, step * 0.8);
    b.box(Math.hypot(step * 0.8, 0.15), 0.032, 0.033, p(u, 0.147, 0), tone(0.59), { rot: [0, yaw.rot[1], slope] });
  }
}

function bridgePost(b: ModelBuilder, x: number, z: number, tone: (k: number) => number, steel: boolean, yaw?: BridgeYaw): void {
  const h = steel ? 0.36 : 0.27;
  b.block(0.085, h, 0.085, [x, h / 2, z], steel ? 0x4c5859 : tone(0.65), { ...yaw, bevel: 0.006 });
  b.block(0.09, 0.027, 0.09, [x, h - 0.009, z], steel ? 0x8b918e : 0x58534a, { ...yaw, bevel: 0.006, edge: 1.28 });
}

function bridgeSeat(b: ModelBuilder, p: BridgePoint, yaw: BridgeYaw, edge: number, hw: number, steel: boolean): void {
  // Seat the footing under the deck so its top cannot clip through the graded banks.
  const depth = Math.min(0.3, Math.abs(edge));
  const u = edge - Math.sign(edge) * depth / 2;
  const width = hw * 2 - 0.08;
  b.block(depth, 0.36, width, p(u, -0.245, 0), steel ? 0x494742 : 0x6d6659, { ...yaw, bevel: 0.025 });
  b.box(depth, 0.035, width, p(u, -0.045, 0), steel ? 0x626661 : 0x877f6e, yaw);
}

function bridgePier(b: ModelBuilder, p: BridgePoint, yaw: BridgeYaw, u: number, hw: number, steel: boolean): void {
  b.block(0.24, 0.12, hw * 2 + 0.1, p(u, -0.2, 0), steel ? 0x47494a : 0x4d3d31, { ...yaw, bevel: 0.018 });
  for (const s of [-0.65, 0.65]) {
    b.block(0.26, 0.9, 0.26, p(u, -0.7, s * hw), steel ? 0x3b3f3d : 0x625144, { ...yaw, bevel: 0.016, taper: 0.12 });
    b.box(0.26, 0.046, 0.26, p(u, -0.29, s * hw), steel ? 0x676e6c : 0x45413a, yaw);
  }
}
