# Look, before and after

Every image here was rendered by us from this checkout and from upstream `v14` at the same
moment of the same battle, at two viewports. Nothing is retouched.

`before/` is stock v14 (`ca4f13b`), `after/` is this branch. Same map, same seed, same tick.

| Moment | What to look at |
|---|---|
| `start-1440x900` | sidebar, radar frame, tab labels, camera pitch |
| `minute1-1440x900` | units and ground under the single key light, hard shadows |
| `openers-1440x900` | opening build phase, no self-lit building faces |
| `menu-1440x900` | menu, which the look commits deliberately leave almost alone |
| `*-390x844` | the same four on a phone viewport, to show the console still fits |
| `detail/` | crops: sidebar metal, ground tile edge, call-down rail, map edge |
| `multiselect-1440x900` | green corner brackets around a multi-selection |

## What the pixels measure

Median hue / saturation / value of the whole frame, PIL `ImageStat` on the PNGs above
(H normalized to degrees). Measured 2026-11-25 on these files.

| Frame | before | after | hue | saturation | value |
|---|---|---|---|---|---|
| start 1440x900 | 203.3 / 0.518 / 0.200 | 204.7 / 0.408 / 0.173 | +1.4° | −21.2 % | −13.7 % |
| minute1 1440x900 | 203.3 / 0.529 / 0.216 | 204.7 / 0.400 / 0.165 | +1.4° | −24.4 % | −23.6 % |
| openers 1440x900 | 214.6 / 0.553 / 0.075 | 214.6 / 0.529 / 0.071 | 0.0° | −4.3 % | −5.3 % |
| menu 1440x900 | 210.4 / 0.294 / 0.176 | 210.4 / 0.286 / 0.169 | 0.0° | −2.7 % | −4.4 % |

Crops, where the change is supposed to be:

| Crop | before (H/S/V) | after (H/S/V) | hue | saturation |
|---|---|---|---|---|
| sidebar | 217.4 / 0.541 / 0.110 | 208.9 / 0.310 / 0.118 | −8.5° | −43 % |
| ground | 60.7 / 0.663 / 0.431 | 62.1 / 0.392 / 0.361 | +1.4° | −41 % |
| call-down rail | 217.4 / 0.533 / 0.129 | 208.9 / 0.310 / 0.129 | −8.5° | −42 % |
| map edge | 64.9 / 0.498 / 0.298 | 66.4 / 0.310 / 0.204 | +1.4° | −38 % |

Read the numbers honestly: the console is where the look lives (hue −8.5°, saturation −43 %).
The ground got 41 % less saturation and 16 % less light, but its hue moved 1.4° — the ground is
desaturated, not re-hued to olive-steel. That is listed as an open defect in the top-level
README rather than sold as a style.
