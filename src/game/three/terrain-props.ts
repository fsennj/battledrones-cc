import * as THREE from "three";
import type { Biome } from "../../sim/types";
import { ModelBuilder, type Vec3 } from "./builder";

/**
 * Prop geometry for the battlefield: trees per biome, rock crags and loose
 * boulders, scrap heaps and crystal clusters. Trees, scrap and crystals are
 * a few shared variants (instanced by the terrain); crags are one-off
 * shapes merged into a single mesh, each coloured from the painted rock it
 * stands on so outcrops read as part of the hand-painted landscape.
 */

/** Seeded PRNG (Park–Miller). */
export function prng(seed: number): () => number {
  let s = Math.max(1, Math.floor(seed) % 2147483647);
  return () => (s = (s * 16807) % 2147483647) / 2147483647;
}

/** Deterministic hash → [0, 1). */
export const hash = (i: number, k: number) => {
  const x = Math.sin(i * 12.9898 + k * 78.233) * 43758.5453;
  return x - Math.floor(x);
};

// ------------------------------------------------------------- crags --

export interface CragSpot {
  x: number;
  y: number;
  /** Ground height to sit on (the lowest point under its footprint). */
  h: number;
  /** Footprint radius (tiles). */
  s: number;
  rot: number;
  /** Linear colour of the painted rock (or ground) beneath. */
  tint: THREE.Color;
  /** 0 crag, 1 slab, 2 spire, 3 loose boulder. */
  kind: number;
  seed: number;
}

const _m = new THREE.Matrix4();
const _q = new THREE.Quaternion();
const _v = new THREE.Vector3();
const _a = new THREE.Vector3();
const _b = new THREE.Vector3();
const _c = new THREE.Vector3();
const _n = new THREE.Vector3();
const _e = new THREE.Vector3();
const _off = new THREE.Vector3();
const TRI = [_a, _b, _c];
const UP = new THREE.Vector3(0, 1, 0);

/** Hash of a lattice position → [-1, 1): shared corners jitter together, so facets never crack. */
function jitterAt(x: number, y: number, z: number, seed: number): number {
  const k = Math.sin(Math.round(x * 1000) * 12.9898 + Math.round(y * 1000) * 78.233 + Math.round(z * 1000) * 37.719 + seed * 4.1) * 43758.5453;
  return (k - Math.floor(k)) * 2 - 1;
}

/**
 * One rock: a jittered icosphere squashed and cut by a tilted plane, so it
 * reads as broken stone with a weathered flat top rather than a pebble.
 * Unit footprint, base at y = 0. Returns non-indexed positions.
 */
function rockShape(rnd: () => number, sx: number, sy: number, sz: number, cut: number, seed: number, detail = 0): Float32Array {
  const g = new THREE.IcosahedronGeometry(1, detail);
  const p = g.attributes.position!.array as Float32Array;
  const tx = (rnd() - 0.5) * 0.5;
  const tz = (rnd() - 0.5) * 0.5;
  for (let i = 0; i < p.length; i += 3) {
    const x = p[i]!;
    const y = p[i + 1]!;
    const z = p[i + 2]!;
    const j = 1 + jitterAt(x, y, z, seed) * 0.3;
    let nx = x * j * sx;
    let ny = (y * j * 0.5 + 0.5) * sy;
    let nz = z * j * sz;
    // a tilted cleavage plane shears the top flat
    const top = cut * sy + tx * nx + tz * nz;
    if (ny > top) ny = top + (ny - top) * 0.12;
    if (ny < 0) ny *= 0.3;
    // and the sides lean in a little toward the top
    const lean = 1 - Math.max(0, ny / sy) * 0.18;
    nx *= lean;
    nz *= lean;
    p[i] = nx;
    p[i + 1] = ny;
    p[i + 2] = nz;
  }
  const out = new Float32Array(p);
  g.dispose();
  return out;
}

/** Three fractured ledges around a single tilted cleavage plane. */
function outcropShape(rnd: () => number, sx: number, sy: number, sz: number, cut: number, column: boolean): Float32Array {
  const n = column ? 6 : 7;
  const phase = rnd() * Math.PI * 2;
  const tilt = (rnd() - 0.5) * sy * 0.36;
  const rim = Array.from({ length: n }, (_, i) => {
    const a = phase + (i + (rnd() - 0.5) * 0.25) * Math.PI * 2 / n;
    const r = 0.88 + rnd() * 0.21;
    return [Math.cos(a) * r, Math.sin(a) * r] as const;
  });
  const levels = column ? [[-0.06, 1], [0.45, 0.91], [cut, 0.79]] : [[-0.08, 0.94], [cut * 0.45, 1], [cut * 0.52, 0.88], [cut, 0.69]];
  const rings = levels.map(([y, r]) => rim.map(([x, z], i): Vec3 => [
    x * sx * r! + sy * (y! + 0.08) * 0.09,
    sy * y! + x * tilt + (i % 2 ? 1 : -1) * sy * 0.035,
    z * sz * r!
  ]));
  const pos: number[] = [];
  const tri = (a: Vec3, b: Vec3, c: Vec3) => pos.push(...a, ...b, ...c);
  for (let k = 1; k < rings.length; k++) {
    const low = rings[k - 1]!;
    const high = rings[k]!;
    for (let i = 0; i < n; i++) {
      const j = (i + 1) % n;
      tri(low[i]!, high[i]!, high[j]!);
      tri(low[i]!, high[j]!, low[j]!);
    }
  }
  const top = rings[rings.length - 1]!;
  for (let i = 1; i < n - 1; i++) tri(top[0]!, top[i + 1]!, top[i]!);
  return new Float32Array(pos);
}

/**
 * Merge every crag into one vertex-coloured mesh geometry (one draw call). `textured`: for the
 * rock-textured crag material (the texture brings its own strata; no glow attribute), else for
 * the model material.
 */
export function cragGeometry(spots: CragSpot[], biome: Biome, textured = false): THREE.BufferGeometry | null {
  const pos: number[] = [];
  const col: number[] = [];
  const snow = biome === "arctic";
  const strata = biome === "desert" ? 0.13 : biome === "volcanic" ? 0.2 : 0;
  const base = new THREE.Color();
  const grey = new THREE.Color();
  const snowCol = new THREE.Color(0.66, 0.75, 0.83);
  const c = new THREE.Color();
  // (on the arctic ridges the painted rock is near black under snow streaks: the crags are a grey stone,
  // lighter than the paint so their shape reads, but dark enough under the bright arctic light that
  // their frosted caps read too, rather than the whole crag going white)
  const minL = biome === "volcanic" ? 0.05 : snow ? 0.07 : 0.12;
  // (pale limestone karst on the reef would grey out under the usual cap)
  const maxL = snow ? 0.1 : biome === "tropical" ? 0.42 : 0.3;
  // karst towers wear a cap of jungle where arctic crags wear snow
  const jungle = biome === "tropical";
  const jungleCol = new THREE.Color(0x41604a);
  const mossCol = new THREE.Color(0x577143);
  const ashCol = new THREE.Color(0x7a5544);
  const hsl = { h: 0, s: 0, l: 0 };
  for (const sp of spots) {
    const rnd = prng(sp.seed * 7919 + 17);
    // parts: [scale x, y, z, cleavage height (of y), offset x, z]
    const parts: [number, number, number, number, number, number][] = [];
    if (sp.kind === 0) {
      parts.push([0.62, 0.95 + rnd() * 0.35, 0.52, 0.72, 0, 0]);
      parts.push([0.36, 0.6 + rnd() * 0.25, 0.32, 0.8, 0.42, 0.2 - rnd() * 0.4]);
      if (rnd() < 0.6) parts.push([0.26, 0.42, 0.24, 0.85, -0.38, 0.28]);
    } else if (sp.kind === 1) {
      parts.push([0.75, 0.42 + rnd() * 0.15, 0.6, 0.62, 0, 0]);
      parts.push([0.32, 0.3, 0.28, 0.8, -0.5, 0.35]);
    } else if (sp.kind === 2) {
      parts.push([0.34, 1.35 + rnd() * 0.4, 0.3, 0.86, 0, 0]);
      parts.push([0.42, 0.55, 0.36, 0.7, 0.26, 0.24]);
    } else {
      parts.push([0.55, 0.5 + rnd() * 0.25, 0.48, 0.7, 0, 0]);
      if (hash(sp.seed, 62) < 0.7) parts.push([0.23, 0.2, 0.19, 0.88, 0.54, 0.22]);
    }
    const column = biome === "volcanic" && sp.kind === 2;
    if (column) parts.push([0.22, 0.9 + rnd() * 0.24, 0.21, 0.77, -0.28, -0.11]);
    // colour: the painted tint's hue, lifted toward the painted rock's lit faces (the paint's
    // average sits between its sunlit stone and black crevices; the crag shades itself)
    base.copy(sp.tint);
    base.getHSL(hsl);
    base.setHSL(hsl.h, Math.min(1, hsl.s * 1.1), Math.min(maxL, Math.max(minL, hsl.l * 1.7)));
    const l = base.r * 0.3 + base.g * 0.6 + base.b * 0.1;
    grey.setRGB(l * 1.3, l * 1.3, l * 1.3);
    for (const [part, [sx, sy, sz, cut, ox, oz]] of parts.entries()) {
      const p = (part === 0 && sp.kind === 1) || column
        ? outcropShape(rnd, sx, sy, sz, cut, column)
        : rockShape(rnd, sx, sy, sz, cut, sp.seed + ox * 31 + oz * 17);
      const top = sy * cut;
      _q.setFromAxisAngle(UP, sp.rot);
      _m.compose(_v.set(sp.x, sp.h, sp.y), _q, _a.set(sp.s, sp.s, sp.s));
      _off.set(ox, 0, oz);
      for (let i = 0; i < p.length; i += 9) {
        // face normal (local) for snow and shading
        _a.set(p[i]!, p[i + 1]!, p[i + 2]!);
        _b.set(p[i + 3]!, p[i + 4]!, p[i + 5]!);
        _c.set(p[i + 6]!, p[i + 7]!, p[i + 8]!);
        _n.subVectors(_c, _b).cross(_e.subVectors(_a, _b)).normalize();
        const fy = (_a.y + _b.y + _c.y) / 3;
        const k = Math.min(1, Math.max(0, fy / Math.max(0.01, top)));
        // dark at the foot (contact shadow), lighter toward the weathered top, and each facet a little different
        const facet = 0.91 + rnd() * 0.18;
        let shade = (0.48 + 0.82 * Math.pow(k, 0.82)) * facet;
        if (strata > 0) shade *= 0.92 + 0.08 * Math.sin((sp.h + fy * sp.s + _a.x * 0.06) / strata * Math.PI);
        c.copy(base).multiplyScalar(shade * (0.94 + part * 0.03));
        // snow lies only on the flat of the cap, a dusting that thickens toward the top
        if (snow && _n.y > 0.63 && k > 0.64) c.lerp(snowCol, Math.min(0.54, (k - 0.55) * _n.y) * facet);
        else if (jungle && _n.y > 0.67 && k > 0.65) c.lerp(jungleCol, Math.min(0.53, (k - 0.46) * _n.y) * facet);
        else if (biome === "temperate" && _n.y > 0.53 && k > 0.69) c.lerp(mossCol, 0.19 * facet);
        else if (biome === "volcanic" && _n.y < 0.45 && k < 0.49) c.lerp(ashCol, 0.18 * facet);
        else if (_n.y > 0.75 && k > 0.6) c.lerp(grey, 0.12);
        for (const v of TRI) {
          v.add(_off).applyMatrix4(_m);
          pos.push(v.x, v.y, v.z);
          col.push(c.r, c.g, c.b);
        }
      }
    }
  }
  if (pos.length === 0) return null;
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3));
  g.setAttribute("color", new THREE.Float32BufferAttribute(col, 3));
  if (!textured) g.setAttribute("glow", new THREE.Float32BufferAttribute(new Float32Array(pos.length / 3), 1));
  g.computeVertexNormals();
  g.computeBoundingSphere();
  return g;
}

// ------------------------------------------------------------- trees --

/** A taper between actual branch joints keeps bends joined at every zoom. */
function branch(b: ModelBuilder, from: Vec3, to: Vec3, r0: number, r1: number, hex: number, sides = 5, cap = false): void {
  const start = new THREE.Vector3(...from);
  const end = new THREE.Vector3(...to);
  const axis = end.clone().sub(start);
  const geo = new THREE.CylinderGeometry(r1, r0, axis.length(), sides, 1, !cap);
  geo.applyQuaternion(new THREE.Quaternion().setFromUnitVectors(UP, axis.normalize()));
  b.add(geo, start.add(end).multiplyScalar(0.5).toArray(), hex);
}

function tuft(b: ModelBuilder, r: number, at: Vec3, hex: number, scale: Vec3 = [1, 1, 1], glow = 0): void {
  b.add(new THREE.IcosahedronGeometry(r, 0), at, hex, { scale, glow, rot: [at[0] * 3, at[2] * 5, 0] });
}

/** Folded leaf with a raised rib, cut shoulders and a pointed tip. */
function leaf(b: ModelBuilder, at: Vec3, a: number, l: number, w: number, rise: number, end: number, hex: number): void {
  const root: Vec3 = [0, 0, 0];
  const rib: Vec3 = [l * 0.43, rise, 0];
  const left: Vec3 = [l * 0.28, rise - w * 0.26, -w * 0.4];
  const right: Vec3 = [l * 0.44, rise - w * 0.3, w * 0.53];
  const tip: Vec3 = [l, end, 0];
  const cut: Vec3 = [l * 0.75, (rise + end) / 2 - w * 0.26, -w * 0.32];
  const geo = new THREE.BufferGeometry();
  geo.setAttribute("position", new THREE.Float32BufferAttribute([
    ...root, ...rib, ...left, ...left, ...rib, ...cut, ...cut, ...rib, ...tip,
    ...root, ...right, ...rib, ...rib, ...right, ...tip
  ], 3));
  geo.setAttribute("shade", new THREE.Float32BufferAttribute([
    0.7, 1.06, 0.87, 0.87, 1.06, 0.9, 0.9, 1.06, 1.18, 0.58, 0.75, 0.92, 0.92, 0.75, 1.08
  ], 1));
  b.add(geo, at, hex, { rot: [0, -a, 0] });
}

function palm(b: ModelBuilder, v: number, tropical: boolean): void {
  const size = tropical ? 1 + v * 0.025 : 0.86 + v * 0.022;
  const lean = (v % 2 ? -1 : 1) * 0.2;
  const bark = tropical ? [0x786754, 0x9c8469] : [0x8b6b49, 0xa68a60];
  let foot: Vec3 = [0, 0, 0];
  for (let i = 1; i <= 5; i++) {
    const f = i / 5;
    const joint: Vec3 = [lean * f * f, f * size, -0.035 * f];
    branch(b, foot, joint, 0.056 - (i - 1) * 0.0045, 0.056 - i * 0.0045, bark[i % 2]!);
    foot = joint;
  }
  const count = tropical ? 9 : 7;
  for (let i = 0; i < count; i++) {
    const f = hash(v, i + 3);
    leaf(b, foot, i * Math.PI * 2 / count + v, 0.35 + f * 0.22, 0.15 + f * 0.05, 0.1 + f * 0.055, -0.14 + f * 0.15,
      (tropical ? [0x416d43, 0x517d43, 0x668b48] : [0x636b3c, 0x737d44, 0x899152])[i % 3]!);
  }
  tuft(b, 0.064, foot, 0x625239, [1, 0.83, 1]);
}

function conifer(b: ModelBuilder, v: number, snow: boolean): void {
  const height = 0.88 + v * 0.04;
  branch(b, [0, 0, 0], [0.035, height * 0.7, 0], 0.064, 0.024, snow ? 0x534538 : 0x695542);
  const greens = snow ? [0x2e4840, 0x3a5144, 0x4a604c] : [0x314e38, 0x45603e, 0x5c7046];
  for (let level = 0; level < 3; level++) {
    const r = 0.32 - level * 0.071;
    const y = height * (0.25 + level * 0.22);
    const tips: Vec3[] = [];
    const shoulder: Vec3[] = [];
    const apex: Vec3 = [0.033, y + height * 0.34, -0.025];
    for (let i = 0; i < 8; i++) {
      const a = (i * Math.PI / 4) + level * 0.35 + v;
      const q = (i % 2 ? 0.66 : 1) * (0.96 + hash(v * 3 + level, i) * 0.13);
      tips.push([Math.cos(a) * r * q, y + (i % 2 ? 0.025 : -0.02), Math.sin(a) * r * q]);
      shoulder.push([Math.cos(a) * r * q * 0.73, y + height * 0.09, Math.sin(a) * r * q * 0.73]);
    }
    const skirt: number[] = [];
    const crown: number[] = [];
    for (let i = 0; i < tips.length; i++) {
      const j = (i + 1) % tips.length;
      skirt.push(...tips[i]!, ...shoulder[i]!, ...shoulder[j]!, ...tips[i]!, ...shoulder[j]!, ...tips[j]!);
      crown.push(...shoulder[i]!, ...apex, ...shoulder[j]!);
    }
    for (const [pos, hex] of [[skirt, greens[level]!], [crown, snow ? [0x9daeb4, 0xb8c7ca, 0xd5e0df][level]! : greens[level]!]] as const) {
      const g = new THREE.BufferGeometry();
      g.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3));
      b.add(g, [0, 0, 0], hex);
    }
  }
}

function broadleaf(b: ModelBuilder, v: number, tropical: boolean): void {
  const mangrove = tropical && v === 2;
  const trunk = mangrove ? 0.33 : 0.47 + v * 0.025;
  const wood = tropical ? 0x82745b : 0x6f543c;
  const base: Vec3 = [0, 0, 0];
  const fork: Vec3 = [-0.025, trunk, 0.017];
  branch(b, base, fork, 0.07, 0.039, wood, 6);
  const roots = mangrove ? 5 : 3;
  for (let i = 0; i < roots; i++) {
    const a = i * Math.PI * 2 / roots + v;
    const r = mangrove ? 0.18 : 0.14;
    branch(b, [Math.cos(a) * r, 0.01, Math.sin(a) * r], [0, mangrove ? 0.24 : 0.13, 0], 0.018, 0.027, 0x635240, 4);
  }
  const colors = tropical ? [0x304f3d, 0x42694a, 0x5c814b, 0x708c52] : [0x465a39, 0x566b3e, 0x6c7c49, 0x7f874e];
  const lobes = tropical ? 4 : 3;
  for (let i = 0; i < lobes; i++) {
    const a = i * Math.PI * 2 / lobes + v;
    const q = hash(v + 17, i);
    const reach = 0.12 + q * 0.085;
    const at: Vec3 = [Math.cos(a) * reach, trunk + 0.11 + q * 0.09, Math.sin(a) * reach];
    if (i % 2 === 0) branch(b, fork, at, 0.033, 0.018, wood, 4);
    tuft(b, 0.219 + q * 0.038, at, colors[i]!, [1.12, tropical ? 0.53 : 0.79, 0.97]);
  }
  tuft(b, 0.23, [0.032, trunk + 0.255, -0.025], colors[2]!, [1.12, tropical ? 0.57 : 0.77, 1.09]);
}

export function treeGeos(biome: Biome): THREE.BufferGeometry[] {
  const out: THREE.BufferGeometry[] = [];
  for (let v = 0; v < 6; v++) {
    const b = new ModelBuilder({ grade: 0.18, ao: [0.17, 0.31] });
    if (biome === "arctic" || (biome === "temperate" && v % 3 === 2)) {
      conifer(b, v, biome === "arctic");
    } else if ((biome === "desert" && v % 2 === 0) || (biome === "tropical" && v % 3 === 0)) {
      palm(b, v, biome === "tropical");
    } else if (biome === "desert" || (biome === "tropical" && v === 5)) {
      // Sage and yucca in the dry bed, ferns and broad fronds on the coast.
      const tropical = biome === "tropical";
      if (!tropical) tuft(b, 0.22, [0, 0.12, 0], 0x766c43, [1.1, 0.55, 1]);
      for (let i = 0; i < 7; i++) {
        const q = hash(v, i + 10);
        leaf(b, [0, 0.07, 0], i * Math.PI * 2 / 7 + v, 0.24 + q * 0.22, tropical ? 0.15 : 0.07,
          0.14 + q * 0.07, 0.05 + q * 0.22, (tropical ? [0x527745, 0x6c8e4d] : [0x737f52, 0x929659])[i % 2]!);
      }
    } else if (biome !== "volcanic") {
      broadleaf(b, v, biome === "tropical");
    } else if (v % 3 !== 2) {
      // Charred timber, with the pale cross-section of each limb exposed.
      const fork: Vec3 = [-0.02 + v * 0.01, 0.43 + 0.018 * v, 0.02];
      const tip: Vec3 = [-0.13 + v * 0.02, 0.73, -0.036];
      branch(b, [0, 0, 0], fork, 0.084, 0.046, 0x493b32);
      branch(b, fork, tip, 0.047, 0.019, 0x3d3630, 5, true);
      for (let i = 0; i < 3; i++) {
        const a = i * Math.PI * 2 / 3 + v;
        const joint: Vec3 = [Math.cos(a) * 0.18, fork[1] + 0.095, Math.sin(a) * 0.16];
        const limb: Vec3 = [joint[0] * 1.35, joint[1] + 0.11, joint[2] * 1.35];
        branch(b, [fork[0], fork[1] - i * 0.055, fork[2]], joint, 0.028, 0.022, 0x514237, 4);
        branch(b, joint, limb, 0.022, 0.014, 0x786052, 4, true);
      }
      tuft(b, 0.03, [0.04, 0.095, -0.03], 0xe27539, [1.4, 0.72, 0.9], 0.48);
    } else {
      tuft(b, 0.21, [0, 0.102, 0], 0x51423a, [1.2, 0.55, 1.1]);
      tuft(b, 0.14, [0.17, 0.087, 0.08], 0x3c322e, [1, 0.57, 1]);
      for (let i = 0; i < 4; i++) {
        const a = i * Math.PI / 2 + v;
        branch(b, [0, 0.11, 0], [Math.cos(a) * 0.24, 0.18, Math.sin(a) * 0.24], 0.022, 0.007, 0x5e493c, 4);
      }
      tuft(b, 0.04, [0.07, 0.153, 0.06], 0xdd753c, [1, 0.72, 1], 0.44);
    }
    out.push(b.build());
  }
  return out;
}

// ------------------------------------------------------ scrap, crystals --

/**
 * Salvage heaps: a low bed of crushed debris with wrecked hull plates and a
 * girder leaning into it, a toppled drum, loose junk, and an amber salvage
 * core glinting on top — gunmetal and rust, so a field reads as metal.
 */
export function scrapGeos(): THREE.BufferGeometry[] {
  const out: THREE.BufferGeometry[] = [];
  const plates = [0x737a83, 0x5d636b, 0x8a4a2a, 0x9a7a44, 0x868c94];
  const junk = [0x6e5238, 0x8a6a3a, 0x5a5f66, 0x7a4a2a, 0x9a7a44, 0x46494e];
  for (let v = 0; v < 3; v++) {
    const b = new ModelBuilder({ grade: 0.2, ao: [0.12, 0.28] });
    const rnd = prng(v * 7919 + 13);
    b.sphere(0.36, [0, -0.05, 0], 0x3d3630, { w: 9, h: 4, phi: Math.PI / 2, scale: [1, 0.36, 1] });
    // hull plates leaning in from round the edge
    for (let i = 0; i < 3; i++) {
      const a = (i / 3) * Math.PI * 2 + rnd() * 1.2;
      const x = Math.cos(a) * 0.15;
      const z = Math.sin(a) * 0.15;
      b.block(0.22 + rnd() * 0.08, 0.033, 0.15 + rnd() * 0.05, [x, 0.1, z], plates[Math.floor(rnd() * plates.length)]!, {
        rot: [Math.sin(a) * 0.7, -a, -Math.cos(a) * 0.7], bevel: 0.011, edge: 1.48
      });
    }
    // a girder across the heap and a toppled drum
    const ga = rnd() * Math.PI;
    const girder = { rot: [0, ga, 0.25] as Vec3 };
    b.box(0.42, 0.062, 0.028, [0, 0.13, 0], 0x4b514f, girder);
    b.block(0.42, 0.024, 0.075, [0, 0.163, 0], 0x7c8784, { ...girder, bevel: 0.006 });
    const x = Math.cos(ga + 1.6) * 0.2;
    const z = Math.sin(ga + 1.6) * 0.2;
    const drum = { rot: [Math.PI / 2, 0, ga] as Vec3 };
    b.cyl(0.061, 0.061, 0.17, 7, [x, 0.066, z], [0x9a6a2a, 0x7a4a2a, 0x5a6a3a][v]!, drum);
    for (const s of [-1, 1]) b.cyl(0.066, 0.066, 0.022, 7, [x + s * Math.sin(ga) * 0.068, 0.066, z - s * Math.cos(ga) * 0.068], 0x4e5050, drum);
    for (let i = 0; i < 6; i++) {
      const a = rnd() * Math.PI * 2;
      const d = rnd() * 0.22;
      b.box(0.06 + rnd() * 0.09, 0.04 + rnd() * 0.05, 0.05 + rnd() * 0.08, [Math.cos(a) * d, 0.08 + (0.22 - d) * 0.35, Math.sin(a) * d], junk[Math.floor(rnd() * junk.length)]!, {
        rot: [rnd() * 1.2, rnd() * 3, rnd() * 1.2]
      });
    }
    b.box(0.06, 0.06, 0.06, [0.04, 0.21, -0.02], 0xffc94a, { glow: 0.7, rot: [0.6, 0.4, 0] });
    out.push(b.build());
  }
  return out;
}

export function crystalGeos(): THREE.BufferGeometry[] {
  const out: THREE.BufferGeometry[] = [];
  for (let v = 0; v < 3; v++) {
    const b = new ModelBuilder();
    let s = v * 104729 + 7;
    const rnd = () => ((s = (s * 16807) % 2147483647) / 2147483647);
    b.add(new THREE.DodecahedronGeometry(0.22, 0), [0, 0.02, 0], 0x3a3f3a, { scale: [1.3, 0.4, 1.2] });
    const n = 5 + v;
    for (let i = 0; i < n; i++) {
      const a = (i / n) * Math.PI * 2 + rnd();
      const d = i === 0 ? 0 : 0.1 + rnd() * 0.14;
      const h = (i === 0 ? 0.5 : 0.22 + rnd() * 0.22) * 1.1;
      const r = i === 0 ? 0.07 : 0.04 + rnd() * 0.03;
      const lean = i === 0 ? 0 : 0.35 + rnd() * 0.3;
      const col = [0x3dffa0, 0x2fd88a, 0x6dffc0][i % 3]!;
      const x = Math.cos(a) * d;
      const z = Math.sin(a) * d;
      b.cyl(0, r, h, 5, [x + Math.cos(a) * Math.sin(lean) * h * 0.5, h * 0.5 * Math.cos(lean), z + Math.sin(a) * Math.sin(lean) * h * 0.5], col, {
        glow: 0.55,
        rot: [Math.sin(a) * lean, 0, -Math.cos(a) * lean]
      });
    }
    out.push(b.build());
  }
  return out;
}
