# battledrones-cc

A Command & Conquer look for [simonw/battledrones](https://github.com/simonw/battledrones),
built as six commits on top of `v14` (`ca4f13b`). Only the rendering and the HUD's chrome are
touched. The simulation, the balance, the network protocol and replay determinism are untouched,
and the game's own replay check is the proof: on this tree it still ends on the same world hash
as stock v14.

See [`cc-look/`](cc-look/) for before/after renders at two viewports and what they measure.

## The six commits

| Commit | What it does |
|---|---|
| `ea60140` | flat RTS camera: FOV 12, pitch fixed at 45° |
| `1e7954f` | one hard warm key light: `NoToneMapping`, shadow radius 0, lower ambient, flat materials |
| `0dd5e1a` | no self-lit building faces: 9 faces moved to diffuse amber, point emitters stay |
| `de17db4` | ground: harder tile-edge contrast, narrower border skirt |
| `563fa09` | console: brushed metal on slate, framed RADAR on top, tabs with text labels, counters as instrument windows, Rajdhani 5.3.0 |
| `608b659` | green corner brackets around a multi-selection |

To put the look on your own v14 checkout: `git cherry-pick ea60140..608b659`.

## What does not change (measured on this tree, 25 Nov 2026)

| Check | Result |
|---|---|
| `npx vite-node tools/check-record.ts battles/showcase/2026-10-11-riverlands-42-gpt-6-luna-vs-gpt-6-luna.json` | `RECORD OK (riverlands, skirmish, 125 turns, 27 hashes through tick 2716, final fb0e5718)` — the same final hash stock v14 produces |
| `npm test` | vitest: 79 files, **1568 passed, 0 failed**. The trailing `node --test tools/pages-archive.test.mjs` needs the `zip` binary; on a host without it all 4 fail with `spawnSync zip ENOENT`, with `zip` installed they pass 4/4 |
| `npm run build` | exit 0, 273 files, 21,953,603 bytes in `dist/`; `grep -c rajdhani dist/sw.js` = 0 (the font is not in the precache, defect 1 below) |
| `git diff --name-only ca4f13b..HEAD -- src/sim/` | empty — no simulation file is in the six commits |
| `art/`, `public/assets/` | no diff — no generated art, no new image bytes |

## Known defects we did not fix

1. **The self-hosted font is not in the PWA precache.** `vite.config.ts` `globPatterns` does not
   cover `*.woff2`, so a first cold start without network falls back to a system font and the
   console chrome loses its typographic character. One line would fix it; it is not fixed here.
2. **The call-down rail overlaps the widened build bar** by 22 × 52 px per button at a 390 px
   viewport. Cosmetic, but it is visible.
3. **The ground is desaturated, not re-hued.** Measured on the ground crop: saturation −41 %,
   value −16 %, hue +1.4°. "Olive-steel" was the target; what shipped is a greyer version of the
   same hue.

## Two things worth knowing before you copy the look

- Our key-light commit sets `renderer.toneMapping = THREE.NoToneMapping`, which also makes the
  game's per-biome `LOOKS.exposure` values inert — `renderer.toneMappingExposure` is written at
  `src/game/three/stage.ts:207` but only has an effect inside tone mapping. Upstream shipped
  `NeutralToneMapping`; the look commit overrode it to get a flatter, harder image. If you want
  the biome exposure dial back, you have to pick tone mapping or the flat look.
- The HUD tabs are labelled with words here. In the original games the tab labels live in
  tooltips only; this is a deliberate usability change, not a restoration.

## Running it

```
npm ci
npm run dev      # http://localhost:5173
npm test         # vitest + the pages-archive test
npm run build    # tsc --noEmit && vite build
```

## Licence and assets

Upstream's code and history are unchanged and stay under the licence the repository ships —
Apache-2.0, verbatim in `LICENSE` (note that upstream's copyright line is still the unfilled
`Copyright [yyyy] [name of copyright owner]` placeholder). Our six commits are additions and
modifications to upstream files, stated here as Apache-2.0 §4(b) requires.

The UI font is Rajdhani 5.3.0 from `@fontsource/rajdhani`, SIL Open Font License 1.1, self-hosted
— no Google Fonts request at runtime. No Westwood/EA art, fonts, icons or sounds are used or
imitated with extracted assets: the console is drawn by our own CSS and the meshes are the
game's existing generated geometry. Screenshots in `cc-look/` were rendered by us.

This repository is not affiliated with, and does not speak for, Electronic Arts or Westwood
Studios. Command & Conquer and Red Alert are their trademarks; the word "look" above means a
layout grammar and a value structure, nothing more.

## Upstream showcase replays

The replay links below point at upstream's hosted game at the version each record was made on; `tests/arena.test.ts` checks them.

| Match | Map | Result | Replay | Record |
|---|---|---|---|---|
| GPT-6 Luna vs GPT-6 Luna | Riverlands | Blue at 4:31 | [▶ Watch the replay](https://simonw.github.io/battledrones/v11/?replay=battles/showcase/2026-10-11-riverlands-42-gpt-6-luna-vs-gpt-6-luna.json) | [Read the record](https://simonw.github.io/battledrones/record-viewer.html?replay=battles/showcase/2026-10-11-riverlands-42-gpt-6-luna-vs-gpt-6-luna.json) |
| GPT-6 Luna (Blitz) vs GPT-6 Luna (Industry) | Dune Sea | Blue at 7:52 | [▶ Watch the replay](https://simonw.github.io/battledrones/v11/?replay=battles/showcase/2026-10-11-dune-sea-7-gpt-6-luna-vs-gpt-6-luna.json) | [Read the record](https://simonw.github.io/battledrones/record-viewer.html?replay=battles/showcase/2026-10-11-dune-sea-7-gpt-6-luna-vs-gpt-6-luna.json) |
| GPT-6 Luna vs GPT-6 Astra | Riverlands | Red (Astra) at 7:50 | [▶ Watch the replay](https://simonw.github.io/battledrones/v11/?replay=battles/showcase/2026-10-11-riverlands-42-gpt-6-luna-vs-gpt-6-astra.json) | [Read the record](https://simonw.github.io/battledrones/record-viewer.html?replay=battles/showcase/2026-10-11-riverlands-42-gpt-6-luna-vs-gpt-6-astra.json) |
| GPT-5.6 Sol vs GPT-6.1 Sol | Archipelago | Red (GPT-6.1 Sol) at 11:45 | [▶ Watch the replay](https://simonw.github.io/battledrones/v11/?replay=battles/showcase/2026-10-11-archipelago-42-gpt-5.6-sol-vs-gpt-6.1-sol.json) | [Read the record](https://simonw.github.io/battledrones/record-viewer.html?replay=battles/showcase/2026-10-11-archipelago-42-gpt-5.6-sol-vs-gpt-6.1-sol.json) |
| GPT-6 Astra vs Gemini 4 Argon | Riverlands | Blue (Astra) at 5:35 | [▶ Watch the replay](https://simonw.github.io/battledrones/v11/?replay=battles/showcase/2026-10-14-riverlands-42-gpt-6-astra-vs-gemini-4-argon.json) | [Read the record](https://simonw.github.io/battledrones/record-viewer.html?replay=battles/showcase/2026-10-14-riverlands-42-gpt-6-astra-vs-gemini-4-argon.json) |
| Claude Opus 5.5 vs Gemini 4 Argon | Archipelago | Blue (Opus) at 4:12 | [▶ Watch the replay](https://simonw.github.io/battledrones/v11/?replay=battles/showcase/2026-10-14-archipelago-42-claude-opus-5.5-vs-gemini-4-argon.json) | [Read the record](https://simonw.github.io/battledrones/record-viewer.html?replay=battles/showcase/2026-10-14-archipelago-42-claude-opus-5.5-vs-gemini-4-argon.json) |
| Claude Opus 5.5 vs GPT-6 Astra | Archipelago (Goliath Armada) | Red (Astra) at 4:41 | [▶ Watch the replay](https://simonw.github.io/battledrones/v11/?replay=battles/showcase/2026-10-14-archipelago-42-claude-opus-5.5-vs-gpt-6-astra-2.json) | [Read the record](https://simonw.github.io/battledrones/record-viewer.html?replay=battles/showcase/2026-10-14-archipelago-42-claude-opus-5.5-vs-gpt-6-astra-2.json) |
| Claude Opus 5.5 vs GPT-6 Astra | Frostbite | Red (Astra) at 4:14 | [▶ Watch the replay](https://simonw.github.io/battledrones/v11/?replay=battles/showcase/2026-10-14-frostbite-42-claude-opus-5.5-vs-gpt-6-astra.json) | [Read the record](https://simonw.github.io/battledrones/record-viewer.html?replay=battles/showcase/2026-10-14-frostbite-42-claude-opus-5.5-vs-gpt-6-astra.json) |
| Claude Haiku 5.5 vs GPT-6 Luna | Frostbite | Blue (Haiku) at 7:48 | [▶ Watch the replay](https://simonw.github.io/battledrones/v11/?replay=battles/showcase/2026-10-14-frostbite-42-claude-haiku-5.5-vs-gpt-6-luna.json) | [Read the record](https://simonw.github.io/battledrones/record-viewer.html?replay=battles/showcase/2026-10-14-frostbite-42-claude-haiku-5.5-vs-gpt-6-luna.json) |
