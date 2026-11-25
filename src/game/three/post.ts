import * as THREE from "three";
import { EffectComposer } from "three/examples/jsm/postprocessing/EffectComposer.js";
import { RenderPass } from "three/examples/jsm/postprocessing/RenderPass.js";
import { SMAAPass } from "three/examples/jsm/postprocessing/SMAAPass.js";
import { OutputPass } from "three/examples/jsm/postprocessing/OutputPass.js";

/**
 * Optional post-processing (?post=1): the scene renders to a linear target, SMAA smooths the
 * edges, and OutputPass applies the tone mapping (ACES) and the sRGB encode. Off by default: the
 * plain renderer path is unchanged. The fog-of-war shader works in display space, so with post on
 * it converts to sRGB around its maths and back (materials.ts fragCode).
 */
export const POST = typeof location !== "undefined" && new URLSearchParams(location.search).get("post") === "1";

export class PostFx {
  private composer: EffectComposer;

  constructor(renderer: THREE.WebGLRenderer, scene: THREE.Scene, camera: THREE.Camera) {
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.composer = new EffectComposer(renderer);
    this.composer.addPass(new RenderPass(scene, camera));
    this.composer.addPass(new SMAAPass()); // linear: must run before OutputPass
    this.composer.addPass(new OutputPass());
  }

  setSize(w: number, h: number, ratio: number): void {
    this.composer.setPixelRatio(ratio);
    this.composer.setSize(w, h);
  }

  render(): void {
    this.composer.render();
  }
}
