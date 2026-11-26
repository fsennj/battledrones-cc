import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import type { BuildingKind, UnitKind } from "../../sim/types";

/**
 * Hand-built models from Blender (art/blender/*.py -> public/assets/models/*.glb) replace the
 * procedural ones, unit by unit and building by building. Each animated mesh is authored in
 * local coordinates around its game pivot. The game places and animates it. Blue vertex
 * colours are recoloured per faction and amber becomes glow. Missing meshes use the
 * procedural geometry. Buildings are authored at map scale (1 = one tile).
 */

interface Team {
  main: number;
  dark: number;
  light: number;
}

export interface GlbParts {
  hull: THREE.BufferGeometry;
  turret?: THREE.BufferGeometry;
  ramp?: THREE.BufferGeometry;
  rotor?: THREE.BufferGeometry;
}

const GLB_UNITS: Partial<Record<UnitKind, string>> = Object.fromEntries(
  (["juggernaut", "stinger", "mastodon", "lancer", "harvester", "condor", "wasp", "raptor", "scout", "flak-crawler", "mortar", "mender", "hornet"] as UnitKind[]).map((k) => [k, `assets/models/${k}.glb`])
);
/** Buildings with Blender geometry, including separately animated turret or radar heads. */
const GLB_BUILDINGS: Partial<Record<BuildingKind, string>> = Object.fromEntries(
  (["hq", "fab-plant", "depot", "airpad", "radar", "sam-site", "turret"] as BuildingKind[]).map((k) => [k, `assets/models/${k}.glb`])
);
const loaded = new Map<UnitKind | BuildingKind, GlbParts>();

export const glbUnit = (kind: UnitKind): GlbParts | undefined => loaded.get(kind);
export const glbBuilding = (kind: BuildingKind): GlbParts | undefined => loaded.get(kind);

/** A GLB mesh as a game geometry: flat-shaded, vertex colours (rgb) and a glow weight. */
function toGame(src: THREE.BufferGeometry): THREE.BufferGeometry {
  const g = src.index ? src.toNonIndexed() : src.clone();
  const col = g.attributes.color as THREE.BufferAttribute | undefined;
  const n = g.attributes.position!.count;
  const cols = new Float32Array(n * 3);
  const glow = new Float32Array(n);
  for (let i = 0; i < n; i++) {
    const r = col ? col.getX(i) : 0.5;
    const gr = col ? col.getY(i) : 0.5;
    const b = col ? col.getZ(i) : 0.5;
    cols.set([r, gr, b], i * 3);
    // amber lights (HAZ yellow has g/r ~0.6, so it stays plain colour)
    if (r > 0.5 && gr < 0.45 * r && b < 0.15 * r) glow[i] = 1;
  }
  for (const name of Object.keys(g.attributes)) if (name !== "position") g.deleteAttribute(name);
  g.setAttribute("color", new THREE.BufferAttribute(cols, 3));
  g.setAttribute("glow", new THREE.BufferAttribute(glow, 1));
  g.computeVertexNormals();
  g.computeBoundingBox();
  g.computeBoundingSphere();
  return g;
}

const lum = (r: number, g: number, b: number) => 0.2126 * r + 0.7152 * g + 0.0722 * b;

/** The GLB is painted blue: the same geometry in another faction's team colours. */
export function recolor(geo: THREE.BufferGeometry, from: Team, to: Team): THREE.BufferGeometry {
  const g = geo.clone();
  const col = g.attributes.color as THREE.BufferAttribute;
  const src = [from.main, from.dark, from.light].map((h) => new THREE.Color().setHex(h));
  const dst = [to.main, to.dark, to.light].map((h) => new THREE.Color().setHex(h));
  const srcLum = src.map((c) => lum(c.r, c.g, c.b));
  for (let i = 0; i < col.count; i++) {
    const r = col.getX(i), gr = col.getY(i), b = col.getZ(i);
    if (!(b > 1.8 * r && b > 1.5 * gr)) continue; // neutral gunmetal, amber, hazard: not team paint
    const l = lum(r, gr, b);
    let best = 0;
    let bestK = Infinity;
    for (let j = 0; j < 3; j++) {
      const k = l / srcLum[j]!;
      if (Math.abs(Math.log(k)) < Math.abs(Math.log(bestK))) {
        best = j;
        bestK = k;
      }
    }
    const d = dst[best]!;
    col.setXYZ(i, Math.min(1, d.r * bestK), Math.min(1, d.g * bestK), Math.min(1, d.b * bestK));
  }
  return g;
}

/**
 * Load every GLB model; `onLoaded` fires per kind (unit or building) so cached procedural defs
 * can be dropped.
 */
export async function loadGlbModels(onLoaded: (kind: UnitKind | BuildingKind) => void, base = ""): Promise<void> {
  const loader = new GLTFLoader();
  const all = [...(Object.entries(GLB_UNITS) as [UnitKind, string][]), ...(Object.entries(GLB_BUILDINGS) as [BuildingKind, string][])];
  await Promise.all(
    all.map(async ([kind, url]) => {
      try {
        const gltf = await loader.loadAsync(base + url);
        const mesh = (name: string) => {
          const o = gltf.scene.getObjectByName(name);
          const m = o && ((o as THREE.Mesh).isMesh ? (o as THREE.Mesh) : (o.children.find((c) => (c as THREE.Mesh).isMesh) as THREE.Mesh | undefined));
          return m?.geometry;
        };
        const hull = mesh("hull");
        if (!hull) throw new Error("no hull node");
        const parts: GlbParts = { hull: toGame(hull) };
        for (const name of ["turret", "ramp", "rotor"] as const) {
          const geometry = mesh(name);
          if (geometry) parts[name] = toGame(geometry);
        }
        loaded.set(kind, parts);
        onLoaded(kind);
      } catch (e) {
        console.warn("glb model failed:", kind, e);
      }
    })
  );
}
