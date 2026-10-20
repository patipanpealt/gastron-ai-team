import { AGENT_BY_ID, AGENTS, type AgentId, type Team } from "../agents";
import type { Profile } from "./appearance";
import { OBJECT_SCALE, PLAQUE_STYLES, type Rot, TILE, WALL_H } from "./catalog";
import {
  baselineOf,
  blockedGrid,
  canPlace,
  childrenOf,
  defOf,
  floorOps,
  footprint,
  itemRect,
  newId,
  normRot,
  DOOR_H,
  PART_H,
  PART_TOP,
  partitionGeo,
  type PlacedItem,
  type RoomLayout,
  roomSize,
  wallSize,
  wallY,
  withItemUpdated,
  seatOf,
  type SeatInfo,
} from "./room";
import { type Anim, animInfo, CELL_H, CELL_W, characterFrame, type Dir, drawFrame, furnitureImage } from "./sprites";

export type BubbleKind = "think" | "work" | "talk" | "wait" | "done" | "error";

interface Bubble {
  text: string;
  kind: BubbleKind;
  until: number | null;
}

interface Pt {
  x: number;
  y: number;
}
interface Tile {
  c: number;
  r: number;
}

interface Actor {
  id: AgentId;
  x: number;
  y: number;
  dir: Dir;
  /** Direction to face once the current walk ends. */
  facing: Dir;
  path: Pt[];
  arrive: (() => void) | null;
  /** Sitting at the workstation. */
  seated: boolean;
  working: boolean;
  busy: boolean;
  bubble: Bubble | null;
  animT: number;
  nextWander: number;
}

interface FlyingDoc {
  fx: number;
  fy: number;
  tx: number;
  ty: number;
  start: number;
  dur: number;
  done: () => void;
}

interface Link {
  from: AgentId;
  to: AgentId;
  label: string;
  start: number;
  until: number;
}

export interface EditState {
  active: boolean;
  /** An item picked from the catalog that follows the pointer until it is dropped. */
  placing: { type: string; rot: Rot; color?: string; /** Extra fields for the new item (partition length, plaque text ...). */ props?: Partial<PlacedItem> } | null;
  selectedId: string | null;
}

const CHAR_SCALE = 2; // characters are drawn at 2x (a 16x32 cell becomes 32x64, one tile wide)
const FEET_Y = 30 * CHAR_SCALE;
const SPEED = 72; // px per second
const TEAM_COLOR: Record<Team, string> = { lead: "#ffb347", creative: "#ff6f91", growth: "#5fb8ff", data: "#b892ff" };
const BUBBLE_EDGE: Record<BubbleKind, string> = { think: "#111111", work: "#111111", talk: "#111111", wait: "#555555", done: "#1f7a3a", error: "#c0392b" };

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));
const center = (t: Tile): Pt => ({ x: t.c * TILE + TILE / 2, y: WALL_H + t.r * TILE + 27 });
const appr = (s: SeatInfo): Tile => ({ c: s.approach.col, r: s.approach.row });
const dirFromVec = (dx: number, dy: number): Dir => (Math.abs(dx) > Math.abs(dy) ? (dx > 0 ? "E" : "W") : dy > 0 ? "S" : "N");

function shade(hex: string, amt: number) {
  const n = parseInt(hex.slice(1), 16);
  const f = (v: number) => Math.round(amt >= 0 ? v + (255 - v) * amt : v * (1 + amt));
  return `rgb(${f(n >> 16)},${f((n >> 8) & 255)},${f(n & 255)})`;
}

export class OfficeEngine {
  private ctx: CanvasRenderingContext2D;
  private world: HTMLCanvasElement;
  private wctx: CanvasRenderingContext2D;
  private bg: HTMLCanvasElement | null = null;
  private bgKey = "";
  private actors = new Map<AgentId, Actor>();
  private docs: FlyingDoc[] = [];
  private links: Link[] = [];
  private room: RoomLayout;
  private profiles: Record<AgentId, Profile>;
  private blocked: boolean[][] = [];
  private seats = new Map<AgentId, SeatInfo>();
  private raf = 0;
  private last = 0;
  private scale = 1;
  private dpr = 1;
  private cssWidth = 0;
  private W = 0;
  private H = 0;

  selected: AgentId | null = null;
  wanderEnabled = true;

  // ---- editor state & callbacks (set by the React side)
  edit: EditState = { active: false, placing: null, selectedId: null };
  onSelectAgent: (id: AgentId | null) => void = () => {};
  onRoomChange: (room: RoomLayout, selectId?: string | null) => void = () => {};
  onEditSelect: (id: string | null) => void = () => {};
  onPlaceCancel: () => void = () => {};
  private pointer: Pt | null = null;
  private drag: { id: string; dx: number; dy: number; moved: boolean; cur: PlacedItem; orig: PlacedItem; startX: number; startY: number } | null = null;
  private hoverAgent: AgentId | null = null;
  /** How many agents are strolling right now (kept low so the office stays calm). */
  private wanderers = 0;

  constructor(
    private canvas: HTMLCanvasElement,
    private font: string,
    private pixelFont: string,
    room: RoomLayout,
    profiles: Record<AgentId, Profile>,
  ) {
    this.ctx = canvas.getContext("2d")!;
    this.world = document.createElement("canvas");
    this.wctx = this.world.getContext("2d")!;
    this.room = room;
    this.profiles = profiles;
    this.layout();
    const now = performance.now();
    for (const a of AGENTS) {
      const p = this.homePoint(a.id);
      this.actors.set(a.id, {
        id: a.id,
        x: p.x,
        y: p.y,
        dir: this.seats.get(a.id)?.facing ?? "S",
        facing: "S",
        path: [],
        arrive: null,
        seated: this.seats.has(a.id),
        working: false,
        busy: false,
        bubble: null,
        animT: Math.random() * 3,
        nextWander: now + 20000 + Math.random() * 40000,
      });
    }
  }

  // ------------------------------------------------------------------ setup

  start() {
    const c = this.canvas;
    c.addEventListener("pointermove", this.onMove);
    c.addEventListener("pointerdown", this.onDown);
    window.addEventListener("pointerup", this.onUp);
    c.addEventListener("pointerleave", this.onLeave);
    c.addEventListener("contextmenu", this.onContext);
    const loop = (t: number) => {
      const dt = Math.min(0.05, (t - (this.last || t)) / 1000);
      this.last = t;
      this.update(dt, t);
      this.render(t);
      this.raf = requestAnimationFrame(loop);
    };
    this.raf = requestAnimationFrame(loop);
  }

  destroy() {
    cancelAnimationFrame(this.raf);
    const c = this.canvas;
    c.removeEventListener("pointermove", this.onMove);
    c.removeEventListener("pointerdown", this.onDown);
    window.removeEventListener("pointerup", this.onUp);
    c.removeEventListener("pointerleave", this.onLeave);
    c.removeEventListener("contextmenu", this.onContext);
  }

  resize(cssWidth: number) {
    this.cssWidth = cssWidth;
    this.dpr = window.devicePixelRatio || 1;
    this.scale = cssWidth / this.W;
    this.canvas.style.width = `${cssWidth}px`;
    this.canvas.style.height = `${cssWidth * (this.H / this.W)}px`;
    this.canvas.width = Math.round(cssWidth * this.dpr);
    this.canvas.height = Math.round(cssWidth * (this.H / this.W) * this.dpr);
  }

  /** Recompute everything that depends on the room. */
  private layout() {
    const { w, h } = roomSize(this.room);
    this.W = w;
    this.H = h;
    this.world.width = w;
    this.world.height = h;
    this.blocked = blockedGrid(this.room);
    this.seats.clear();
    for (const it of this.room.items) {
      if (defOf(it).workstation && it.agent) this.seats.set(it.agent, seatOf(it));
    }
    this.bgKey = "";
  }

  setRoom(room: RoomLayout) {
    this.room = room;
    this.layout();
    if (this.cssWidth) this.resize(this.cssWidth);
    // put everyone who is idle back where they belong; keep people who are mid-task walking
    for (const a of this.actors.values()) {
      if (a.path.length) continue;
      const seat = this.seats.get(a.id);
      if (seat && (a.seated || !a.busy)) {
        a.x = seat.x;
        a.y = seat.y;
        a.dir = seat.facing;
        a.seated = true;
      } else if (!seat) {
        a.seated = false;
        const t = this.tileOf(a);
        if (this.isBlocked(t)) {
          const p = this.nearestFree(t);
          const c = center(p);
          a.x = c.x;
          a.y = c.y;
        }
      }
    }
  }

  setProfiles(p: Record<AgentId, Profile>) {
    this.profiles = p;
  }

  setEdit(patch: Partial<EditState>) {
    this.edit = { ...this.edit, ...patch };
    // selecting an item re-renders React and lands here mid-gesture, so only drop a drag when editing stops or an item is picked from the catalog
    if (!this.edit.active || this.edit.placing) this.drag = null;
    if (!this.drag) this.canvas.style.cursor = this.edit.placing ? "copy" : "default";
  }

  // ------------------------------------------------------------------ grid helpers

  private inBounds(t: Tile) {
    return t.c >= 0 && t.r >= 0 && t.c < this.room.cols && t.r < this.room.rows;
  }
  private isBlocked(t: Tile) {
    return !this.inBounds(t) || this.blocked[t.r][t.c];
  }
  private tileOf(p: Pt): Tile {
    return {
      c: Math.min(this.room.cols - 1, Math.max(0, Math.floor(p.x / TILE))),
      r: Math.min(this.room.rows - 1, Math.max(0, Math.floor((p.y - WALL_H) / TILE))),
    };
  }

  private nearestFree(from: Tile): Tile {
    const seen = new Set<number>([from.r * 1000 + from.c]);
    const q: Tile[] = [from];
    while (q.length) {
      const cur = q.shift()!;
      if (!this.isBlocked(cur)) return cur;
      for (const [dc, dr] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
        const n = { c: cur.c + dc, r: cur.r + dr };
        const k = n.r * 1000 + n.c;
        if (!this.inBounds(n) || seen.has(k)) continue;
        seen.add(k);
        q.push(n);
      }
    }
    return from;
  }

  private findPath(from: Tile, to: Tile): Tile[] {
    const key = (t: Tile) => t.r * this.room.cols + t.c;
    const prev = new Map<number, number>([[key(from), -1]]);
    const q: Tile[] = [from];
    while (q.length) {
      const cur = q.shift()!;
      if (cur.c === to.c && cur.r === to.r) break;
      for (const [dc, dr] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
        const n = { c: cur.c + dc, r: cur.r + dr };
        if (!this.inBounds(n) || prev.has(key(n))) continue;
        if (this.blocked[n.r][n.c] && !(n.c === to.c && n.r === to.r)) continue;
        prev.set(key(n), key(cur));
        q.push(n);
      }
    }
    if (!prev.has(key(to))) return [];
    const out: Tile[] = [];
    for (let k = key(to); k !== key(from); k = prev.get(k)!) out.unshift({ c: k % this.room.cols, r: Math.floor(k / this.room.cols) });
    return out;
  }

  /** Where an agent without a workstation stands: a free tile near the middle of the room. */
  private homePoint(id: AgentId): Pt {
    const seat = this.seats.get(id);
    if (seat) return { x: seat.x, y: seat.y };
    const i = AGENTS.findIndex((a) => a.id === id);
    const t = this.nearestFree({ c: Math.floor(this.room.cols / 2) - 3 + (i % 7), r: Math.floor(this.room.rows / 2) + Math.floor(i / 7) });
    return center(t);
  }

  // ------------------------------------------------------------------ commands (used by the orchestrator)

  setBubble(id: AgentId, text: string | null, kind: BubbleKind = "talk", ms?: number) {
    this.actors.get(id)!.bubble = text ? { text, kind, until: ms ? performance.now() + ms : null } : null;
  }

  setWorking(id: AgentId, working: boolean) {
    this.actors.get(id)!.working = working;
  }

  setBusy(id: AgentId, busy: boolean) {
    const a = this.actors.get(id)!;
    a.busy = busy;
    if (!busy) a.nextWander = performance.now() + 15000 + Math.random() * 30000;
  }

  link(from: AgentId, to: AgentId, label: string, ms = 2600) {
    const now = performance.now();
    this.links = this.links.filter((l) => !(l.from === from && l.to === to));
    this.links.push({ from, to, label, start: now, until: now + ms });
  }

  /** Walk to a tile (optionally ending on an exact pixel, e.g. a chair) and turn to `facing`. */
  private walk(id: AgentId, goal: Tile, facing: Dir, finalPx?: Pt, seat?: SeatInfo): Promise<void> {
    const a = this.actors.get(id)!;
    a.arrive?.(); // release whoever was awaiting the previous walk
    const mySeat = this.seats.get(id);
    const start: Tile = a.seated && mySeat ? appr(mySeat) : this.tileOf(a);
    const tiles = this.findPath(start, goal);
    if (!tiles.length && (start.c !== goal.c || start.r !== goal.r)) {
      // walled in (a closed door, a partition all round): stay put rather than walk through the wall
      a.facing = facing;
      return Promise.resolve();
    }
    const pts: Pt[] = [];
    if (a.seated && mySeat) pts.push(center(appr(mySeat)));
    // each agent keeps to its own lane so a group walking the same route does not stack up on one line
    // unsigned 32-bit hash: a float/negative hash once pushed the lane offset to -18 px, a whole row up, into desks
    const h = [...id].reduce((n, ch) => (Math.imul(n, 31) + ch.charCodeAt(0)) >>> 0, 7);
    const jx = ((h % 5) - 2) * 3; // -6..6 px
    // feet stand at tile top + 27 (see center), so only nudge them up: -12..0 px keeps them inside the tile
    const jy = -((h >>> 3) % 5) * 3;
    tiles.forEach((t, i) => {
      const c = center(t);
      pts.push(i === tiles.length - 1 && !finalPx ? c : { x: c.x + jx, y: c.y + jy });
    });
    if (finalPx) pts.push(finalPx);
    a.facing = facing;
    a.seated = false;
    return new Promise((resolve) => {
      if (!pts.length || (pts.length === 1 && Math.hypot(pts[0].x - a.x, pts[0].y - a.y) < 1)) {
        a.path = [];
        a.dir = facing;
        a.seated = !!seat;
        a.arrive = null;
        resolve();
        return;
      }
      a.path = pts;
      a.arrive = () => {
        a.seated = !!seat;
        resolve();
      };
    });
  }

  goToDesk(id: AgentId): Promise<void> {
    const seat = this.seats.get(id);
    if (!seat) {
      const p = this.homePoint(id);
      return this.walk(id, this.tileOf(p), "S");
    }
    const a = this.actors.get(id)!;
    if (a.seated && !a.path.length) return Promise.resolve();
    return this.walk(id, appr(seat), seat.facing, { x: seat.x, y: seat.y }, seat);
  }

  /** Walk over and stand beside another agent's chair, facing them. */
  visit(id: AgentId, host: AgentId): Promise<void> {
    const h = this.actors.get(host)!;
    const hs = this.seats.get(host);
    const base: Tile = hs ? appr(hs) : this.tileOf(h);
    const me = this.actors.get(id)!;
    const here = this.tileOf(me);
    const cands = [
      { c: base.c + 1, r: base.r },
      { c: base.c - 1, r: base.r },
      { c: base.c, r: base.r + 1 },
      { c: base.c, r: base.r - 1 },
      base,
    ]
      .filter((t) => !this.isBlocked(t))
      .sort((p, q) => Math.abs(p.c - here.c) + Math.abs(p.r - here.r) - (Math.abs(q.c - here.c) + Math.abs(q.r - here.r)));
    const spot = cands[0] ?? this.nearestFree(base);
    const c = center(spot);
    return this.walk(id, spot, dirFromVec(h.x - c.x, h.y - c.y));
  }

  /** Free tiles around the meeting table(s), nearest first; falls back to the middle of the room. */
  private meetingSpots(): { t: Tile; face: Dir }[] {
    const tables = this.room.items.filter((i) => i.type === "meeting");
    const out: { t: Tile; face: Dir; d: number; ang: number }[] = [];
    const seen = new Set<string>();
    const targets = tables.length
      ? tables.map((t) => ({ rect: itemRect(t), fp: footprint(t), item: t }))
      : [{ rect: { x: this.W / 2 - 16, y: WALL_H + (this.room.rows * TILE) / 2 - 16, w: 32, h: 32 }, fp: [1, 1] as [number, number], item: null }];
    for (const tg of targets) {
      const cx = tg.item ? (tg.item.col + tg.fp[0] / 2) * TILE : tg.rect.x + 16;
      const cy = tg.item ? WALL_H + (tg.item.row + tg.fp[1] / 2) * TILE : tg.rect.y + 16;
      const c0 = tg.item ? tg.item.col : Math.floor(cx / TILE);
      const r0 = tg.item ? tg.item.row : Math.floor((cy - WALL_H) / TILE);
      for (let r = r0 - 3; r <= r0 + tg.fp[1] + 2; r++) {
        for (let c = c0 - 3; c <= c0 + tg.fp[0] + 2; c++) {
          const t = { c, r };
          const k = `${c},${r}`;
          if (seen.has(k) || this.isBlocked(t)) continue;
          seen.add(k);
          const dx = Math.max(c0 - c, 0, c - (c0 + tg.fp[0] - 1));
          const dy = Math.max(r0 - r, 0, r - (r0 + tg.fp[1] - 1));
          const d = Math.max(dx, dy);
          if (d < 1 || d > 3) continue;
          const p = center(t);
          out.push({ t, face: dirFromVec(cx - p.x, cy - p.y), d, ang: Math.atan2(p.y - cy, p.x - cx) });
        }
      }
    }
    return out.sort((a, b) => a.d - b.d || a.ang - b.ang).map(({ t, face }) => ({ t, face }));
  }

  /** Gather agents around the meeting table; the director stands at the head. */
  gather(ids: AgentId[]): Promise<void[]> {
    const all = this.meetingSpots();
    const promises: Promise<void>[] = [];
    // spread people round the table instead of crowding one end: farthest-point picks from the nearest ring
    const poolN = Math.max(ids.length * 3, 12);
    const pool = all.slice(0, poolN);
    const spots: { t: Tile; face: Dir }[] = [];
    while (spots.length < ids.length && pool.length) {
      let bi = 0;
      let bd = -1;
      pool.forEach((sp, i) => {
        const d = spots.length ? Math.min(...spots.map((q) => Math.hypot(q.t.c - sp.t.c, q.t.r - sp.t.r))) : 99;
        if (d > bd) {
          bd = d;
          bi = i;
        }
      });
      spots.push(pool.splice(bi, 1)[0]);
    }
    const free = [...spots];
    const extra = [...pool, ...all.slice(poolN)];
    while (free.length < ids.length && extra.length) free.push(extra.shift()!);
    const order = [...ids].sort((a, b) => (a === "director" ? -1 : b === "director" ? 1 : 0));
    for (const id of order) {
      const a = this.actors.get(id)!;
      const here = this.tileOf(a);
      if (!free.length) {
        promises.push(this.goToDesk(id));
        continue;
      }
      // the closest spot that is still free (the director takes the first one, nearest the table's end)
      let bi = 0;
      if (id !== "director") {
        let bd = Infinity;
        free.forEach((s, i) => {
          const d = Math.abs(s.t.c - here.c) + Math.abs(s.t.r - here.r);
          if (d < bd) {
            bd = d;
            bi = i;
          }
        });
      }
      const [spot] = free.splice(bi, 1);
      promises.push(this.walk(id, spot.t, spot.face));
    }
    return Promise.all(promises);
  }

  sendDoc(from: AgentId, to: AgentId, dur = 1100): Promise<void> {
    const a = this.actors.get(from)!;
    const b = this.actors.get(to)!;
    return new Promise((done) =>
      this.docs.push({ fx: a.x, fy: a.y - 34, tx: b.x, ty: b.y - 30, start: performance.now(), dur, done }),
    );
  }

  // ------------------------------------------------------------------ simulation

  private update(dt: number, t: number) {
    for (const a of this.actors.values()) {
      if (a.path.length) {
        const next = a.path[0];
        const dx = next.x - a.x;
        const dy = next.y - a.y;
        const dist = Math.hypot(dx, dy);
        const step = SPEED * dt;
        if (dist <= step) {
          a.x = next.x;
          a.y = next.y;
          a.path.shift();
          if (!a.path.length) {
            a.dir = a.facing;
            const cb = a.arrive;
            a.arrive = null;
            cb?.();
          }
        } else {
          a.x += (dx / dist) * step;
          a.y += (dy / dist) * step;
          a.dir = dirFromVec(dx, dy);
        }
      }
      a.animT += dt;
      if (!a.seated) this.keepApart(a);
      if (a.bubble?.until && t > a.bubble.until) a.bubble = null;
      if (this.wanderEnabled && !this.edit.active && !a.busy && !a.path.length && t > a.nextWander) {
        a.nextWander = t + 40000 + Math.random() * 50000;
        if (this.wanderers < 2) {
          this.wanderers++;
          void this.wander(a.id).finally(() => this.wanderers--);
        }
      }
    }
    this.updateDoors(t);
    const now = performance.now();
    this.docs = this.docs.filter((d) => {
      if (now - d.start >= d.dur) {
        d.done();
        return false;
      }
      return true;
    });
    this.links = this.links.filter((l) => now < l.until);
  }

  /** Personal space: standing or walking, two agents never end up on top of each other. */
  private keepApart(a: Actor) {
    for (const b of this.actors.values()) {
      if (b === a || b.seated) continue;
      const dx = a.x - b.x;
      const dy = a.y - b.y;
      const d = Math.hypot(dx, dy);
      const R = 18;
      if (d >= R) continue;
      const ux = d > 0.01 ? dx / d : (a.id < b.id ? 1 : -1);
      const uy = d > 0.01 ? dy / d : 0;
      // the walking one gives way; two standing ones share the nudge
      const share = a.path.length && !b.path.length ? 1 : !a.path.length && b.path.length ? 0 : 0.5;
      const push = (R - d) * 0.25 * share;
      const nx = a.x + ux * push;
      const ny = a.y + uy * push;
      if (!this.isBlocked(this.tileOf({ x: nx, y: ny }))) {
        a.x = nx;
        a.y = ny;
      }
    }
  }

  /** A short stroll: coffee, the sofa, or a chat at a colleague's desk. */
  private async wander(id: AgentId) {
    const a = this.actors.get(id)!;
    const items = this.room.items;
    const near = (types: string[]) => items.filter((i) => types.includes(i.type));
    const roll = Math.random();
    const standBy = (it: PlacedItem): Tile | null => {
      const [w, h] = footprint(it);
      const cands: Tile[] = [];
      for (let c = it.col - 1; c <= it.col + w; c++) for (let r = it.row - 1; r <= it.row + h; r++) cands.push({ c, r });
      const ok = cands.filter((t) => !this.isBlocked(t) && (t.c < it.col || t.c >= it.col + w || t.r < it.row || t.r >= it.row + h));
      return ok.length ? ok[Math.floor(Math.random() * ok.length)] : null;
    };
    let line = "";
    let spot: Tile | null = null;
    if (roll < 0.4 && near(["cooler", "fridge"]).length) {
      const it = near(["cooler", "fridge"])[Math.floor(Math.random() * near(["cooler", "fridge"]).length)];
      spot = standBy(it);
      line = it.type === "cooler" ? "💧 ขอน้ำสักแก้ว" : "☕ หาอะไรกินหน่อย";
    } else if (roll < 0.62 && near(["sofa", "plush"]).length) {
      const it = near(["sofa", "plush"])[Math.floor(Math.random() * 2) % near(["sofa", "plush"]).length];
      spot = standBy(it);
      line = "😌 พักสายตาแป๊บ";
    } else if (roll < 0.74 && near(["whiteboard", "wb_wall"]).length) {
      spot = standBy(near(["whiteboard"])[0] ?? near(["wb_wall"])[0]);
      line = "📌 เช็กบอร์ดงาน";
    } else {
      const others = AGENTS.filter((o) => o.id !== id);
      const host = others[Math.floor(Math.random() * others.length)].id;
      await this.visit(id, host);
      if (a.busy) return;
      this.setBubble(id, "💬 มีไอเดียอยากแชร์", "talk", 2500);
      this.setBubble(host, "👀 ไหนเล่าซิ", "talk", 2500);
      this.link(id, host, "IDEA", 2600);
      await sleep(3200);
      if (!a.busy) await this.goToDesk(id);
      return;
    }
    if (!spot) return;
    const p = center(spot);
    await this.walk(id, spot, dirFromVec(this.W / 2 - p.x, WALL_H + 100 - p.y));
    if (a.busy) return;
    this.setBubble(id, line, "talk", 3000);
    await sleep(4000);
    if (!a.busy) await this.goToDesk(id);
  }

  // ------------------------------------------------------------------ pointer

  private toWorld(e: PointerEvent): Pt {
    const r = this.canvas.getBoundingClientRect();
    return { x: ((e.clientX - r.left) / r.width) * this.W, y: ((e.clientY - r.top) / r.height) * this.H };
  }

  /** Map a CSS-pixel position on the canvas to an agent. */
  hitTest(cx: number, cy: number): AgentId | null {
    const x = cx / this.scale;
    const y = cy / this.scale;
    let best: AgentId | null = null;
    let bd = Infinity;
    for (const a of this.actors.values()) {
      const top = a.y - FEET_Y;
      const bottom = a.y + 2;
      if (x < a.x - 16 || x > a.x + 16 || y < top || y > bottom) continue;
      const d = Math.abs(a.y - y);
      if (d < bd) {
        bd = d;
        best = a.id;
      }
    }
    return best;
  }

  private itemsInOrder(): PlacedItem[] {
    const own = this.room.items.filter((i) => defOf(i).kind !== "wall");
    // wall items hung on a partition are drawn (and picked) together with it
    const walls = this.room.items.filter((i) => defOf(i).kind === "wall" && !i.mount);
    return [...walls, ...own.sort((a, b) => baselineOf(a) - baselineOf(b))];
  }

  private pickItem(p: Pt): PlacedItem | null {
    // things hanging on a partition are in front of it
    const hung = this.room.items.filter((i) => i.mount);
    for (let i = hung.length - 1; i >= 0; i--) {
      const r = itemRect(hung[i]);
      if (p.x >= r.x && p.x <= r.x + r.w && p.y >= r.y && p.y <= r.y + r.h) return hung[i];
    }
    const list = this.itemsInOrder();
    for (let i = list.length - 1; i >= 0; i--) {
      const it = list[i];
      if (defOf(it).kind === "rug") continue;
      const r = itemRect(it);
      if (p.x >= r.x && p.x <= r.x + r.w && p.y >= r.y && p.y <= r.y + r.h) return it;
    }
    // rugs last (they lie under everything)
    for (let i = list.length - 1; i >= 0; i--) {
      const it = list[i];
      if (defOf(it).kind !== "rug") continue;
      const r = itemRect(it);
      if (p.x >= r.x && p.x <= r.x + r.w && p.y >= r.y && p.y <= r.y + r.h) return it;
    }
    return null;
  }

  /** Doors currently opened by someone walking through (door id -> time it may close). */
  private autoOpen = new Map<string, number>();

  /** Propped open by the user, or held open by an agent passing through. */
  private isDoorOpen(d: PlacedItem) {
    return !!d.open || this.autoOpen.has(d.id);
  }

  /** Doors in a partition swing open when an agent comes near and close shortly after they have gone. */
  private updateDoors(t: number) {
    for (const d of this.room.items) {
      const doorway = !!defOf(d).doorway;
      if (!doorway && (defOf(d).proc !== "door" || !d.mount || d.mount === "__floor__")) continue;
      const r = doorway ? null : itemRect(d);
      const cx = r ? r.x + r.w / 2 : d.col * TILE + TILE / 2;
      const cy = r ? r.y + r.h - 12 : WALL_H + d.row * TILE + 27;
      let near = false;
      for (const a of this.actors.values()) {
        if (!a.seated && Math.hypot(a.x - cx, a.y - cy) < 40) near = true;
      }
      if (near) this.autoOpen.set(d.id, t + 700);
      else if (this.autoOpen.has(d.id) && t > this.autoOpen.get(d.id)!) this.autoOpen.delete(d.id);
    }
  }

  /** The door under the pointer, if any. */
  private doorAt(p: Pt): PlacedItem | null {
    for (const it of this.room.items) {
      if (defOf(it).proc !== "door") continue;
      const r = itemRect(it);
      if (p.x >= r.x && p.x <= r.x + r.w && p.y >= r.y && p.y <= r.y + r.h) return it;
    }
    return null;
  }

  /** Open or close a door; the walkable grid follows because the room is rebuilt. */
  toggleDoor(id: string) {
    const it = this.room.items.find((i) => i.id === id);
    if (!it || defOf(it).proc !== "door") return;
    this.onRoomChange({ ...this.room, items: this.room.items.map((i) => (i.id === id ? { ...i, open: !i.open } : i)) });
  }

  /** The partition whose front face is under the pointer, if any. */
  private hostAt(p: Pt): PlacedItem | null {
    for (const it of this.room.items) {
      if (defOf(it).proc !== "partition" || defOf(it).doorway) continue;
      const f = partitionGeo(it).face;
      if (f && p.x >= f.x && p.x <= f.x + f.w && p.y >= f.y && p.y <= f.y + f.h) return it;
    }
    return null;
  }

  /** Where an item would sit with the pointer at `p` (its footprint centred on the pointer, snapped to the grid). */
  private placeAt(base: PlacedItem, p: Pt, grab?: { dx: number; dy: number }): PlacedItem {
    const def = defOf(base);
    if (def.kind === "wall") {
      const { w, h } = wallSize(base);
      const gx = grab?.dx ?? w / 2;
      const gy = grab?.dy ?? h / 2;
      const snap = (v: number) => Math.round(v / 4) * 4;
      const host = this.hostAt(p);
      if (host) {
        // hung on the front face of a partition: slides in both directions
        const f = partitionGeo(host).face!;
        if (def.proc === "door") {
          const col = Math.max(0, Math.min(Math.round(f.w / TILE) - 1, Math.floor((p.x - f.x) / TILE)));
          return { ...base, mount: host.id, x: f.x + col * TILE, y: f.y + f.h - h };
        }
        return {
          ...base,
          mount: host.id,
          x: Math.max(f.x + 4, Math.min(f.x + f.w - 4 - w, snap(p.x - gx))),
          y: Math.max(f.y + 4, Math.min(f.y + f.h - 4 - h, snap(p.y - gy))),
        };
      }
      if (p.y < WALL_H + 4) {
        // back wall
        const x = Math.max(0, Math.min(this.room.cols * TILE - w, snap(p.x - gx)));
        const y = def.proc === "plaque" ? Math.max(4, Math.min(WALL_H - h - 4, snap(p.y - gy))) : base.mount ? wallY(def) : (base.y ?? wallY(def));
        return { ...base, mount: undefined, x, y };
      }
      // not over a wall: shown in red, cannot be dropped
      return { ...base, mount: "__floor__", x: snap(p.x - gx), y: snap(p.y - gy) };
    }
    const [fw, fh] = footprint(base);
    const col = Math.round((p.x - (grab?.dx ?? (fw * TILE) / 2)) / TILE);
    const row = Math.round((p.y - WALL_H - (grab?.dy ?? (fh * TILE) / 2)) / TILE);
    return { ...base, col, row };
  }

  private onMove = (e: PointerEvent) => {
    const p = this.toWorld(e);
    this.pointer = p;
    if (this.edit.active) {
      if (this.drag) {
        const d = this.drag;
        if (!d.moved && Math.hypot(e.clientX - d.startX, e.clientY - d.startY) > 4) d.moved = true;
        if (d.moved) d.cur = this.placeAt(d.orig, p, { dx: d.dx, dy: d.dy });
        this.canvas.style.cursor = "grabbing";
      } else if (!this.edit.placing) {
        this.canvas.style.cursor = this.pickItem(p) ? "grab" : "default";
      }
      return;
    }
    const r = this.canvas.getBoundingClientRect();
    this.hoverAgent = this.hitTest(e.clientX - r.left, e.clientY - r.top);
    this.canvas.style.cursor = this.hoverAgent || this.doorAt(p) ? "pointer" : "default";
  };

  private onLeave = () => {
    this.pointer = null;
    this.hoverAgent = null;
  };

  private onContext = (e: Event) => {
    if (this.edit.active && this.edit.placing) {
      e.preventDefault();
      this.onPlaceCancel();
    }
  };

  private onDown = (e: PointerEvent) => {
    if (e.button !== 0) return;
    const p = this.toWorld(e);
    if (!this.edit.active) {
      const r = this.canvas.getBoundingClientRect();
      const agent = this.hitTest(e.clientX - r.left, e.clientY - r.top);
      const door = agent ? null : this.doorAt(p);
      if (door) {
        this.toggleDoor(door.id);
        return;
      }
      this.onSelectAgent(agent);
      return;
    }
    if (this.edit.placing) {
      const pl = this.edit.placing;
      const def = defOf({ type: pl.type } as PlacedItem);
      const item = this.placeAt({ id: newId(), type: pl.type, col: 0, row: 0, rot: pl.rot, color: pl.color, ...pl.props, y: wallY(def) }, p);
      if (canPlace(this.room, item).ok) {
        this.onRoomChange({ ...this.room, items: [...this.room.items, item] }, item.id);
        if (!e.shiftKey) this.onPlaceCancel();
      }
      return;
    }
    const hit = this.pickItem(p);
    this.onEditSelect(hit?.id ?? null);
    if (hit) {
      const r = itemRect(hit);
      const def = defOf(hit);
      const grabDx = def.kind === "wall" ? p.x - (hit.x ?? 0) : p.x - hit.col * TILE;
      const grabDy = def.kind === "wall" ? p.y - (hit.y ?? 0) : p.y - WALL_H - hit.row * TILE;
      this.drag = { id: hit.id, dx: grabDx, dy: grabDy, moved: false, cur: hit, orig: hit, startX: e.clientX, startY: e.clientY };
      void r;
    }
  };

  private onUp = () => {
    const d = this.drag;
    this.drag = null;
    if (!d || !d.moved) return;
    if (canPlace(this.room, d.cur).ok) {
      // a partition takes whatever is hung on it along
      this.onRoomChange(withItemUpdated(this.room, d.cur).room, d.id);
    }
  };

  // ------------------------------------------------------------------ rendering

  private buildBackground() {
    const key = `${this.room.floor}|${this.room.floorTint}|${this.room.wallTint}|${this.room.cols}|${this.room.rows}|${furnitureImage("floor_a") ? 1 : 0}${furnitureImage("floor_b") ? 1 : 0}${furnitureImage("wall") ? 1 : 0}`;
    if (this.bg && this.bgKey === key) return;
    this.bgKey = key;
    const c = document.createElement("canvas");
    c.width = this.W;
    c.height = this.H;
    const g = c.getContext("2d")!;
    g.imageSmoothingEnabled = false;
    const A = furnitureImage("floor_a");
    const Bf = furnitureImage("floor_b");
    for (let r = 0; r < this.room.rows; r++) {
      for (let col = 0; col < this.room.cols; col++) {
        const x = col * TILE;
        const y = WALL_H + r * TILE;
        const f = this.room.floor;
        if (f === "wood_a" || f === "wood_b") {
          const useB = f === "wood_b" || ((col * 7 + r * 13) % 5 < 2);
          const img = useB ? Bf : A;
          if (img) g.drawImage(img, x, y);
          else {
            g.fillStyle = "#d6bb90";
            g.fillRect(x, y, TILE, TILE);
          }
        } else if (f === "tile") {
          const dark = (col + r) % 2 === 0;
          g.fillStyle = dark ? "#8fa0b6" : "#a3b2c6";
          g.fillRect(x, y, TILE, TILE);
          g.fillStyle = "rgba(255,255,255,0.18)";
          g.fillRect(x, y, TILE, 2);
          g.fillRect(x, y, 2, TILE);
          g.fillStyle = "rgba(40,50,70,0.28)";
          g.fillRect(x, y + TILE - 2, TILE, 2);
          g.fillRect(x + TILE - 2, y, 2, TILE);
        } else {
          g.fillStyle = (col + r) % 2 === 0 ? "#6f8296" : "#6a7d91";
          g.fillRect(x, y, TILE, TILE);
          g.fillStyle = "rgba(255,255,255,0.07)";
          for (let k = 0; k < 9; k++) g.fillRect(x + ((k * 11 + r * 5) % 30), y + ((k * 7 + col * 3) % 30), 2, 1);
        }
      }
    }
    if (this.room.floorTint) {
      g.globalCompositeOperation = "source-atop";
      g.globalAlpha = 0.32;
      g.fillStyle = this.room.floorTint;
      g.fillRect(0, WALL_H, this.W, this.room.rows * TILE);
      g.globalAlpha = 1;
      g.globalCompositeOperation = "source-over";
    }
    // back wall
    const wallImg = furnitureImage("wall");
    const wallTileW = Math.round(TILE * OBJECT_SCALE);
    for (let x = 0; x < this.W; x += wallTileW) {
      if (wallImg) g.drawImage(wallImg, x, 0, wallTileW, WALL_H);
      else {
        g.fillStyle = "#e3d8bd";
        g.fillRect(x, 0, wallTileW, WALL_H);
      }
    }
    if (this.room.wallTint) {
      g.globalAlpha = 0.3;
      g.fillStyle = this.room.wallTint;
      g.fillRect(0, 0, this.W, WALL_H);
      g.globalAlpha = 1;
    }
    const grad = g.createLinearGradient(0, WALL_H, 0, WALL_H + 10);
    grad.addColorStop(0, "rgba(40,24,30,0.28)");
    grad.addColorStop(1, "rgba(40,24,30,0)");
    g.fillStyle = grad;
    g.fillRect(0, WALL_H, this.W, 10);
    this.bg = c;
  }

  private drawRug(c: CanvasRenderingContext2D, it: PlacedItem, alpha = 1) {
    const [w, h] = footprint(it);
    const x = it.col * TILE + 2;
    const y = WALL_H + it.row * TILE + 2;
    const W = w * TILE - 4;
    const H = h * TILE - 4;
    const col = it.color ?? "#8c3b4a";
    c.save();
    c.globalAlpha = alpha;
    c.fillStyle = "rgba(0,0,0,0.18)";
    c.fillRect(x + 2, y + 3, W, H);
    c.fillStyle = shade(col, -0.3);
    c.fillRect(x, y, W, H);
    c.fillStyle = col;
    c.fillRect(x + 3, y + 3, W - 6, H - 6);
    c.fillStyle = shade(col, 0.28);
    c.fillRect(x + 6, y + 6, W - 12, 2);
    c.fillRect(x + 6, y + H - 8, W - 12, 2);
    c.fillRect(x + 6, y + 6, 2, H - 12);
    c.fillRect(x + W - 8, y + 6, 2, H - 12);
    c.fillStyle = shade(col, -0.12);
    c.fillRect(x + 10, y + 10, W - 20, H - 20);
    c.fillStyle = shade(col, 0.12);
    for (let i = 0; i < Math.floor((W - 24) / 8); i++) c.fillRect(x + 12 + i * 8, y + H / 2 - 1, 4, 2);
    // fringe
    c.fillStyle = shade(col, 0.45);
    for (let i = 0; i < Math.floor(W / 4); i++) {
      c.fillRect(x + i * 4 + 1, y - 2, 2, 2);
      c.fillRect(x + i * 4 + 1, y + H, 2, 2);
    }
    c.restore();
  }

  private drawOps(c: CanvasRenderingContext2D, it: PlacedItem, alpha = 1) {
    c.save();
    c.globalAlpha = alpha;
    for (const op of floorOps(it)) {
      const img = furnitureImage(op.sprite);
      if (img) c.drawImage(img, op.x, op.y, img.width * op.s, img.height * op.s);
    }
    c.restore();
  }

  private drawPartition(c: CanvasRenderingContext2D, it: PlacedItem, alpha = 1, withDoors = true) {
    const g = partitionGeo(it);
    const col = it.color ?? "#e9e4d6";
    const style = it.style ?? "solid";
    const OL = "#2b2230";
    c.save();
    c.globalAlpha = alpha;
    const holes = withDoors ? this.room.items.filter((d) => d.mount === it.id && defOf(d).proc === "door" && this.isDoorOpen(d)).map((d) => itemRect(d)) : [];
    const dw = defOf(it).doorway ? this.doorwayRect(it) : null;
    if (dw && withDoors && this.isDoorOpen(it)) holes.push(dw);
    if (holes.length) {
      // an open door is a gap in the panel: what is behind it (floor, people walking through) shows
      c.beginPath();
      c.rect(g.body.x - 20, g.body.y - 20, g.body.w + 40, g.body.h + 60);
      for (const r of holes) c.rect(r.x, r.y, r.w, r.h);
      c.clip("evenodd");
    }
    if (g.horizontal) {
      const f = g.face!;
      const plinth = 10;
      // soft shadow on the floor in front
      c.fillStyle = "rgba(40,24,30,0.22)";
      c.fillRect(f.x + 4, g.base - 1, f.w, 9);
      if (style === "glass") {
        c.fillStyle = shade(col, -0.35);
        c.fillRect(f.x, f.y, f.w, f.h);
        c.fillStyle = "rgba(196,228,242,0.9)";
        for (let x = f.x; x < f.x + f.w; x += TILE) {
          c.fillRect(x + 4, f.y + 4, Math.min(TILE, f.x + f.w - x) - 8, f.h - plinth - 8);
        }
        c.fillStyle = "rgba(255,255,255,0.5)";
        for (let x = f.x; x < f.x + f.w; x += TILE) {
          c.fillRect(x + 8, f.y + 8, 3, 22);
          c.fillRect(x + 14, f.y + 8, 2, 14);
        }
      } else if (style === "slat") {
        for (let x = f.x; x < f.x + f.w; x += 6) {
          c.fillStyle = ((x - f.x) / 6) % 2 === 0 ? shade(col, 0.08) : shade(col, -0.22);
          c.fillRect(x, f.y, Math.min(6, f.x + f.w - x), f.h);
        }
        c.fillStyle = shade(col, -0.3);
        c.fillRect(f.x, f.y + 24, f.w, 3);
        c.fillRect(f.x, f.y + f.h - plinth - 16, f.w, 3);
      } else {
        c.fillStyle = col;
        c.fillRect(f.x, f.y, f.w, f.h);
        c.fillStyle = shade(col, 0.22);
        c.fillRect(f.x, f.y + 3, f.w, 3);
        c.fillStyle = shade(col, -0.14);
        for (let x = f.x + TILE; x < f.x + f.w; x += TILE) c.fillRect(x - 1, f.y, 2, f.h - plinth);
      }
      c.fillStyle = shade(col, -0.42);
      c.fillRect(f.x, f.y + f.h - plinth, f.w, plinth);
      c.fillStyle = shade(col, -0.2);
      c.fillRect(f.x, f.y + f.h - plinth, f.w, 2);
      // top edge
      c.fillStyle = shade(col, 0.34);
      c.fillRect(f.x, f.y - PART_TOP, f.w, PART_TOP);
      c.fillStyle = shade(col, -0.1);
      c.fillRect(f.x, f.y - 3, f.w, 3);
      c.strokeStyle = OL;
      c.lineWidth = 1;
      c.strokeRect(f.x + 0.5, f.y - PART_TOP + 0.5, f.w - 1, f.h + PART_TOP - 1);
    } else {
      const b = g.body;
      const topH = b.h - PART_H;
      c.fillStyle = "rgba(40,24,30,0.22)";
      c.fillRect(b.x + 4, g.base - 2, b.w, 8);
      c.fillStyle = shade(col, 0.34);
      c.fillRect(b.x, b.y, b.w, topH);
      const endY = b.y + topH;
      if (style === "glass") {
        c.fillStyle = shade(col, -0.35);
        c.fillRect(b.x, endY, b.w, PART_H);
        c.fillStyle = "rgba(196,228,242,0.9)";
        c.fillRect(b.x + 3, endY + 4, b.w - 6, PART_H - 18);
      } else if (style === "slat") {
        c.fillStyle = shade(col, 0.05);
        c.fillRect(b.x, endY, b.w, PART_H);
        c.fillStyle = shade(col, -0.25);
        for (let y = endY + 4; y < endY + PART_H - 8; y += 8) c.fillRect(b.x, y, b.w, 3);
      } else {
        c.fillStyle = col;
        c.fillRect(b.x, endY, b.w, PART_H);
        c.fillStyle = shade(col, 0.2);
        c.fillRect(b.x + 2, endY + 3, 3, PART_H - 14);
      }
      c.fillStyle = shade(col, -0.42);
      c.fillRect(b.x, endY + PART_H - 10, b.w, 10);
      c.strokeStyle = OL;
      c.lineWidth = 1;
      c.strokeRect(b.x + 0.5, b.y + 0.5, b.w - 1, b.h - 1);
    }
    c.restore();
  }

  /** The door opening of a Partition + ประตู: the whole tile, door-height, at the bottom of the panel. */
  private doorwayRect(it: PlacedItem) {
    const g = partitionGeo(it);
    if (g.horizontal) return { x: g.face!.x, y: g.base - DOOR_H, w: TILE, h: DOOR_H };
    const b = g.body;
    return { x: b.x - 2, y: g.base - PART_H, w: b.w + 4, h: PART_H };
  }

  /** The door leaf / frame of a Partition + ประตู, drawn over the panel. */
  private drawDoorway(c: CanvasRenderingContext2D, it: PlacedItem, alpha = 1) {
    const r = this.doorwayRect(it);
    if (partitionGeo(it).horizontal) {
      this.drawDoor(c, { ...it, type: "door", mount: it.id, x: r.x, y: r.y, open: it.open }, alpha);
      return;
    }
    // seen edge-on: closed shows the door's frame on the panel; open leaves two posts and the lintel
    c.save();
    c.globalAlpha = alpha;
    c.fillStyle = "#2b2230";
    if (this.isDoorOpen(it)) {
      c.fillRect(r.x + 2, r.y, r.w - 4, 4);
      c.fillRect(r.x + 2, r.y + 4, r.w - 4, 3);
    } else {
      c.strokeStyle = "#2b2230";
      c.lineWidth = 2;
      c.strokeRect(r.x + 3, r.y + 6, r.w - 6, r.h - 8);
      c.fillStyle = "#f0d27a";
      c.fillRect(r.x + r.w / 2 - 1, r.y + r.h / 2, 2, 5);
    }
    c.restore();
  }

  private drawPlaque(c: CanvasRenderingContext2D, it: PlacedItem, alpha = 1) {
    const { w, h } = wallSize(it);
    const x = it.x ?? 0;
    const y = it.y ?? 0;
    const st = PLAQUE_STYLES.find((q) => q.id === it.style) ?? PLAQUE_STYLES[0];
    c.save();
    c.globalAlpha = alpha;
    c.fillStyle = "rgba(30,20,30,0.28)";
    c.fillRect(x + 2, y + 3, w, h);
    c.fillStyle = shade(st.fill, -0.55);
    c.fillRect(x, y, w, h);
    c.fillStyle = st.fill;
    c.fillRect(x + 2, y + 2, w - 4, h - 4);
    c.fillStyle = shade(st.fill, 0.3);
    c.fillRect(x + 2, y + 2, w - 4, 2);
    c.fillStyle = shade(st.fill, -0.22);
    c.fillRect(x + 2, y + h - 4, w - 4, 2);
    // screws
    for (const sx of [x + 5, x + w - 7]) {
      c.fillStyle = shade(st.fill, -0.5);
      c.fillRect(sx, y + h / 2 - 1, 2, 2);
    }
    const text = (it.text ?? "").trim();
    if (text) {
      let px = Math.min(h - 10, 18);
      c.font = `700 ${px}px ${this.font}`;
      while (px > 7 && c.measureText(text).width > w - 22) {
        px--;
        c.font = `700 ${px}px ${this.font}`;
      }
      c.textAlign = "center";
      c.textBaseline = "middle";
      c.fillStyle = shade(st.fill, -0.45);
      c.fillText(text, x + w / 2 + 1, y + h / 2 + 2);
      c.fillStyle = st.text;
      c.fillText(text, x + w / 2, y + h / 2 + 1);
      c.textAlign = "left";
    }
    c.restore();
  }

  /** A door: shut it is a wooden panel, open it is a doorway with the leaf swung back. */
  private drawDoor(c: CanvasRenderingContext2D, it: PlacedItem, alpha = 1) {
    const { w, h } = wallSize(it);
    const x = it.x ?? 0;
    const y = it.y ?? 0;
    const onPanel = !!it.mount && it.mount !== "__floor__";
    const OL = "#2b2230";
    const wood = "#c98a4b";
    c.save();
    c.globalAlpha = alpha;
    const open = this.isDoorOpen(it);
    if (!open) {
      if (!onPanel) {
        const img = furnitureImage("door");
        if (img) c.drawImage(img, x, y, img.width * OBJECT_SCALE, img.height * OBJECT_SCALE);
        c.restore();
        return;
      }
      c.fillStyle = OL;
      c.fillRect(x, y, w, h);
      c.fillStyle = shade(wood, -0.3);
      c.fillRect(x + 2, y + 2, w - 4, h - 2);
      c.fillStyle = wood;
      c.fillRect(x + 4, y + 4, w - 8, h - 4);
      c.fillStyle = shade(wood, 0.2);
      c.fillRect(x + 4, y + 4, w - 8, 2);
      c.fillStyle = "#8ec9ea"; // window
      c.fillRect(x + 8, y + 9, w - 16, 16);
      c.fillStyle = "rgba(255,255,255,0.55)";
      c.fillRect(x + 10, y + 11, 4, 8);
      c.fillStyle = shade(wood, -0.18); // lower panel
      c.fillRect(x + 8, y + 32, w - 16, 22);
      c.fillStyle = shade(wood, 0.12);
      c.fillRect(x + 10, y + 34, w - 20, 18);
      c.fillStyle = "#d9dde2"; // kick plate
      c.fillRect(x + 4, y + h - 8, w - 8, 6);
      c.fillStyle = "#f0d27a"; // handle
      c.fillRect(x + w - 11, y + 30, 5, 3);
      c.fillRect(x + w - 8, y + 28, 2, 7);
    } else {
      const leaf = Math.round(w * 0.26);
      if (!onPanel) {
        // the doorway into the next room
        c.fillStyle = OL;
        c.fillRect(x, y, w, h);
        const gr = c.createLinearGradient(0, y, 0, y + h);
        gr.addColorStop(0, "#3a2f45");
        gr.addColorStop(1, "#1d1826");
        c.fillStyle = gr;
        c.fillRect(x + 3, y + 3, w - 6, h - 3);
      } else {
        c.fillStyle = OL; // frame around the gap
        c.fillRect(x, y, w, 3);
        c.fillRect(x, y, 2, h);
        c.fillRect(x + w - 2, y, 2, h);
      }
      // the leaf, swung open against the left jamb
      c.fillStyle = shade(wood, -0.35);
      c.beginPath();
      c.moveTo(x + 2, y + 3);
      c.lineTo(x + 2 + leaf, y + 7);
      c.lineTo(x + 2 + leaf, y + h - 5);
      c.lineTo(x + 2, y + h - 2);
      c.closePath();
      c.fill();
      c.fillStyle = shade(wood, -0.1);
      c.beginPath();
      c.moveTo(x + 4, y + 6);
      c.lineTo(x + leaf, y + 9);
      c.lineTo(x + leaf, y + h - 8);
      c.lineTo(x + 4, y + h - 5);
      c.closePath();
      c.fill();
      c.fillStyle = "#f0d27a";
      c.fillRect(x + leaf - 4, y + 30, 2, 5);
    }
    c.restore();
  }

  private drawWallItem(c: CanvasRenderingContext2D, it: PlacedItem, alpha = 1) {
    const def = defOf(it);
    if (def.proc === "plaque") return this.drawPlaque(c, it, alpha);
    if (def.proc === "door") return this.drawDoor(c, it, alpha);
    const img = furnitureImage(def.variant("S").sprite);
    if (!img) return;
    c.save();
    c.globalAlpha = alpha;
    c.drawImage(img, it.x ?? 0, it.y ?? wallY(def), img.width * OBJECT_SCALE, img.height * OBJECT_SCALE);
    c.restore();
  }

  private actorFrame(a: Actor, t: number): HTMLCanvasElement | null {
    const ap = this.profiles[a.id].appearance;
    let anim: Anim = "idle";
    if (a.seated) anim = "sit";
    else if (a.path.length) anim = "walk";
    else if (a.bubble && a.bubble.kind === "done") anim = "wave";
    else if (a.bubble && a.bubble.kind === "talk") anim = "talk";
    const info = animInfo(anim);
    if (!info) return null;
    const idx = info.frames <= 1 ? 0 : Math.floor((a.animT * 1000) / info.msPerFrame) % info.frames;
    void t;
    return characterFrame(ap, anim, a.dir, idx);
  }

  private drawActor(c: CanvasRenderingContext2D, a: Actor, t: number) {
    const frame = this.actorFrame(a, t);
    if (!a.seated) {
      c.fillStyle = "rgba(30,20,30,0.2)";
      c.beginPath();
      c.ellipse(a.x, a.y + 1, 11, 4, 0, 0, Math.PI * 2);
      c.fill();
    }
    if (this.selected === a.id) {
      c.strokeStyle = "rgba(95,233,255,0.9)";
      c.lineWidth = 2;
      c.beginPath();
      c.ellipse(a.x, a.y + 1, 15, 6, 0, 0, Math.PI * 2);
      c.stroke();
    }
    if (frame) drawFrame(c, frame, a.x - (CELL_W * CHAR_SCALE) / 2, a.y - FEET_Y, CHAR_SCALE);
  }

  private render(t: number) {
    if (!this.W) return;
    this.buildBackground();
    const c = this.wctx;
    c.imageSmoothingEnabled = false;
    c.clearRect(0, 0, this.W, this.H);
    c.drawImage(this.bg!, 0, 0);

    const dragging = this.drag?.moved ? this.drag : null;
    const items = this.itemsInOrder().map((i) => (dragging && i.id === dragging.id ? null : i)).filter((i): i is PlacedItem => !!i);

    // 1) flat things: wall items, rugs
    for (const it of items) {
      const k = defOf(it).kind;
      if (k === "wall") this.drawWallItem(c, it);
      else if (k === "rug") this.drawRug(c, it);
    }

    // 2) light pools under working agents' screens
    for (const a of this.actors.values()) {
      if (!a.working || !a.seated) continue;
      const g = c.createRadialGradient(a.x, a.y - 14, 2, a.x, a.y - 14, 34);
      g.addColorStop(0, `rgba(95,243,255,${0.16 + 0.04 * Math.sin(t / 260)})`);
      g.addColorStop(1, "rgba(95,243,255,0)");
      c.fillStyle = g;
      c.fillRect(a.x - 40, a.y - 50, 80, 80);
    }

    // 3) depth-sorted objects and people
    type Drawable = { y: number; draw: () => void };
    const list: Drawable[] = [];
    const seatedAt = new Map<string, Actor>();
    for (const a of this.actors.values()) {
      const seat = this.seats.get(a.id);
      if (a.seated && seat) seatedAt.set(seat.itemId, a);
    }
    for (const it of items) {
      const def = defOf(it);
      if (def.kind === "wall" || def.kind === "rug") continue;
      if (def.proc === "partition") {
        const hung = childrenOf(this.room, it.id).filter((ch) => !(dragging && ch.id === dragging.id));
        list.push({
          y: baselineOf(it),
          draw: () => {
            this.drawPartition(c, it);
            if (defOf(it).doorway) this.drawDoorway(c, it);
            for (const ch of hung) this.drawWallItem(c, ch);
          },
        });
        continue;
      }
      if (def.workstation) {
        const ops = floorOps(it);
        const occupant = seatedAt.get(it.id);
        const seq = stationOrder(it);
        list.push({
          y: baselineOf(it),
          draw: () => {
            const drawChair = () => this.drawSprite(c, ops[0]);
            const drawDesk = () => this.drawSprite(c, ops[1]);
            if (seq === "desk-last") {
              drawChair();
              if (occupant) this.drawActor(c, occupant, t);
              drawDesk();
            } else {
              drawDesk();
              if (occupant) this.drawActor(c, occupant, t);
              drawChair();
            }
          },
        });
      } else {
        list.push({ y: baselineOf(it), draw: () => this.drawOps(c, it) });
      }
    }
    for (const a of this.actors.values()) {
      const seat = this.seats.get(a.id);
      if (a.seated && seat && seatedAt.has(seat.itemId)) continue; // drawn with its workstation
      list.push({ y: a.y, draw: () => this.drawActor(c, a, t) });
    }
    list.sort((p, q) => p.y - q.y);
    for (const d of list) d.draw();

    // 4) editor overlays
    if (this.edit.active) this.drawEditorOverlay(c);

    // 5) flying documents
    const now = performance.now();
    for (const d of this.docs) {
      const k = Math.min(1, (now - d.start) / d.dur);
      const e = k < 0.5 ? 2 * k * k : 1 - Math.pow(-2 * k + 2, 2) / 2;
      const x = d.fx + (d.tx - d.fx) * e;
      const y = d.fy + (d.ty - d.fy) * e - Math.sin(k * Math.PI) * 30;
      c.fillStyle = "#fffdf5";
      c.fillRect(x - 6, y - 8, 12, 16);
      c.strokeStyle = "#5e3a22";
      c.lineWidth = 1;
      c.strokeRect(x - 5.5, y - 7.5, 11, 15);
      c.fillStyle = "#c0392b";
      c.fillRect(x - 3, y - 4, 6, 1);
      c.fillStyle = "#8a7b68";
      c.fillRect(x - 3, y - 1, 6, 1);
      c.fillRect(x - 3, y + 2, 5, 1);
    }

    // blit the world, then draw crisp text overlays at screen resolution
    const ctx = this.ctx;
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.imageSmoothingEnabled = false;
    ctx.drawImage(this.world, 0, 0, this.W, this.H, 0, 0, this.canvas.width, this.canvas.height);
    ctx.setTransform(this.dpr, 0, 0, this.dpr, 0, 0);
    const k = this.scale;
    for (const l of this.links) this.drawLink(ctx, l, k, now);
    if (!this.edit.active) for (const a of this.actors.values()) this.drawLabel(ctx, a, k);
    for (const a of [...this.actors.values()].filter((x) => x.bubble).sort((p, q) => p.y - q.y)) this.drawBubble(ctx, a, k);
  }

  private drawSprite(c: CanvasRenderingContext2D, op: { sprite: string; x: number; y: number; s: number }) {
    const img = furnitureImage(op.sprite);
    if (img) c.drawImage(img, op.x, op.y, img.width * op.s, img.height * op.s);
  }

  private drawEditorOverlay(c: CanvasRenderingContext2D) {
    // grid
    c.strokeStyle = "rgba(255,255,255,0.24)";
    c.lineWidth = 1;
    c.beginPath();
    for (let col = 0; col <= this.room.cols; col++) {
      c.moveTo(col * TILE + 0.5, WALL_H);
      c.lineTo(col * TILE + 0.5, this.H);
    }
    for (let r = 0; r <= this.room.rows; r++) {
      c.moveTo(0, WALL_H + r * TILE + 0.5);
      c.lineTo(this.W, WALL_H + r * TILE + 0.5);
    }
    c.stroke();

    // selection
    const sel = this.edit.selectedId ? this.room.items.find((i) => i.id === this.edit.selectedId) : null;
    const dragging = this.drag?.moved ? this.drag.cur : null;
    const shown = dragging ?? sel ?? null;
    if (shown) {
      const r = itemRect(shown);
      c.save();
      c.strokeStyle = "#ffe26a";
      c.lineWidth = 2;
      c.setLineDash([5, 3]);
      c.strokeRect(r.x - 1, r.y - 1, r.w + 2, r.h + 2);
      c.restore();
    }

    // ghost (placing a new item, or the item being dragged)
    let ghost: PlacedItem | null = null;
    if (dragging) ghost = dragging;
    else if (this.edit.placing && this.pointer) {
      const pl = this.edit.placing;
      const def = defOf({ type: pl.type } as PlacedItem);
      ghost = this.placeAt({ id: "ghost", type: pl.type, col: 0, row: 0, rot: normRot(def, pl.rot), color: pl.color, y: wallY(def) }, this.pointer);
    }
    if (ghost) {
      const ok = canPlace(this.room, ghost).ok;
      const def = defOf(ghost);
      if (def.kind === "wall") this.drawWallItem(c, ghost, 0.8);
      else if (def.kind === "rug") this.drawRug(c, ghost, 0.8);
      else if (def.proc === "partition") {
        this.drawPartition(c, ghost, 0.8, false);
        if (defOf(ghost).doorway) this.drawDoorway(c, ghost, 0.8);
        if (this.drag?.moved && this.drag.id === ghost.id) {
          // what is hung on the panel travels with it
          const og = partitionGeo(this.drag.orig).face;
          const ng = partitionGeo(ghost).face;
          if (og && ng) {
            for (const ch of childrenOf(this.room, ghost.id)) {
              this.drawWallItem(c, { ...ch, x: (ch.x ?? 0) + ng.x - og.x, y: (ch.y ?? 0) + ng.y - og.y }, 0.8);
            }
          }
        }
      } else this.drawOps(c, ghost, 0.78);
      const r = itemRect(ghost);
      c.save();
      c.fillStyle = ok ? "rgba(120,230,120,0.22)" : "rgba(235,80,70,0.32)";
      c.strokeStyle = ok ? "#6fe06f" : "#eb5046";
      c.lineWidth = 2;
      if (def.kind === "wall") {
        c.fillRect(r.x, r.y, r.w, r.h);
        c.strokeRect(r.x, r.y, r.w, r.h);
      } else {
        const [fw, fh] = footprint(ghost);
        c.fillRect(ghost.col * TILE, WALL_H + ghost.row * TILE, fw * TILE, fh * TILE);
        c.strokeRect(ghost.col * TILE + 1, WALL_H + ghost.row * TILE + 1, fw * TILE - 2, fh * TILE - 2);
      }
      c.restore();
    }
    // who sits at each workstation
    for (const it of this.room.items) {
      if (!defOf(it).workstation) continue;
      const r = itemRect(it);
      const label = it.agent ? this.profiles[it.agent].name : "ว่าง";
      c.font = `bold 9px ${this.pixelFont}`;
      const w = c.measureText(label).width + 8;
      c.fillStyle = it.agent ? "rgba(20,30,50,0.85)" : "rgba(90,40,40,0.85)";
      c.fillRect(r.x + r.w / 2 - w / 2, r.y + r.h - 14, w, 12);
      c.fillStyle = "#fff";
      c.textBaseline = "middle";
      c.fillText(label, r.x + r.w / 2 - w / 2 + 4, r.y + r.h - 8);
    }
  }

  private drawLabel(ctx: CanvasRenderingContext2D, a: Actor, k: number) {
    const name = this.profiles[a.id].name;
    const team = AGENT_BY_ID[a.id].team;
    const fs = Math.max(9, Math.round(3.3 * k));
    ctx.font = `600 ${fs}px ${this.font}`;
    const tw = ctx.measureText(name).width;
    const bw = tw + 16;
    const bh = fs + 6;
    const lx = a.x * k - bw / 2;
    const ly = (a.y + 5) * k;
    ctx.fillStyle = "rgba(8,10,16,0.86)";
    ctx.fillRect(lx, ly, bw, bh);
    ctx.strokeStyle = this.selected === a.id ? "#5ff3ff" : "rgba(255,255,255,0.25)";
    ctx.lineWidth = 1;
    ctx.strokeRect(lx + 0.5, ly + 0.5, bw - 1, bh - 1);
    ctx.fillStyle = TEAM_COLOR[team];
    ctx.fillRect(lx + 4, ly + bh / 2 - 2, 4, 4);
    ctx.fillStyle = "#ffffff";
    ctx.textBaseline = "middle";
    ctx.fillText(name, lx + 11, ly + bh / 2 + 1);
  }

  private drawLink(ctx: CanvasRenderingContext2D, l: Link, k: number, now: number) {
    const a = this.actors.get(l.from)!;
    const b = this.actors.get(l.to)!;
    const ax = a.x * k;
    const ay = (a.y - 30) * k;
    const bx = b.x * k;
    const by = (b.y - 30) * k;
    const len = Math.hypot(bx - ax, by - ay);
    if (len < 10) return;
    const ux = (bx - ax) / len;
    const uy = (by - ay) / len;
    const pad = 14 * k * 0.6;
    const sx = ax + ux * pad;
    const sy = ay + uy * pad;
    const ex = bx - ux * pad;
    const ey = by - uy * pad;
    const life = Math.min(1, (now - l.start) / 250, (l.until - now) / 400);
    ctx.save();
    ctx.globalAlpha = Math.max(0, life);
    ctx.strokeStyle = "#5ff3ff";
    ctx.shadowColor = "#5ff3ff";
    ctx.shadowBlur = 10;
    ctx.lineWidth = Math.max(2, k * 0.9);
    ctx.setLineDash([8, 6]);
    ctx.lineDashOffset = -now / 25;
    ctx.beginPath();
    ctx.moveTo(sx, sy);
    ctx.lineTo(ex, ey);
    ctx.stroke();
    ctx.setLineDash([]);
    const ah = Math.max(7, k * 3);
    ctx.fillStyle = "#5ff3ff";
    ctx.beginPath();
    ctx.moveTo(ex, ey);
    ctx.lineTo(ex - ux * ah - uy * ah * 0.6, ey - uy * ah + ux * ah * 0.6);
    ctx.lineTo(ex - ux * ah + uy * ah * 0.6, ey - uy * ah - ux * ah * 0.6);
    ctx.closePath();
    ctx.fill();
    ctx.shadowBlur = 0;
    const fs = Math.max(9, Math.round(3.2 * k));
    ctx.font = `600 ${fs}px ${this.pixelFont}`;
    const tw = ctx.measureText(l.label).width;
    const mx = (sx + ex) / 2;
    const my = (sy + ey) / 2;
    ctx.fillStyle = "rgba(8,10,16,0.9)";
    ctx.fillRect(mx - tw / 2 - 6, my - fs / 2 - 4, tw + 12, fs + 8);
    ctx.strokeStyle = "#5ff3ff";
    ctx.lineWidth = 1;
    ctx.strokeRect(mx - tw / 2 - 5.5, my - fs / 2 - 3.5, tw + 11, fs + 7);
    ctx.fillStyle = "#ffffff";
    ctx.textBaseline = "middle";
    ctx.fillText(l.label, mx - tw / 2, my + 1);
    ctx.restore();
  }

  private drawBubble(ctx: CanvasRenderingContext2D, a: Actor, k: number) {
    const b = a.bubble!;
    const fs = Math.max(10, Math.round(4 * k));
    ctx.font = `500 ${fs}px ${this.font}`;
    const maxW = Math.max(120, 46 * k);
    let text = b.text.replace(/\s+/g, " ").trim();
    if (ctx.measureText(text).width > maxW) {
      while (text.length > 1 && ctx.measureText("…" + text).width > maxW) text = text.slice(1);
      text = "…" + text;
    }
    const tw = ctx.measureText(text).width;
    const headY = (a.y - FEET_Y - 4) * k;
    const bw = tw + 14;
    const bh = fs + 10;
    let bx = a.x * k - bw / 2;
    bx = Math.max(4, Math.min(bx, this.W * k - bw - 4));
    const by = Math.max(2, headY - bh - 6);
    const fill = b.kind === "error" ? "#ffe3df" : b.kind === "wait" ? "#ecebe6" : "#ffffff";
    ctx.fillStyle = "rgba(0,0,0,0.35)";
    ctx.fillRect(bx + 3, by + 3, bw, bh);
    ctx.fillStyle = fill;
    ctx.fillRect(bx, by, bw, bh);
    ctx.strokeStyle = BUBBLE_EDGE[b.kind];
    ctx.lineWidth = 2;
    ctx.strokeRect(bx + 1, by + 1, bw - 2, bh - 2);
    const tx = Math.max(bx + 8, Math.min(a.x * k, bx + bw - 8));
    ctx.beginPath();
    ctx.moveTo(tx - 4, by + bh - 1);
    ctx.lineTo(tx, by + bh + 6);
    ctx.lineTo(tx + 4, by + bh - 1);
    ctx.closePath();
    ctx.fillStyle = fill;
    ctx.fill();
    ctx.beginPath();
    ctx.moveTo(tx - 4, by + bh);
    ctx.lineTo(tx, by + bh + 6);
    ctx.lineTo(tx + 4, by + bh);
    ctx.stroke();
    ctx.fillStyle = "#111111";
    ctx.textBaseline = "middle";
    ctx.fillText(text, bx + 7, by + bh / 2 + 1);
  }
}

function stationOrder(it: PlacedItem): "desk-last" | "desk-first" {
  const rot = normRot(defOf(it), it.rot);
  return rot === "N" ? "desk-first" : "desk-last";
}

export { CELL_H };
