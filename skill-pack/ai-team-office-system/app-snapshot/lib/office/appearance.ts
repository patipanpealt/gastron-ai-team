// What a character can wear, and each agent's starting look.
import { AGENTS, type AgentId } from "../agents";
import { hexToRgb, luminance } from "./palette";

export type SkinId = "light" | "medium" | "tan" | "deep";
export type HairStyleId = "neat" | "sidepart" | "up" | "short" | "ponytail" | "hime";
export type TopId = "tee" | "shirt" | "suit" | "dress" | "tank";
export type BottomId = "slacks" | "jeans" | "shorts" | "pencil" | "pleated";

export interface Appearance {
  skin: SkinId;
  /** "none" = bald. */
  hairStyle: HairStyleId | "none";
  /** Hex colour, or null for the original black. */
  hairColor: string | null;
  top: TopId;
  /** Hex colour, or null for the garment's original colour. */
  topColor: string | null;
  /** Ignored when the top is a dress (the dress has its own skirt). */
  bottom: BottomId;
  bottomColor: string | null;
}

export interface Profile {
  name: string;
  appearance: Appearance;
}

export const SKINS: { id: SkinId; name: string; hex: string }[] = [
  { id: "light", name: "ขาว", hex: "#f9d2b6" },
  { id: "medium", name: "ขาวเหลือง", hex: "#f5c49e" },
  { id: "tan", name: "แทน", hex: "#d69e6c" },
  { id: "deep", name: "เข้ม", hex: "#9c6844" },
];

export const HAIR_STYLES: { id: HairStyleId; name: string }[] = [
  { id: "neat", name: "ผมสั้นเรียบร้อย" },
  { id: "sidepart", name: "ผมเสยข้าง" },
  { id: "up", name: "ผมสั้นยกหน้า" },
  { id: "short", name: "ผมบ๊อบสั้น" },
  { id: "ponytail", name: "ผมมัดหางม้า" },
  { id: "hime", name: "ผมยาวหน้าม้า" },
];

export const TOPS: { id: TopId; name: string }[] = [
  { id: "tee", name: "เสื้อยืด" },
  { id: "shirt", name: "เสื้อเชิ้ต" },
  { id: "suit", name: "สูท + เนคไท" },
  { id: "dress", name: "เดรส" },
  { id: "tank", name: "เสื้อกล้าม" },
];

export const BOTTOMS: { id: BottomId; name: string }[] = [
  { id: "slacks", name: "กางเกงสแลคส์" },
  { id: "jeans", name: "ยีนส์" },
  { id: "shorts", name: "กางเกงขาสั้น" },
  { id: "pencil", name: "กระโปรงดินสอ" },
  { id: "pleated", name: "กระโปรงจีบ" },
];

/** Which ramp of each sheet is "the garment colour" (the rest — tie, collar, ribbon — keeps its own colour). */
export const TOP_MAIN: Record<TopId, string> = { tee: "tee", shirt: "shirt", suit: "navy", dress: "rose", tank: "heather" };
export const BOTTOM_MAIN: Record<BottomId, string> = { slacks: "slacks", jeans: "jeans", shorts: "khaki", pencil: "navy", pleated: "wine" };

const SKIN_RGB = SKINS.map((s) => ({ id: s.id, rgb: hexToRgb(s.hex) }));
export function nearestSkin(hex: string): SkinId {
  const [r, g, b] = hexToRgb(hex);
  let best = SKIN_RGB[0];
  let bd = Infinity;
  for (const s of SKIN_RGB) {
    const d = (s.rgb[0] - r) ** 2 + (s.rgb[1] - g) ** 2 + (s.rgb[2] - b) ** 2;
    if (d < bd) {
      bd = d;
      best = s;
    }
  }
  return best.id;
}

type Look = Pick<Appearance, "hairStyle" | "top" | "bottom">;

// Starting wardrobe: a mix of styles so the team is easy to tell apart. Colours come from each agent's old palette.
const START: Record<AgentId, Look> = {
  director: { hairStyle: "neat", top: "suit", bottom: "slacks" },
  strategist: { hairStyle: "short", top: "shirt", bottom: "pencil" },
  researcher: { hairStyle: "up", top: "shirt", bottom: "jeans" },
  copywriter: { hairStyle: "ponytail", top: "tee", bottom: "pleated" },
  content: { hairStyle: "sidepart", top: "tee", bottom: "jeans" },
  creative: { hairStyle: "hime", top: "dress", bottom: "pleated" },
  social: { hairStyle: "ponytail", top: "shirt", bottom: "pencil" },
  ads: { hairStyle: "neat", top: "tee", bottom: "slacks" },
  seo: { hairStyle: "up", top: "tee", bottom: "slacks" },
  analyst: { hairStyle: "short", top: "tank", bottom: "shorts" },
  qa: { hairStyle: "sidepart", top: "shirt", bottom: "slacks" },
};

const PANTS: Record<string, string> = {};

export function defaultAppearance(id: AgentId): Appearance {
  const a = AGENTS.find((x) => x.id === id)!;
  const start = START[id];
  const darkHair = luminance(a.look.hair) < 0.14;
  return {
    skin: nearestSkin(a.look.skin),
    hairStyle: start.hairStyle,
    hairColor: darkHair ? null : a.look.hair,
    top: start.top,
    topColor: a.look.shirt,
    bottom: start.bottom,
    bottomColor: PANTS[id] ?? null,
  };
}

export function defaultProfiles(): Record<AgentId, Profile> {
  return Object.fromEntries(AGENTS.map((a) => [a.id, { name: a.name, appearance: defaultAppearance(a.id) }])) as Record<AgentId, Profile>;
}

export function sanitizeAppearance(raw: unknown, fallback: Appearance): Appearance {
  const o = (raw && typeof raw === "object" ? raw : {}) as Partial<Appearance>;
  const pick = <T extends string>(v: unknown, list: readonly T[], d: T): T => (list.includes(v as T) ? (v as T) : d);
  const hex = (v: unknown, d: string | null) => (v === null ? null : typeof v === "string" && /^#[0-9a-fA-F]{6}$/.test(v) ? v : d);
  return {
    skin: pick(o.skin, SKINS.map((s) => s.id), fallback.skin),
    hairStyle: pick(o.hairStyle, ["none", ...HAIR_STYLES.map((s) => s.id)] as const, fallback.hairStyle),
    hairColor: hex(o.hairColor, fallback.hairColor),
    top: pick(o.top, TOPS.map((s) => s.id), fallback.top),
    topColor: hex(o.topColor, fallback.topColor),
    bottom: pick(o.bottom, BOTTOMS.map((s) => s.id), fallback.bottom),
    bottomColor: hex(o.bottomColor, fallback.bottomColor),
  };
}

export function randomAppearance(): Appearance {
  const r = <T,>(a: readonly T[]) => a[Math.floor(Math.random() * a.length)];
  const colors = ["#d9333f", "#e8863a", "#e8c23a", "#2fa86a", "#2aa6a0", "#4a9fe0", "#3a64c8", "#384672", "#7a50b8", "#e67f98", "#dfe2ee", "#8a90a0", "#3b3d4e", "#8a5a3c"];
  const hair = [null, "#5a3a26", "#8a5634", "#a8472c", "#e8b948", "#8a8e9c", "#e878a8", "#3f6fd0"];
  return {
    skin: r(SKINS).id,
    hairStyle: r(HAIR_STYLES).id,
    hairColor: r(hair),
    top: r(TOPS).id,
    topColor: r(colors),
    bottom: r(BOTTOMS).id,
    bottomColor: r(colors),
  };
}
