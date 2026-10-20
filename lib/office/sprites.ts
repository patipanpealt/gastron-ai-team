// Loading the art and putting a character together from its layers.
//
// A character is a stack of aligned sheets (see public/assets/character): hair-back, body, bottom, top, face, hair.
// Hair and clothes are recoloured when a sheet is loaded by swapping the ramp the sheet was drawn with for a ramp
// built from the chosen colour.
import { useSyncExternalStore } from "react";
import { type Appearance, BOTTOM_MAIN, TOP_MAIN } from "./appearance";
import { makeRamp, remapColors } from "./palette";

const BASE = "/assets";

export type Dir = "S" | "N" | "W" | "E";
export type Anim = "idle" | "walk" | "sit" | "talk" | "wave";

interface CharMeta {
  frame: [number, number];
  animations: Record<string, { msPerFrame: number; loop: boolean; directions: Record<string, { row: number; frames: { x: number; y: number; w: number; h: number }[] }> }>;
}
interface Palettes {
  hair: { black: string[] };
  garments: Record<string, string[]>;
}

export const CELL_W = 16;
export const CELL_H = 32;

let version = 0;
const listeners = new Set<() => void>();
const bump = () => {
  version++;
  listeners.forEach((l) => l());
};
export const subscribeAssets = (cb: () => void) => {
  listeners.add(cb);
  return () => listeners.delete(cb);
};
/** Re-renders a component whenever more art has finished loading. */
export function useAssetsVersion() {
  return useSyncExternalStore(subscribeAssets, () => version, () => 0);
}

const images = new Map<string, HTMLImageElement | "loading" | "error">();
function image(url: string): HTMLImageElement | null {
  const cur = images.get(url);
  if (cur && cur !== "loading" && cur !== "error") return cur;
  if (!cur && typeof window !== "undefined") {
    images.set(url, "loading");
    const img = new Image();
    img.onload = () => {
      images.set(url, img);
      bump();
    };
    img.onerror = () => images.set(url, "error");
    img.src = url;
  }
  return null;
}

export const furnitureImage = (name: string) => image(`${BASE}/furniture/${name}.png`);

let meta: CharMeta | null = null;
let palettes: Palettes | null = null;
let metaRequested = false;
function ensureMeta() {
  if (metaRequested || typeof window === "undefined") return;
  metaRequested = true;
  void Promise.all([fetch(`${BASE}/character/character16.json`).then((r) => r.json()), fetch(`${BASE}/character/palettes.json`).then((r) => r.json())])
    .then(([m, p]) => {
      meta = m as CharMeta;
      palettes = p as Palettes;
      bump();
    })
    .catch(() => (metaRequested = false));
}

export function animInfo(anim: Anim) {
  ensureMeta();
  const a = meta?.animations[anim];
  if (!a) return null;
  return { msPerFrame: a.msPerFrame, loop: a.loop, frames: a.directions.S.frames.length };
}

const recolored = new Map<string, HTMLCanvasElement>();
/** A sheet, optionally recoloured (`to` replaces the ramp `from`). Returns null while it is still loading. */
function sheet(name: string, recolor?: { from: string[]; to: string[]; key: string }): CanvasImageSource | null {
  const img = image(`${BASE}/character/${name}.png`);
  if (!img) return null;
  if (!recolor) return img;
  const k = `${name}|${recolor.key}`;
  let c = recolored.get(k);
  if (!c) {
    c = remapColors(img, recolor.from, recolor.to);
    recolored.set(k, c);
  }
  return c;
}

const frames = new Map<string, HTMLCanvasElement>();

export function appearanceKey(ap: Appearance) {
  return [ap.skin, ap.hairStyle, ap.hairColor, ap.top, ap.topColor, ap.top === "dress" ? "-" : ap.bottom, ap.top === "dress" ? "-" : ap.bottomColor].join("|");
}

/** One 16x32 frame of a dressed character, or null while the art is still loading. */
export function characterFrame(ap: Appearance, anim: Anim, dir: Dir, frame: number): HTMLCanvasElement | null {
  ensureMeta();
  if (!meta || !palettes) return null;
  const dirs = meta.animations[anim]?.directions[dir];
  if (!dirs) return null;
  const n = dirs.frames.length;
  const fi = ((Math.floor(frame) % n) + n) % n; // always a valid frame, even for a negative or fractional count
  const fr = dirs.frames[fi];
  const key = `${appearanceKey(ap)}#${anim}#${dir}#${fi}`;
  const hit = frames.get(key);
  if (hit) return hit;

  const hairRecolor = ap.hairColor ? { from: palettes.hair.black, to: makeRamp(ap.hairColor, "hair"), key: ap.hairColor } : undefined;
  const topRecolor = ap.topColor ? { from: palettes.garments[TOP_MAIN[ap.top]], to: makeRamp(ap.topColor, "garment"), key: ap.topColor } : undefined;
  const botRecolor = ap.bottomColor ? { from: palettes.garments[BOTTOM_MAIN[ap.bottom]], to: makeRamp(ap.bottomColor, "garment"), key: ap.bottomColor } : undefined;

  const hair = ap.hairStyle !== "none" ? ap.hairStyle : null;
  const layers: (CanvasImageSource | null)[] = [
    hair ? sheet(`hair_${hair}_back`, hairRecolor) : undefined,
    sheet(`body_${ap.skin}`),
    ap.top !== "dress" ? sheet(`bottom_${ap.bottom}`, botRecolor) : undefined,
    sheet(`top_${ap.top}`, topRecolor),
    sheet("face"),
    hair ? sheet(`hair_${hair}`, hairRecolor) : undefined,
  ].filter((l) => l !== undefined) as (CanvasImageSource | null)[];
  if (layers.some((l) => l === null)) return null; // something is still loading; try again next frame

  const c = document.createElement("canvas");
  c.width = CELL_W;
  c.height = CELL_H;
  const ctx = c.getContext("2d")!;
  for (const l of layers) ctx.drawImage(l!, fr.x, fr.y, CELL_W, CELL_H, 0, 0, CELL_W, CELL_H);
  frames.set(key, c);
  return c;
}

/** Draw a frame scaled up with hard pixels. (x, y) is the top-left corner. */
export function drawFrame(ctx: CanvasRenderingContext2D, frame: HTMLCanvasElement, x: number, y: number, scale: number) {
  ctx.imageSmoothingEnabled = false;
  ctx.drawImage(frame, Math.round(x), Math.round(y), CELL_W * scale, CELL_H * scale);
}
