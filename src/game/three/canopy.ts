import * as THREE from "three";

/** A tree as scattered: ground position (tiles) and size. */
export interface TreeSpot {
  x: number;
  y: number;
  s: number;
}

/** A robot's middle above ground, in tiles. */
const ROBOT_H = 0.2;
/** Size to use when a caller supplies a canopy mesh before attaching vertices. */
const DEFAULT_CROWN_H = 0.55;
const DEFAULT_CROWN_R = 0.32;
/** Thinned all the way inside this (plus the canopy's reach), not at all past FADE_R further out. */
const CLEAR_R = 0.5;
const FADE_R = 0.4;
/** Easing time constants (ms): the canopy clears quickly, grows back unhurried. */
const CLEAR_MS = 90;
const GROW_MS = 260;

/**
 * Woods thinned over infantry. Robots stand half a tree tall, so a squad in
 * the woods would all but vanish under the canopy (its ring too): the trees
 * whose canopy covers a squad on show — those right round it and in front of
 * it, toward the camera — dissolve to stumps of their trunks while it's
 * there (canopyMat) and grow back as it moves on. Only squads the player is
 * shown count: the trees never give away a Sniper Team hidden among them.
 */
export class Canopy {
  private readonly x: Float32Array;
  private readonly z: Float32Array;
  private readonly crownY: Float32Array;
  private readonly crownR: Float32Array;
  private maxY = ROBOT_H;
  private minY = ROBOT_H;
  private maxR = 0;
  /** The instanced mesh and slot of each tree; its thinning now and wanted this frame (0–1). */
  private readonly mesh: Uint8Array;
  private readonly slot: Uint32Array;
  readonly fade: Float32Array;
  private readonly want: Float32Array;
  private readonly attrs: THREE.InstancedBufferAttribute[] = [];
  private readonly dirty: boolean[] = [];
  /** Trees by tile (CSR: tile i's trees are at[start[i] … start[i + 1])). */
  private readonly start: Int32Array;
  private readonly at: Int32Array;
  /** Trees thinned at all, or wanted thinned (each listed once). */
  private active: number[] = [];
  private readonly listed: Uint8Array;

  constructor(
    private readonly W: number,
    private readonly H: number,
    meshes: { mesh: THREE.InstancedMesh; spots: TreeSpot[] }[]
  ) {
    const n = meshes.reduce((k, m) => k + m.spots.length, 0);
    this.x = new Float32Array(n);
    this.z = new Float32Array(n);
    this.crownY = new Float32Array(n);
    this.crownR = new Float32Array(n);
    this.mesh = new Uint8Array(n);
    this.slot = new Uint32Array(n);
    this.fade = new Float32Array(n);
    this.want = new Float32Array(n);
    this.listed = new Uint8Array(n);
    const tileOf = new Int32Array(n);
    const count = new Int32Array(W * H + 1);
    let i = 0;
    meshes.forEach(({ mesh, spots }, m) => {
      const attr = new THREE.InstancedBufferAttribute(new Float32Array(spots.length), 1);
      attr.setUsage(THREE.DynamicDrawUsage);
      mesh.geometry.setAttribute("canopy", attr);
      this.attrs.push(attr);
      this.dirty.push(false);
      // The palm fronds, pine skirts and scrub crowns cover different areas on screen.
      // Measure the widest part above the stump once per variant.
      const p = mesh.geometry.getAttribute("position");
      const vertices = p?.count ?? 0;
      let radius = vertices ? 0 : DEFAULT_CROWN_R;
      let height = DEFAULT_CROWN_H;
      for (let j = 0; j < vertices; j++) {
        const y = p.getY(j);
        if (y < 0.2) continue;
        const r = Math.hypot(p.getX(j), p.getZ(j));
        if (r > radius) {
          radius = r;
          height = y;
        }
      }
      spots.forEach((p, k) => {
        this.x[i] = p.x;
        this.z[i] = p.y;
        this.crownY[i] = height * p.s;
        this.crownR[i] = radius * p.s;
        this.maxY = Math.max(this.maxY, this.crownY[i]!);
        this.minY = Math.min(this.minY, this.crownY[i]!);
        this.maxR = Math.max(this.maxR, this.crownR[i]!);
        this.mesh[i] = m;
        this.slot[i] = k;
        const t = Math.min(H - 1, Math.max(0, Math.floor(p.y))) * W + Math.min(W - 1, Math.max(0, Math.floor(p.x)));
        tileOf[i] = t;
        count[t + 1]!++;
        i++;
      });
    });
    for (let t = 0; t < W * H; t++) count[t + 1]! += count[t]!;
    this.start = count.slice();
    this.at = new Int32Array(n);
    for (let k = 0; k < n; k++) this.at[count[tileOf[k]!]!++] = k;
  }

  /**
   * Thin the trees over the squads at `points` (x, y pairs, tiles; `n` of
   * them) for a camera pitched `cot` (cotangent of its angle below the
   * horizon: how far north a height shows on the ground), easing over `dtMs`.
   */
  thin(points: ArrayLike<number>, n: number, cot: number, dtMs: number): void {
    const want = this.want;
    for (const i of this.active) want[i] = 0;
    // a canopy covers the ground (and the robots) north of it, the higher the further: look south
    const shiftMin = (this.minY - ROBOT_H) * cot;
    const shiftMax = (this.maxY - ROBOT_H) * cot;
    const reach = CLEAR_R + this.maxR + FADE_R;
    for (let p = 0; p < n; p++) {
      const sx = points[p * 2]!;
      const sz = points[p * 2 + 1]!;
      const x0 = Math.max(0, Math.floor(sx - reach));
      const x1 = Math.min(this.W - 1, Math.floor(sx + reach));
      const y0 = Math.max(0, Math.floor(sz - reach + Math.min(shiftMin, shiftMax)));
      const y1 = Math.min(this.H - 1, Math.floor(sz + reach + Math.max(shiftMin, shiftMax)));
      for (let ty = y0; ty <= y1; ty++)
        for (let tx = x0; tx <= x1; tx++) {
          const t = ty * this.W + tx;
          for (let k = this.start[t]!; k < this.start[t + 1]!; k++) {
            const i = this.at[k]!;
            const dx = this.x[i]! - sx;
            const dz = this.z[i]! - sz - (this.crownY[i]! - ROBOT_H) * cot;
            const r0 = CLEAR_R + this.crownR[i]!;
            const w = 1 - (Math.hypot(dx, dz) - r0) / FADE_R;
            if (w <= want[i]!) continue;
            want[i] = Math.min(1, w);
            if (!this.listed[i]) {
              this.listed[i] = 1;
              this.active.push(i);
            }
          }
        }
    }
    const clear = 1 - Math.exp(-dtMs / CLEAR_MS);
    const grow = 1 - Math.exp(-dtMs / GROW_MS);
    const fade = this.fade;
    let keep = 0;
    for (let a = 0; a < this.active.length; a++) {
      const i = this.active[a]!;
      const to = want[i]!;
      const from = fade[i]!;
      let f = from + (to - from) * (to > from ? clear : grow);
      if (to === 0 && f < 0.01) f = 0;
      if (f !== from) {
        fade[i] = f;
        this.attrs[this.mesh[i]!]!.setX(this.slot[i]!, f);
        this.dirty[this.mesh[i]!] = true;
      }
      if (f > 0 || to > 0) this.active[keep++] = i;
      else this.listed[i] = 0;
    }
    this.active.length = keep;
    for (let m = 0; m < this.attrs.length; m++)
      if (this.dirty[m]) {
        this.attrs[m]!.needsUpdate = true;
        this.dirty[m] = false;
      }
  }
}
