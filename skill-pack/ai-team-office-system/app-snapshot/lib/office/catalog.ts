// Everything that can be placed in the office: sizes, footprints and which sprite to draw for each rotation.
//
// World units are pixels. A tile is 32x32. The floor grid starts WALL_H pixels below the top of the canvas (the back
// wall occupies that strip). Objects are drawn OBJECT_SCALE times bigger than their source art, and their footprint
// (`variant().fp`, in tiles at 1x) grows with them. Floor items are aligned so the *solid body* of the sprite (not
// its soft shadow) is centred in its footprint and rests on the footprint's lower edge.
import meta from "./furniture-meta.json";

export const TILE = 32;
/** Furniture, wall decor and the back wall are drawn this much bigger than their source art (characters are not). */
export const OBJECT_SCALE = 1.5;
export const WALL_H = Math.round(64 * OBJECT_SCALE);

/** Sprite suffix for each rotation: S=front, E=right, N=back, W=left. */
export type Rot = "S" | "E" | "N" | "W";
export const ROT_ORDER: Rot[] = ["S", "E", "N", "W"];
export const ROT_SUFFIX: Record<Rot, string> = { S: "front", E: "right", N: "back", W: "left" };

export type Category = "work" | "furniture" | "decor" | "wall" | "zone";
/** floor = solid object on the floor, rug = flat on the floor, top = small thing that may stand on a table, wall = hangs on the back wall */
export type Kind = "floor" | "rug" | "top" | "wall";

export interface SpriteMeta {
  w: number;
  h: number;
  body: [number, number, number, number];
}
export const SPRITES = meta as unknown as Record<string, SpriteMeta>;

export interface Variant {
  sprite: string;
  fp: [number, number];
}

export interface ItemDef {
  type: string;
  name: string;
  icon: string;
  cat: Category;
  kind: Kind;
  rots: Rot[];
  /** Sprite and footprint (columns, rows) for a rotation. */
  variant: (rot: Rot) => Variant;
  block: boolean;
  /** Default y (px from the top of the canvas) for wall items. */
  wallY?: number;
  workstation?: boolean;
  /** Drawn by code instead of from a sprite: a partition panel or a name plaque. */
  proc?: "partition" | "plaque" | "door";
  /** A one-tile partition with a door in it: agents walk through, the door swings open for them. */
  doorway?: boolean;
  /** The user can pick a colour (rugs). */
  tint?: boolean;
}

const byRot =
  (base: string, fpFrontBack: [number, number], fpSide: [number, number]) =>
  (rot: Rot): Variant => ({
    sprite: `${base}_${ROT_SUFFIX[rot]}`,
    fp: rot === "S" || rot === "N" ? fpFrontBack : fpSide,
  });

const single = (sprite: string, fp: [number, number]) => (): Variant => ({ sprite, fp });
const ALL: Rot[] = ["S", "E", "N", "W"];

export const ITEMS: ItemDef[] = [
  // ---- workstations & seating
  {
    type: "workstation",
    name: "โต๊ะทำงาน + เก้าอี้",
    icon: "🖥️",
    cat: "work",
    kind: "floor",
    rots: ALL,
    workstation: true,
    block: true,
    // footprint of the whole set (desk + chair); the drawing code composes the two sprites
    variant: (rot) => ({ sprite: "desk_front", fp: rot === "S" || rot === "N" ? [2, 3] : [2, 2] }),
  },
  { type: "desk", name: "โต๊ะ", icon: "🪑", cat: "work", kind: "floor", rots: ALL, block: true, variant: byRot("desk", [2, 2], [1, 2]) },
  { type: "chair", name: "เก้าอี้", icon: "💺", cat: "work", kind: "floor", rots: ALL, block: true, variant: byRot("chair", [1, 1], [1, 1]) },
  {
    type: "meeting",
    name: "โต๊ะประชุม",
    icon: "🗣️",
    cat: "work",
    kind: "floor",
    rots: ["S", "E"],
    block: true,
    variant: (rot) => (rot === "S" || rot === "N" ? { sprite: "meeting_h", fp: [6, 2] } : { sprite: "meeting_v", fp: [2, 6] }),
  },
  // ---- furniture
  { type: "sofa", name: "โซฟา", icon: "🛋️", cat: "furniture", kind: "floor", rots: ALL, block: true, variant: byRot("sofa", [3, 1], [1, 2]) },
  { type: "shelf", name: "ชั้นหนังสือ", icon: "📚", cat: "furniture", kind: "floor", rots: ALL, block: true, variant: byRot("shelf", [2, 1], [1, 2]) },
  { type: "filing", name: "ตู้เอกสาร", icon: "🗄️", cat: "furniture", kind: "floor", rots: ALL, block: true, variant: byRot("filing", [1, 1], [1, 1]) },
  { type: "fridge", name: "ตู้เย็น", icon: "🧊", cat: "furniture", kind: "floor", rots: ALL, block: true, variant: byRot("fridge", [1, 1], [1, 1]) },
  { type: "cooler", name: "ตู้กดน้ำ", icon: "🚰", cat: "furniture", kind: "floor", rots: ALL, block: true, variant: byRot("cooler", [1, 1], [1, 1]) },
  { type: "whiteboard", name: "ไวต์บอร์ด", icon: "📋", cat: "furniture", kind: "floor", rots: ALL, block: true, variant: byRot("wb", [2, 1], [1, 2]) },
  { type: "plush", name: "ตุ๊กตาหมูตัวใหญ่", icon: "🐷", cat: "furniture", kind: "floor", rots: ALL, block: true, variant: byRot("plush", [1, 1], [1, 1]) },
  { type: "bin_office", name: "ถังขยะ", icon: "🗑️", cat: "furniture", kind: "floor", rots: ["S"], block: true, variant: single("bin_office", [1, 1]) },
  { type: "bin_pedal", name: "ถังขยะเท้าเหยียบ", icon: "🥫", cat: "furniture", kind: "floor", rots: ["S"], block: true, variant: single("bin_pedal", [1, 1]) },
  // ---- zones & signs
  {
    type: "partition",
    name: "แผ่น Partition กั้นโซน",
    icon: "🧱",
    cat: "zone",
    kind: "floor",
    rots: ["S", "E"],
    block: true,
    proc: "partition",
    tint: true,
    // footprint comes from the panel's length (see room.ts)
    variant: () => ({ sprite: "", fp: [1, 1] }),
  },
  {
    type: "partition_door",
    name: "Partition + ประตู (ต่อกับแผ่นปกติได้)",
    icon: "🚪",
    cat: "zone",
    kind: "floor",
    rots: ["S", "E"],
    block: true,
    proc: "partition",
    doorway: true,
    tint: true,
    variant: () => ({ sprite: "", fp: [1, 1] }),
  },
  {
    type: "plaque",
    name: "ป้ายชื่อทีม (พิมพ์ข้อความเอง)",
    icon: "🪧",
    cat: "zone",
    kind: "wall",
    rots: ["S"],
    block: false,
    wallY: 14,
    proc: "plaque",
    variant: () => ({ sprite: "", fp: [0, 0] }),
  },
  // ---- decor
  { type: "plant_big", name: "ต้นไม้ใหญ่", icon: "🪴", cat: "decor", kind: "floor", rots: ["S"], block: true, variant: single("plant_big", [1, 1]) },
  { type: "plant_snake", name: "ต้นลิ้นมังกร", icon: "🌿", cat: "decor", kind: "floor", rots: ["S"], block: true, variant: single("plant_snake", [1, 1]) },
  { type: "plant_desk", name: "กระถางเล็ก (วางบนโต๊ะ)", icon: "🌱", cat: "decor", kind: "top", rots: ["S"], block: false, variant: single("plant_desk", [1, 1]) },
  { type: "rug_s", name: "พรม เล็ก", icon: "🟫", cat: "decor", kind: "rug", rots: ["S"], block: false, tint: true, variant: () => ({ sprite: "", fp: [2, 2] }) },
  { type: "rug_m", name: "พรม กลาง", icon: "🟦", cat: "decor", kind: "rug", rots: ["S", "E"], block: false, tint: true, variant: (r) => ({ sprite: "", fp: r === "S" || r === "N" ? [3, 2] : [2, 3] }) },
  { type: "rug_l", name: "พรม ใหญ่", icon: "🟩", cat: "decor", kind: "rug", rots: ["S", "E"], block: false, tint: true, variant: (r) => ({ sprite: "", fp: r === "S" || r === "N" ? [4, 3] : [3, 4] }) },
  { type: "rug_xl", name: "พรม ใหญ่มาก", icon: "🟥", cat: "decor", kind: "rug", rots: ["S", "E"], block: false, tint: true, variant: (r) => ({ sprite: "", fp: r === "S" || r === "N" ? [6, 4] : [4, 6] }) },
  // ---- wall
  { type: "window", name: "หน้าต่าง", icon: "🪟", cat: "wall", kind: "wall", rots: ["S"], block: false, wallY: 8, variant: single("window", [0, 0]) },
  { type: "window_blinds", name: "หน้าต่าง + ม่านปรับแสง", icon: "🪟", cat: "wall", kind: "wall", rots: ["S"], block: false, wallY: 8, variant: single("window_blinds", [0, 0]) },
  { type: "door", name: "ประตู", icon: "🚪", cat: "wall", kind: "wall", rots: ["S"], block: false, wallY: 4, proc: "door", variant: single("door", [0, 0]) },
  { type: "pillar", name: "เสาผนัง", icon: "🏛️", cat: "wall", kind: "wall", rots: ["S"], block: false, wallY: 0, variant: single("wall_pillar", [0, 0]) },
  { type: "wb_wall", name: "ไวต์บอร์ดติดผนัง", icon: "📋", cat: "wall", kind: "wall", rots: ["S"], block: false, wallY: 8, variant: single("wb_wall", [0, 0]) },
  { type: "calendar", name: "ปฏิทิน", icon: "📅", cat: "wall", kind: "wall", rots: ["S"], block: false, wallY: 6, variant: single("calendar", [0, 0]) },
  { type: "clock", name: "นาฬิกา เล็ก", icon: "🕒", cat: "wall", kind: "wall", rots: ["S"], block: false, wallY: 10, variant: single("clock", [0, 0]) },
  { type: "clock_large", name: "นาฬิกา ใหญ่", icon: "🕰️", cat: "wall", kind: "wall", rots: ["S"], block: false, wallY: 8, variant: single("clock_large", [0, 0]) },
  { type: "poster_flame", name: "โปสเตอร์ SAFE", icon: "🔥", cat: "wall", kind: "wall", rots: ["S"], block: false, wallY: 8, variant: single("poster_flame", [0, 0]) },
  { type: "poster_flame_large", name: "โปสเตอร์ SAFE ใหญ่", icon: "🔥", cat: "wall", kind: "wall", rots: ["S"], block: false, wallY: 4, variant: single("poster_flame_large", [0, 0]) },
  { type: "poster_pig", name: "โปสเตอร์หมู HI!", icon: "🐷", cat: "wall", kind: "wall", rots: ["S"], block: false, wallY: 8, variant: single("poster_pig", [0, 0]) },
  { type: "poster_pig_large", name: "โปสเตอร์หมู ใหญ่", icon: "🐷", cat: "wall", kind: "wall", rots: ["S"], block: false, wallY: 4, variant: single("poster_pig_large", [0, 0]) },
];

export const ITEM_BY_TYPE = Object.fromEntries(ITEMS.map((i) => [i.type, i])) as Record<string, ItemDef>;

export const CATEGORY_LABEL: Record<Category, string> = {
  work: "โต๊ะ & ที่นั่ง",
  furniture: "เฟอร์นิเจอร์",
  decor: "ของตกแต่ง & พรม",
  wall: "ผนัง",
  zone: "กั้นโซน & ป้าย",
};

export const PARTITION_STYLES = [
  { id: "solid", name: "ทึบ" },
  { id: "glass", name: "กระจกใส" },
  { id: "slat", name: "ไม้ระแนง" },
] as const;
export type PartitionStyle = (typeof PARTITION_STYLES)[number]["id"];
export const PARTITION_COLORS = ["#e9e4d6", "#9fb8a0", "#8fb4d8", "#e3a6b8", "#44546e", "#a67c52", "#4a4f5c", "#cf5b4c"];

export const PLAQUE_STYLES = [
  { id: "wood", name: "ไม้", fill: "#a9743f", text: "#fff0d0" },
  { id: "brass", name: "ทองเหลือง", fill: "#d9b25a", text: "#3a2a10" },
  { id: "navy", name: "กรมท่า", fill: "#2d3a63", text: "#ffffff" },
  { id: "green", name: "เขียว", fill: "#1f8f55", text: "#ffffff" },
  { id: "red", name: "แดง", fill: "#c0262f", text: "#ffffff" },
  { id: "white", name: "ขาว", fill: "#f4f1e8", text: "#2b2230" },
] as const;
export type PlaqueStyle = (typeof PLAQUE_STYLES)[number]["id"];

/** Plaque sizes in world pixels. */
export const PLAQUE_SIZES = [
  { id: "xs", name: "เล็กมาก", w: 64, h: 22 },
  { id: "s", name: "เล็ก", w: 96, h: 28 },
  { id: "m", name: "กลาง", w: 144, h: 32 },
  { id: "l", name: "ใหญ่", w: 208, h: 40 },
] as const;
export type PlaqueSize = (typeof PLAQUE_SIZES)[number]["id"];

export const FLOORS = [
  { id: "wood_a", name: "ไม้ลายอิฐ A" },
  { id: "wood_b", name: "ไม้ลายอิฐ B" },
  { id: "tile", name: "กระเบื้องหมากรุก" },
  { id: "carpet", name: "พรมปูทั้งห้อง" },
] as const;
export type FloorId = (typeof FLOORS)[number]["id"];

export const SURFACE_TINTS: { id: string; name: string; hex: string | null }[] = [
  { id: "none", name: "สีเดิม", hex: null },
  { id: "mint", name: "มิ้นท์", hex: "#7fd6b4" },
  { id: "sky", name: "ฟ้า", hex: "#7fb8f0" },
  { id: "rose", name: "ชมพู", hex: "#f09ab4" },
  { id: "lilac", name: "ม่วงอ่อน", hex: "#b59af0" },
  { id: "sand", name: "ทราย", hex: "#e8c88a" },
  { id: "slate", name: "เทาเข้ม", hex: "#6a7488" },
  { id: "green", name: "เขียว", hex: "#6fbf6a" },
];
