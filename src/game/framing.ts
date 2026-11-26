import { BUILDINGS } from "../sim/balance";
import { predictOpenerSite } from "../sim/openers";
import type { Faction, World } from "../sim/types";
import { hqOf, isResource } from "../sim/world";
import type { CameraRig } from "./three/camera";

/** An axis-aligned box in tile units. */
export interface Box {
  x0: number;
  y0: number;
  x1: number;
  y1: number;
}

/** Screen space (CSS px) covered by HUD along each edge. */
export interface Insets {
  top: number;
  right: number;
  bottom: number;
  left: number;
}

/** Units within this many tiles of the HQ's centre are part of the opening shot. */
const START_UNIT_REACH = 8;

/**
 * Where a side's base is: its HQ's footprint or, with no HQ (Nomads, or the
 * HQ lost), the ground under its first Goliath — the base that walks. Null
 * when it has neither.
 */
export function homeBox(w: World, faction: Faction): Box | null {
  const hq = hqOf(w, faction);
  if (hq) {
    const size = BUILDINGS.hq.size;
    return { x0: hq.tx, y0: hq.ty, x1: hq.tx + size, y1: hq.ty + size };
  }
  let g: { x: number; y: number; id: number } | null = null;
  for (const u of w.units.values()) if (u.goliath && u.faction === faction && (!g || u.id < g.id)) g = u;
  return g ? { x0: g.x - 1, y0: g.y - 1, x1: g.x + 1, y1: g.y + 1 } : null;
}

/**
 * The opening shot: the HQ (or under Nomads the anchored Goliath), its home
 * field, where the opener's factory goes and the units the side starts with
 * (the Trooper Squad on the HQ's far flank), so the player sees their whole
 * start at a glance.
 */
export function startBox(w: World, faction: Faction): Box | null {
  const home = homeBox(w, faction);
  if (!home) return null;
  const box: Box = { ...home };
  const add = (x0: number, y0: number, x1: number, y1: number) => {
    box.x0 = Math.min(box.x0, x0);
    box.y0 = Math.min(box.y0, y0);
    box.x1 = Math.max(box.x1, x1);
    box.y1 = Math.max(box.y1, y1);
  };
  // the nearest field: its closest tile plus the rest of that patch
  const c = { x: (home.x0 + home.x1) / 2, y: (home.y0 + home.y1) / 2 };
  let near: { x: number; y: number } | null = null;
  let nearD = Infinity;
  for (let ty = 0; ty < w.height; ty++)
    for (let tx = 0; tx < w.width; tx++) {
      if (!isResource(w, ty * w.width + tx)) continue;
      const d = Math.hypot(tx + 0.5 - c.x, ty + 0.5 - c.y);
      if (d < nearD) {
        nearD = d;
        near = { x: tx, y: ty };
      }
    }
  if (near && nearD < 16)
    for (let ty = near.y - 3; ty <= near.y + 3; ty++)
      for (let tx = near.x - 3; tx <= near.x + 3; tx++)
        if (tx >= 0 && ty >= 0 && tx < w.width && ty < w.height && isResource(w, ty * w.width + tx))
          add(tx, ty, tx + 1, ty + 1);
  const site = predictOpenerSite(w, faction, "fab-plant");
  if (site) add(site.tx, site.ty, site.tx + 2, site.ty + 2);
  // (a squad's robots stand a little way round its centre)
  for (const u of w.units.values())
    if (u.faction === faction && Math.hypot(u.x - c.x, u.y - c.y) <= START_UNIT_REACH)
      add(u.x - 0.75, u.y - 0.75, u.x + 0.75, u.y + 0.75);
  // breathing room round the edges
  return { x0: box.x0 - 1, y0: box.y0 - 1, x1: box.x1 + 1, y1: box.y1 + 1 };
}

/** Measure how much of the screen the DOM HUD covers on each edge (CSS px). */
function hudInsets(W: number, H: number): Insets {
  const rect = (sel: string) => document.querySelector(sel)?.getBoundingClientRect() ?? null;
  const ins: Insets = { top: 8, right: 8, bottom: 8, left: 8 };
  const landscape = W > H;
  const topWidgets = landscape ? [".tl", ".topbar"] : [".tl", ".topbar", ".minimap-wrap"];
  for (const sel of topWidgets) {
    const r = rect(sel);
    if (r && r.height > 0) ins.top = Math.max(ins.top, r.bottom + 6);
  }
  // the zoom buttons stand over the map at the left edge, where the starting squad waits
  const zoom = rect(".zoombtns");
  if (zoom && zoom.width > 0) ins.left = Math.max(ins.left, zoom.right + 6);
  const bar = rect(".buildbar");
  const dock = rect(".dock");
  if (landscape) {
    if (bar && bar.width > 0) ins.right = Math.max(ins.right, W - bar.left + 6);
  } else if (dock && dock.height > 0) ins.bottom = Math.max(ins.bottom, H - dock.top + 6);
  return ins;
}

/** The rectangle available for camera framing, in CSS px. */
export function hudPlayArea(w: number, h: number): Box {
  const ins = hudInsets(w, h);
  const x0 = Math.min(ins.left, w - 1);
  const y0 = Math.min(ins.top, h - 1);
  return { x0, y0, x1: Math.max(x0 + 1, w - ins.right), y1: Math.max(y0 + 1, h - ins.bottom) };
}

/** Fit a ground box into screen space using the rig's pitch at each candidate zoom. */
export function fitCamera(rig: CameraRig, box: Box, area: Box, maxZoom: number): boolean {
  const previous = { x: rig.x, y: rig.y, zoom: rig.zoom };
  const x = (box.x0 + box.x1) / 2;
  const y = (box.y0 + box.y1) / 2;
  const sx = (area.x0 + area.x1) / 2;
  const sy = (area.y0 + area.y1) / 2;
  const fits = (zoom: number) => {
    rig.zoom = zoom;
    rig.placeAt(x, y, sx, sy);
    for (const px of [box.x0, box.x1]) {
      for (const py of [box.y0, box.y1]) {
        const p = rig.project(px, py);
        if (p.behind || p.x < area.x0 || p.x > area.x1 || p.y < area.y0 || p.y > area.y1) return false;
      }
    }
    return true;
  };
  if (fits(maxZoom)) return true;
  let lo = 0;
  let hi = maxZoom;
  for (let i = 0; i < 16; i++) {
    const zoom = (lo + hi) / 2;
    if (fits(zoom)) lo = zoom;
    else hi = zoom;
  }
  if (lo > 0) return fits(lo);
  rig.zoom = previous.zoom;
  rig.centerOn(previous.x, previous.y);
  return false;
}
