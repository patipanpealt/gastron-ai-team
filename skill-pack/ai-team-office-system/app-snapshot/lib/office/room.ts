// The office layout: what is placed where, the default layout, and the geometry helpers the engine and the room
// editor share (footprints, collision, seats).
import { AGENTS, type AgentId } from "../agents";
import {
  FLOORS,
  ITEM_BY_TYPE,
  type FloorId,
  type ItemDef,
  OBJECT_SCALE,
  PARTITION_STYLES,
  PLAQUE_SIZES,
  PLAQUE_STYLES,
  type PlaqueSize,
  ROT_ORDER,
  type Rot,
  SPRITES,
  TILE,
  WALL_H,
} from "./catalog";

export interface PlacedItem {
  id: string;
  type: string;
  /** Floor items: tile column / row of the top-left footprint cell. */
  col: number;
  row: number;
  rot: Rot;
  /** Workstations: who sits here. */
  agent?: AgentId;
  /** Rugs and partitions: colour. */
  color?: string;
  /** Partitions: length in tiles. */
  len?: number;
  /** Partitions: solid / glass / slat. Plaques: wood / brass / navy ... */
  style?: string;
  /** Plaques: the text on the sign. */
  text?: string;
  /** Plaques: size. */
  size?: PlaqueSize;
  /** Doors: open (agents can walk through the gap) or closed. */
  open?: boolean;
  /** Wall items hung on a partition instead of the back wall: the partition's id. */
  mount?: string;
  /** Wall items: position in pixels from the top-left of the canvas. */
  x?: number;
  y?: number;
}

export interface RoomLayout {
  /** Layout version: 2 = objects drawn at 1.5x (older saves used a different scale and are replaced by the default); 3 = chairs face the right way. */
  v: 3;
  cols: number;
  rows: number;
  floor: FloorId;
  floorTint: string | null;
  wallTint: string | null;
  items: PlacedItem[];
}

export const MIN_COLS = 18;
export const MAX_COLS = 40;
export const MIN_ROWS = 12;
export const MAX_ROWS = 30;

export const roomSize = (r: Pick<RoomLayout, "cols" | "rows">) => ({ w: r.cols * TILE, h: WALL_H + r.rows * TILE });

let counter = 0;
export const newId = () => `i${Date.now().toString(36)}${(counter++).toString(36)}${Math.floor(Math.random() * 1296).toString(36)}`;

export function defOf(item: PlacedItem): ItemDef {
  return ITEM_BY_TYPE[item.type];
}

export function normRot(def: ItemDef, rot: Rot): Rot {
  return def.rots.includes(rot) ? rot : def.rots[0];
}

export function nextRot(def: ItemDef, rot: Rot): Rot {
  const list = def.rots.length === 2 ? def.rots : ROT_ORDER.filter((r) => def.rots.includes(r));
  return list[(list.indexOf(normRot(def, rot)) + 1) % list.length];
}

/** Default y (px) of a wall item. */
export const wallY = (def: ItemDef) => Math.round((def.wallY ?? 0) * OBJECT_SCALE);

/** Footprint (cols, rows) of a floor item as placed — the 1x footprint grown with the object scale. */
export function footprint(item: PlacedItem): [number, number] {
  const def = defOf(item);
  const rot = normRot(def, item.rot);
  if (def.workstation) return stationGeo(rot).fp;
  if (def.proc === "partition") return rot === "S" ? [partLen(item), 1] : [1, partLen(item)];
  if (def.kind === "top") return [1, 1];
  const [w, h] = def.variant(rot).fp;
  return [Math.ceil(w * OBJECT_SCALE - 1e-6), Math.ceil(h * OBJECT_SCALE - 1e-6)];
}

export function cellsOf(item: PlacedItem): [number, number][] {
  const [w, h] = footprint(item);
  const out: [number, number][] = [];
  for (let r = 0; r < h; r++) for (let c = 0; c < w; c++) out.push([item.col + c, item.row + r]);
  return out;
}

// ---- partitions & wall items -----------------------------------------------------------------------------

export interface Rect {
  x: number;
  y: number;
  w: number;
  h: number;
}

/** A partition panel is a thin wall standing on the floor: tall, drawn in the same 3/4 view as the furniture. */
export const PART_H = 84; // height of the front face
export const PART_TOP = 12; // visible depth of the top edge (horizontal panels)
export const PART_SIDE = 14; // thickness of a vertical panel

// a doorway is 1 or 2 tiles wide (new ones are 2; ones placed before kept their 1)
export const partLen = (item: PlacedItem) =>
  defOf(item)?.doorway ? (item.len === 1 ? 1 : 2) : Math.min(16, Math.max(1, Math.round(item.len ?? 4)));

export interface PartGeo {
  horizontal: boolean;
  /** Front face — the area wall items can be hung on (horizontal panels only). */
  face: Rect | null;
  /** Everything that is visible (face + top edge). */
  body: Rect;
  /** Where the panel meets the floor (for the south edge). */
  base: number;
}

export function partitionGeo(item: PlacedItem): PartGeo {
  const def = defOf(item);
  const horizontal = normRot(def, item.rot) === "S";
  const len = partLen(item);
  const x0 = item.col * TILE;
  const y0 = WALL_H + item.row * TILE;
  if (horizontal) {
    const w = len * TILE;
    const base = y0 + TILE - 4;
    const face = { x: x0, y: base - PART_H, w, h: PART_H };
    return { horizontal, face, body: { x: x0, y: face.y - PART_TOP, w, h: PART_H + PART_TOP }, base };
  }
  const xL = x0 + (TILE - PART_SIDE) / 2;
  const Y0 = y0 + 4;
  const Y1 = y0 + len * TILE - 4;
  return { horizontal, face: null, body: { x: xL, y: Y0 - PART_H, w: PART_SIDE, h: Y1 - Y0 + PART_H }, base: Y1 };
}

/** Size (world px) of a wall item: a sprite drawn at the object scale, or a plaque in its chosen size. */
export function wallSize(item: PlacedItem): { w: number; h: number } {
  const def = defOf(item);
  if (def.proc === "plaque") {
    const z = PLAQUE_SIZES.find((q) => q.id === (item.size ?? "s")) ?? PLAQUE_SIZES[1];
    return { w: z.w, h: z.h };
  }
  if (def.proc === "door" && item.mount) return { w: TILE, h: DOOR_H }; // a door in a partition fills exactly one tile of it
  const m = SPRITES[def.variant("S").sprite];
  return { w: m.w * OBJECT_SCALE, h: m.h * OBJECT_SCALE };
}

/** Height of a door set into a partition. */
export const DOOR_H = 72;

/** The tile column of a partition that a door is set into (null if it is not on a horizontal partition). */
export function doorCell(room: RoomLayout, door: PlacedItem): { host: PlacedItem; col: number } | null {
  const host = door.mount ? room.items.find((o) => o.id === door.mount) : undefined;
  if (!host || defOf(host)?.proc !== "partition") return null;
  const face = partitionGeo(host).face;
  if (!face) return null;
  return { host, col: host.col + Math.floor(((door.x ?? 0) + TILE / 2 - face.x) / TILE) };
}

export const childrenOf = (room: RoomLayout, id: string) => room.items.filter((i) => i.mount === id);

const inset = (r: Rect, d: number): Rect => ({ x: r.x + d, y: r.y + d, w: r.w - 2 * d, h: r.h - 2 * d });
const within = (r: Rect, box: Rect) => r.x >= box.x && r.y >= box.y && r.x + r.w <= box.x + box.w && r.y + r.h <= box.y + box.h;

/**
 * Replace one item, carrying along whatever is hung on it when it is a partition (moved, lengthened, shortened).
 * Items that no longer fit on the panel are dropped; `dropped` says how many.
 */
export function withItemUpdated(room: RoomLayout, next: PlacedItem): { room: RoomLayout; dropped: number } {
  const old = room.items.find((i) => i.id === next.id);
  let items = room.items.map((i) => (i.id === next.id ? next : i));
  let dropped = 0;
  if (old && defOf(next)?.proc === "partition") {
    const og = partitionGeo(old);
    const ng = partitionGeo(next);
    items = items.flatMap((i) => {
      if (i.mount !== next.id) return [i];
      if (!og.face || !ng.face) {
        dropped++;
        return [];
      }
      const moved = { ...i, x: (i.x ?? 0) + (ng.face.x - og.face.x), y: (i.y ?? 0) + (ng.face.y - og.face.y) };
      const { w, h } = wallSize(moved);
      if (within({ x: moved.x ?? 0, y: moved.y ?? 0, w, h }, defOf(moved).proc === "door" ? ng.face : inset(ng.face, 4))) return [moved];
      dropped++;
      return [];
    });
  }
  return { room: { ...room, items }, dropped };
}

/** Remove an item (and, for a partition, everything hung on it). */
export function withItemRemoved(room: RoomLayout, id: string): RoomLayout {
  return { ...room, items: room.items.filter((i) => i.id !== id && i.mount !== id) };
}

// ---- workstations -------------------------------------------------------------------------------------------

export interface StationGeo {
  fp: [number, number];
  /** Local cell of the chair (walkable). */
  chairCell: [number, number];
  /** Local tile (may be outside the footprint) where an agent stands before sitting down. */
  approach: [number, number];
  chair: { sprite: string; cx: number; bottom: number };
  /** Local pixel rect the desk sprite is fitted into. */
  desk: { sprite: string; x: number; y: number; w: number; h: number };
  /** Local pixel position of the seated agent's feet. */
  seat: { x: number; y: number };
  /** Direction the seated agent faces. */
  facing: Rot;
  order: "desk-last" | "desk-first";
}

const S = OBJECT_SCALE;
const T = TILE * S; // a "1x tile" in world pixels

/** `rot` = the direction the person at this workstation faces. Numbers are the 1x layout multiplied by the object scale. */
export function stationGeo(rot: Rot): StationGeo {
  const fpOf = (w: number, h: number): [number, number] => [Math.ceil(w * S - 1e-6), Math.ceil(h * S - 1e-6)];
  switch (rot) {
    case "S":
      return {
        fp: fpOf(2, 3), chairCell: [1, 0], approach: [1, -1],
        chair: { sprite: "chair_front", cx: 32 * S, bottom: 31 * S + 14 },
        desk: { sprite: "desk_back", x: 0, y: T, w: 2 * T, h: 2 * T },
        seat: { x: 32 * S, y: 30 * S }, facing: "S", order: "desk-last",
      };
    case "N":
      return {
        fp: fpOf(2, 3), chairCell: [1, 3], approach: [1, 5],
        chair: { sprite: "chair_back", cx: 32 * S, bottom: 95 * S },
        desk: { sprite: "desk_front", x: 0, y: 0, w: 2 * T, h: 2 * T },
        seat: { x: 32 * S, y: 102 }, facing: "N", order: "desk-first",
      };
    case "E":
      return {
        fp: fpOf(2, 2), chairCell: [0, 1], approach: [-1, 1],
        chair: { sprite: "chair_right", cx: 16 * S, bottom: 50 * S },
        desk: { sprite: "desk_left", x: T, y: 0, w: T, h: 2 * T },
        seat: { x: 14 * S, y: 46 * S - 12 }, facing: "E", order: "desk-last",
      };
    default:
      return {
        fp: fpOf(2, 2), chairCell: [2, 1], approach: [3, 1],
        chair: { sprite: "chair_left", cx: 48 * S, bottom: 50 * S },
        desk: { sprite: "desk_right", x: 0, y: 0, w: T, h: 2 * T },
        seat: { x: 50 * S, y: 46 * S - 12 }, facing: "W", order: "desk-last",
      };
  }
}

export interface SeatInfo {
  itemId: string;
  /** Tile to stand on before sitting. */
  approach: { col: number; row: number };
  /** World pixel position of the seated agent's feet. */
  x: number;
  y: number;
  facing: Rot;
}

export function seatOf(item: PlacedItem): SeatInfo {
  const g = stationGeo(normRot(defOf(item), item.rot));
  return {
    itemId: item.id,
    approach: { col: item.col + g.approach[0], row: item.row + g.approach[1] },
    x: item.col * TILE + g.seat.x,
    y: WALL_H + item.row * TILE + g.seat.y,
    facing: g.facing,
  };
}

/** Cells that block walking for this item. */
export function blockingCells(item: PlacedItem): [number, number][] {
  const def = defOf(item);
  if (!def.block) return [];
  const cells = cellsOf(item);
  if (def.workstation) {
    const g = stationGeo(normRot(def, item.rot));
    return cells.filter(([c, r]) => !(c === item.col + g.chairCell[0] && r === item.row + g.chairCell[1]));
  }
  return cells;
}

export function blockedGrid(room: RoomLayout): boolean[][] {
  const g = Array.from({ length: room.rows }, () => Array<boolean>(room.cols).fill(false));
  for (const it of room.items) {
    for (const [c, r] of blockingCells(it)) if (r >= 0 && r < room.rows && c >= 0 && c < room.cols) g[r][c] = true;
  }
  // a door lets agents through the tile of the panel it is set into (it opens by itself when someone arrives)
  for (const it of room.items) {
    if (defOf(it)?.doorway) for (const [c, r] of cellsOf(it)) if (r >= 0 && r < room.rows && c >= 0 && c < room.cols) g[r][c] = false;
  }
  for (const it of room.items) {
    if (defOf(it)?.proc !== "door") continue; // doors in a partition are automatic: agents open them as they walk through
    const cell = doorCell(room, it);
    if (cell && cell.host.row >= 0 && cell.host.row < room.rows && cell.col >= 0 && cell.col < room.cols) g[cell.host.row][cell.col] = false;
  }
  return g;
}

// ---- sprites ------------------------------------------------------------------------------------------------

export interface DrawOp {
  sprite: string;
  x: number;
  y: number;
  /** Draw scale. */
  s: number;
}

/** Top-left pixel of a (scaled) sprite so its solid body is centred in the rect and rests on its lower edge. */
export function placeSprite(sprite: string, fx: number, fy: number, fw: number, fh: number): DrawOp {
  const m = SPRITES[sprite];
  const [bx0, , bx1, by1] = m.body;
  return { sprite, s: S, x: Math.round(fx + (fw - (bx1 - bx0) * S) / 2 - bx0 * S), y: Math.round(fy + fh - 2 - by1 * S) };
}

export function floorOps(item: PlacedItem): DrawOp[] {
  const def = defOf(item);
  const ox = item.col * TILE;
  const oy = WALL_H + item.row * TILE;
  if (def.workstation) {
    const g = stationGeo(normRot(def, item.rot));
    const chair = SPRITES[g.chair.sprite];
    const cbx = ((chair.body[0] + chair.body[2]) / 2) * S;
    return [
      { sprite: g.chair.sprite, s: S, x: Math.round(ox + g.chair.cx - cbx), y: Math.round(oy + g.chair.bottom - chair.body[3] * S) },
      placeSprite(g.desk.sprite, ox + g.desk.x, oy + g.desk.y, g.desk.w, g.desk.h),
    ];
  }
  const v = def.variant(normRot(def, item.rot));
  if (!v.sprite) return [];
  const [w, h] = footprint(item);
  return [placeSprite(v.sprite, ox, oy, w * TILE, h * TILE)];
}

/** Axis-aligned box (world px) of an item, for picking and the selection outline. */
export function itemRect(item: PlacedItem): { x: number; y: number; w: number; h: number } {
  const def = defOf(item);
  if (def.kind === "wall") {
    const z = wallSize(item);
    return { x: item.x ?? 0, y: item.y ?? wallY(def), w: z.w, h: z.h };
  }
  if (def.proc === "partition") return partitionGeo(item).body;
  const [w, h] = footprint(item);
  let x0 = item.col * TILE;
  let y0 = WALL_H + item.row * TILE;
  let x1 = x0 + w * TILE;
  const y1 = y0 + h * TILE;
  if (def.kind !== "rug") {
    for (const op of floorOps(item)) {
      const m = SPRITES[op.sprite];
      x0 = Math.min(x0, op.x + m.body[0] * op.s);
      x1 = Math.max(x1, op.x + m.body[2] * op.s);
      y0 = Math.min(y0, op.y + m.body[1] * op.s);
    }
  }
  return { x: x0, y: y0, w: x1 - x0, h: y1 - y0 };
}

export function baselineOf(item: PlacedItem): number {
  const def = defOf(item);
  const [, h] = footprint(item);
  const y = WALL_H + (item.row + h) * TILE;
  return def.kind === "top" ? y + 1 : y;
}

// ---- placement rules ----------------------------------------------------------------------------------------

export function canPlace(room: RoomLayout, item: PlacedItem): { ok: boolean; reason?: string } {
  const def = defOf(item);
  if (!def) return { ok: false, reason: "ไม่รู้จักของชิ้นนี้" };
  const others = room.items.filter((o) => o.id !== item.id);
  if (def.kind === "wall") {
    const r = itemRect(item);
    if (item.mount) {
      const host = room.items.find((o) => o.id === item.mount);
      const face = host && defOf(host)?.proc === "partition" ? partitionGeo(host).face : null;
      if (!face) return { ok: false, reason: "แปะได้เฉพาะหน้า partition แนวนอน" };
      if (def.proc === "door") {
        // a door stands on the floor, exactly inside one tile of the panel
        if (!within(r, face) || (r.x - face.x) % TILE !== 0 || r.y + r.h !== face.y + face.h) return { ok: false, reason: "ประตูต้องอยู่ในช่องของแผ่น partition" };
      } else if (!within(r, inset(face, 4))) return { ok: false, reason: "ใหญ่เกินพื้นที่บนแผ่น partition" };
    } else {
      const maxX = room.cols * TILE;
      if (r.x < 0 || r.x + r.w > maxX) return { ok: false, reason: "ติดผนังเกินขอบ" };
    }
    for (const o of others) {
      if (defOf(o).kind !== "wall" || o.mount !== item.mount) continue;
      const q = itemRect(o);
      if (r.x < q.x + q.w && r.x + r.w > q.x && r.y < q.y + q.h && r.y + r.h > q.y) return { ok: false, reason: "ซ้อนกับของบนผนัง" };
    }
    return { ok: true };
  }
  const cells = cellsOf(item);
  for (const [c, r] of cells) if (c < 0 || r < 0 || c >= room.cols || r >= room.rows) return { ok: false, reason: "อยู่นอกห้อง" };
  if (def.kind === "rug") return { ok: true };
  const mine = new Set(blockingCells(item).map(([c, r]) => `${c},${r}`));
  const all = new Set(cells.map(([c, r]) => `${c},${r}`));
  for (const o of others) {
    const od = defOf(o);
    if (od.kind === "wall" || od.kind === "rug") continue;
    if (def.kind === "top") {
      if (od.kind === "top" && cellsOf(o).some(([c, r]) => all.has(`${c},${r}`))) return { ok: false, reason: "มีของวางอยู่แล้ว" };
      continue;
    }
    if (od.kind === "top") continue;
    const theirs = blockingCells(o);
    if (theirs.some(([c, r]) => mine.has(`${c},${r}`))) return { ok: false, reason: "ชนกับของชิ้นอื่น" };
  }
  if (def.workstation) {
    const s = seatOf(item);
    if (s.approach.col < 0 || s.approach.row < 0 || s.approach.col >= room.cols || s.approach.row >= room.rows) {
      return { ok: false, reason: "ต้องมีทางเดินเข้าที่นั่ง" };
    }
  }
  return { ok: true };
}

// ---- default layout -----------------------------------------------------------------------------------------

const ws = (agent: AgentId, col: number, row: number, rot: Rot): PlacedItem => ({ id: `ws-${agent}`, type: "workstation", col, row, rot, agent });
let n = 0;
const mk = (type: string, col: number, row: number, rot: Rot = "S", extra: Partial<PlacedItem> = {}): PlacedItem => ({
  id: `d${n++}`,
  type,
  col,
  row,
  rot,
  ...extra,
});
const wall = (type: string, x: number): PlacedItem => ({ id: `d${n++}`, type, col: 0, row: 0, rot: "S", x, y: wallY(ITEM_BY_TYPE[type]) });

export function defaultRoom(): RoomLayout {
  n = 0;
  const top: AgentId[] = ["strategist", "researcher", "copywriter", "content", "creative"];
  const bottom: AgentId[] = ["social", "ads", "seo", "analyst", "qa"];
  const items: PlacedItem[] = [
    // rugs go first so they sit under everything
    mk("rug_l", 23, 1, "S", { color: "#8c3b4a" }),
    mk("rug_l", 1, 14, "S", { color: "#2f8a84" }),
    mk("rug_xl", 21, 13, "S", { color: "#5b6f8a" }),
    // open plan: two rows of five workstations, 4 tiles apart
    ...top.map((a, i) => ws(a, 1 + i * 4, 1, "S")),
    ...bottom.map((a, i) => ws(a, 1 + i * 4, 7, "N")),
    // director's corner
    ws("director", 25, 1, "S"),
    mk("shelf", 29, 0),
    mk("filing", 22, 0),
    mk("plant_snake", 20, 0),
    mk("plant_big", 30, 6),
    mk("plant_big", 22, 6),
    // meeting area
    mk("meeting", 21, 15, "S"),
    ...[22, 24, 26, 28].map((c) => mk("chair", c, 13, "S")),
    ...[22, 24, 26, 28].map((c) => mk("chair", c, 18, "N")),
    mk("chair", 19, 15, "E"),
    mk("chair", 30, 15, "W"),
    mk("plant_big", 30, 19),
    // lounge
    mk("sofa", 2, 17, "S"),
    mk("plush", 0, 15),
    mk("plant_snake", 0, 19),
    mk("plant_desk", 5, 15),
    // kitchen corner
    mk("fridge", 9, 19),
    mk("cooler", 11, 19),
    mk("bin_office", 13, 19),
    mk("whiteboard", 15, 19, "S"),
    mk("plant_big", 18, 19),
    // back wall
    wall("window", 40),
    wall("window", 160),
    wall("clock", 290),
    wall("window", 340),
    wall("poster_pig", 470),
    wall("wb_wall", 520),
    wall("calendar", 650),
    wall("window", 730),
    wall("window", 850),
    wall("door", 950),
  ];
  return { v: 3, cols: 32, rows: 21, floor: "wood_a", floorTint: null, wallTint: null, items };
}

// ---- loading saved layouts ------------------------------------------------------------------------------------

const HEX = /^#[0-9a-fA-F]{6}$/;
const AGENT_IDS = new Set<string>(AGENTS.map((a) => a.id));

export function sanitizeRoom(raw: unknown): RoomLayout {
  const d = defaultRoom();
  if (!raw || typeof raw !== "object") return d;
  const o = raw as Omit<Partial<RoomLayout>, "v"> & { v?: number };
  if (o.v !== 2 && o.v !== 3) return d; // saved before objects were enlarged: positions no longer fit, start from the new default
  // v2 -> v3: the chairs of the starting layout (ids d<number>) were turned the wrong way round; fix those only
  const migrate = o.v === 2;
  const int = (v: unknown, lo: number, hi: number, dflt: number) => (typeof v === "number" && Number.isFinite(v) ? Math.min(hi, Math.max(lo, Math.round(v))) : dflt);
  const room: RoomLayout = {
    v: 3,
    cols: int(o.cols, MIN_COLS, MAX_COLS, d.cols),
    rows: int(o.rows, MIN_ROWS, MAX_ROWS, d.rows),
    floor: FLOORS.some((f) => f.id === o.floor) ? (o.floor as FloorId) : d.floor,
    floorTint: typeof o.floorTint === "string" && HEX.test(o.floorTint) ? o.floorTint : null,
    wallTint: typeof o.wallTint === "string" && HEX.test(o.wallTint) ? o.wallTint : null,
    items: [],
  };
  if (!Array.isArray(o.items)) return d;
  const seen = new Set<string>();
  const usedAgents = new Set<string>();
  for (const r of o.items as Partial<PlacedItem>[]) {
    if (!r || typeof r.type !== "string" || !ITEM_BY_TYPE[r.type]) continue;
    const def = ITEM_BY_TYPE[r.type];
    const id = typeof r.id === "string" && !seen.has(r.id) ? r.id : newId();
    seen.add(id);
    const item: PlacedItem = {
      id,
      type: r.type,
      col: int(r.col, 0, 99, 0),
      row: int(r.row, 0, 99, 0),
      rot: normRot(def, (ROT_ORDER as string[]).includes(r.rot as string) ? (r.rot as Rot) : "S"),
    };
    if (migrate && r.type === "chair" && /^d\d+$/.test(id) && (item.rot === "S" || item.rot === "N")) item.rot = item.rot === "S" ? "N" : "S";
    if (def.kind === "wall") {
      item.x = int(r.x, 0, 4000, 0);
      item.y = int(r.y, 0, typeof r.mount === "string" ? 4000 : WALL_H, wallY(def)); // things hung on a partition sit lower than the back wall
    }
    if (def.tint) item.color = typeof r.color === "string" && HEX.test(r.color) ? r.color : def.proc === "partition" ? "#e9e4d6" : "#8c3b4a";
    if (def.proc === "partition") {
      item.len = int(r.len, 1, 16, 4);
      item.style = PARTITION_STYLES.some((q) => q.id === r.style) ? r.style : "solid";
    }
    if (def.proc === "plaque") {
      item.text = typeof r.text === "string" ? r.text.slice(0, 40) : "ชื่อทีม";
      item.style = PLAQUE_STYLES.some((q) => q.id === r.style) ? r.style : "wood";
      item.size = PLAQUE_SIZES.some((q) => q.id === r.size) ? r.size : "s";
    }
    if (def.kind === "wall" && typeof r.mount === "string") item.mount = r.mount;
    if (def.proc === "door" && r.open === true) item.open = true;
    if (def.workstation && typeof r.agent === "string" && AGENT_IDS.has(r.agent) && !usedAgents.has(r.agent)) {
      item.agent = r.agent as AgentId;
      usedAgents.add(r.agent);
    }
    room.items.push(item);
  }
  // drop anything that no longer fits (e.g. the room was shrunk); panels first so what hangs on them can be checked
  const base: PlacedItem[] = [];
  for (const item of room.items.filter((i) => !i.mount)) if (canPlace({ ...room, items: base }, item).ok) base.push(item);
  const kept = [...base];
  for (const item of room.items.filter((i) => i.mount)) if (canPlace({ ...room, items: kept }, item).ok) kept.push(item);
  room.items = room.items.filter((i) => kept.includes(i));
  return room;
}
