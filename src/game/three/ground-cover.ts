import * as THREE from "three";
import type { Biome } from "../../sim/types";
import { fogged } from "./materials";
import { prng } from "./terrain-props";

const COVER: Record<Biome, [number, number]> = {
  temperate: [0x43502d, 0xa2ab5d],
  tropical: [0x3f5b2f, 0xa8bb70],
  desert: [0x75623e, 0xcbb580],
  arctic: [0x73796a, 0xc1c6b7],
  volcanic: [0x514638, 0x9b8663]
};

/** Low dry clumps and taller bank reeds. Each is rendered as an instance. */
export function coverGeos(biome: Biome): THREE.BufferGeometry[] {
  const base = new THREE.Color(COVER[biome][0]);
  const tip = new THREE.Color(COVER[biome][1]);
  return [false, true].map((reeds) => {
    const rnd = prng(reeds ? 19 : 32);
    const positions: number[] = [];
    const colors: number[] = [];
    const color = new THREE.Color();
    const vertex = (x: number, y: number, z: number, light: number) => {
      positions.push(x, y, z);
      color.copy(base).lerp(tip, light);
      colors.push(color.r, color.g, color.b);
    };
    for (let i = 0; i < (reeds ? 7 : 9); i++) {
      const angle = rnd() * Math.PI * 2;
      const dx = Math.cos(angle), dz = Math.sin(angle);
      const x = (rnd() - 0.5) * 0.16, z = (rnd() - 0.5) * 0.16;
      const h = (reeds ? 0.18 : 0.10) + rnd() * (reeds ? 0.11 : 0.09);
      const bend = (reeds ? 0.07 : 0.105) * (0.55 + 0.45 * rnd());
      const width = 0.016 + rnd() * 0.013;
      const warm = 0.75 + rnd() * 0.24;
      const blade = (level: number, side: number) => {
        const bx = x + dx * bend * level * level;
        const bz = z + dz * bend * level * level;
        const band = side * width * (1 - level * 0.7);
        vertex(bx - dz * band, level * h, bz + dx * band, level * warm);
      };
      blade(0, -1); blade(0, 1); blade(0.61, -1);
      blade(0.61, -1); blade(0, 1); blade(0.61, 1);
      blade(0.61, -1); blade(0.61, 1); blade(1, 0);
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
    g.setAttribute("color", new THREE.Float32BufferAttribute(colors, 3));
    g.computeVertexNormals();
    g.computeBoundingSphere();
    return g;
  });
}

let shared: THREE.MeshLambertMaterial | undefined;

/** Thin plants sway under the same clock and fog as the rest of the landscape. */
export function groundCoverMat(): THREE.MeshLambertMaterial {
  return (shared ??= fogged(new THREE.MeshLambertMaterial({ vertexColors: true, side: THREE.DoubleSide }), {
    key: "ground-cover",
    also: (s) => {
      s.vertexShader = s.vertexShader
        .replace("#include <common>", "#include <common>\nuniform float uTime;")
        .replace("#include <begin_vertex>", /* glsl */ `#include <begin_vertex>
        #ifdef USE_INSTANCING
          vec2 root = instanceMatrix[ 3 ].xz;
          float bend = position.y * position.y * 0.62;
          float wave = sin( dot( root, vec2( 0.47, 0.32 ) ) + uTime * 1.65 );
          transformed.xz += vec2( 0.82, 0.55 ) * bend * wave;
        #endif`);
    }
  }));
}
