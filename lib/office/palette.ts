// Colour helpers for the dress-up system.
//
// The sprite sheets are drawn with fixed colour ramps (garments: 6 tones, hair: 8 tones). To dress a character in
// any colour the app builds a ramp for the chosen colour (hue-shifted shadows, warm highlights, like the art) and
// swaps the original ramp for it, pixel for pixel, when a sheet is loaded.

export type Rgb = [number, number, number];

export function hexToRgb(hex: string): Rgb {
  const h = hex.replace("#", "");
  const n = h.length === 3 ? h.split("").map((c) => c + c).join("") : h;
  return [parseInt(n.slice(0, 2), 16), parseInt(n.slice(2, 4), 16), parseInt(n.slice(4, 6), 16)];
}

export function rgbToHex([r, g, b]: Rgb): string {
  return "#" + [r, g, b].map((v) => Math.round(Math.min(255, Math.max(0, v))).toString(16).padStart(2, "0")).join("");
}

export function rgbToHsl([r, g, b]: Rgb): [number, number, number] {
  r /= 255;
  g /= 255;
  b /= 255;
  const max = Math.max(r, g, b);
  const min = Math.min(r, g, b);
  const l = (max + min) / 2;
  if (max === min) return [0, 0, l];
  const d = max - min;
  const s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
  let h = 0;
  if (max === r) h = (g - b) / d + (g < b ? 6 : 0);
  else if (max === g) h = (b - r) / d + 2;
  else h = (r - g) / d + 4;
  return [h * 60, s, l];
}

export function hslToRgb([h, s, l]: [number, number, number]): Rgb {
  h = ((h % 360) + 360) % 360;
  const c = (1 - Math.abs(2 * l - 1)) * s;
  const x = c * (1 - Math.abs(((h / 60) % 2) - 1));
  const m = l - c / 2;
  const [r, g, b] = h < 60 ? [c, x, 0] : h < 120 ? [x, c, 0] : h < 180 ? [0, c, x] : h < 240 ? [0, x, c] : h < 300 ? [x, 0, c] : [c, 0, x];
  return [(r + m) * 255, (g + m) * 255, (b + m) * 255];
}

const clamp = (v: number, lo: number, hi: number) => Math.min(hi, Math.max(lo, v));

/** Move a hue `deg` degrees toward blue-violet (250°) along the short way round: shadows read cool. */
function toward(h: number, target: number, deg: number) {
  const d = ((target - h + 540) % 360) - 180;
  return h + Math.sign(d) * Math.min(Math.abs(d), deg);
}

/**
 * A tone ramp built around `base`.
 *  garment (6): highlight, light, base, shade, deep, outline
 *  hair    (8): gloss, highlight, light, base, mid, shade, deep, outline
 */
export function makeRamp(base: string, kind: "garment" | "hair"): string[] {
  const [h, s, l] = rgbToHsl(hexToRgb(base));
  const tone = (dl: number, ds: number, cool: number, hueWarm = 0) =>
    rgbToHex(hslToRgb([toward(h, 250, cool) + hueWarm, clamp(s * ds, 0, 1), clamp(l + dl, 0.04, 0.97)]));
  if (kind === "garment") {
    return [
      tone(0.3, 0.75, 0, 5),
      tone(0.15, 0.95, 0, 2),
      rgbToHex(hexToRgb(base)),
      tone(-0.14, 1.05, 10),
      tone(-0.26, 1.1, 18),
      tone(-Math.min(0.42, l - 0.07), 0.8, 24),
    ];
  }
  return [
    tone(0.38, 0.55, 0, 6),
    tone(0.22, 0.8, 0, 4),
    tone(0.1, 0.95, 0, 1),
    rgbToHex(hexToRgb(base)),
    tone(-0.08, 1.02, 4),
    tone(-0.16, 1.05, 10),
    tone(-0.23, 1.08, 16),
    tone(-Math.min(0.3, l - 0.05), 0.7, 24),
  ];
}

export interface ColorOption {
  id: string;
  name: string;
  hex: string;
}

export const GARMENT_COLORS: ColorOption[] = [
  { id: "red", name: "แดง", hex: "#d9333f" },
  { id: "orange", name: "ส้ม", hex: "#e8863a" },
  { id: "yellow", name: "เหลือง", hex: "#e8c23a" },
  { id: "lime", name: "เขียวมะนาว", hex: "#8cc84b" },
  { id: "green", name: "เขียว", hex: "#2fa86a" },
  { id: "teal", name: "เขียวน้ำทะเล", hex: "#2aa6a0" },
  { id: "sky", name: "ฟ้า", hex: "#4a9fe0" },
  { id: "blue", name: "น้ำเงิน", hex: "#3a64c8" },
  { id: "navy", name: "กรมท่า", hex: "#384672" },
  { id: "purple", name: "ม่วง", hex: "#7a4fb0" },
  { id: "pink", name: "ชมพู", hex: "#e67f98" },
  { id: "white", name: "ขาว", hex: "#dfe2ee" },
  { id: "gray", name: "เทา", hex: "#8a90a0" },
  { id: "black", name: "ดำ", hex: "#3b3d4e" },
  { id: "brown", name: "น้ำตาล", hex: "#8a5a3c" },
  { id: "beige", name: "เบจ", hex: "#d4b678" },
];

export const HAIR_COLORS: ColorOption[] = [
  { id: "black", name: "ดำ", hex: "#4c5072" },
  { id: "darkbrown", name: "น้ำตาลเข้ม", hex: "#5a3a26" },
  { id: "brown", name: "น้ำตาล", hex: "#8a5634" },
  { id: "auburn", name: "น้ำตาลแดง", hex: "#a8472c" },
  { id: "ginger", name: "ส้มทอง", hex: "#d9702e" },
  { id: "blonde", name: "บลอนด์", hex: "#e8b948" },
  { id: "platinum", name: "ขาวเงิน", hex: "#cfcab8" },
  { id: "gray", name: "เทา", hex: "#8a8e9c" },
  { id: "pink", name: "ชมพู", hex: "#e878a8" },
  { id: "blue", name: "ฟ้าน้ำเงิน", hex: "#3f6fd0" },
  { id: "purple", name: "ม่วง", hex: "#7a50b8" },
  { id: "teal", name: "เขียวมิ้นท์", hex: "#2fa59a" },
];

/**
 * Swap every pixel whose colour is in `from` (index i) for `to[i]`. Used to recolour a sheet drawn with the default
 * ramp. Pixels with other colours (skin, face, translucent shadows) are left alone.
 */
export function remapColors(src: CanvasImageSource & { width: number; height: number }, from: string[], to: string[]): HTMLCanvasElement {
  const c = document.createElement("canvas");
  c.width = src.width;
  c.height = src.height;
  const ctx = c.getContext("2d", { willReadFrequently: true })!;
  ctx.imageSmoothingEnabled = false;
  ctx.drawImage(src, 0, 0);
  const map = new Map<number, Rgb>();
  from.forEach((f, i) => {
    const [r, g, b] = hexToRgb(f);
    map.set((r << 16) | (g << 8) | b, hexToRgb(to[i] ?? f));
  });
  const img = ctx.getImageData(0, 0, c.width, c.height);
  const d = img.data;
  for (let i = 0; i < d.length; i += 4) {
    if (d[i + 3] === 0) continue;
    const m = map.get((d[i] << 16) | (d[i + 1] << 8) | d[i + 2]);
    if (m) {
      d[i] = m[0];
      d[i + 1] = m[1];
      d[i + 2] = m[2];
    }
  }
  ctx.putImageData(img, 0, 0);
  return c;
}

/** Perceived brightness 0..1. */
export function luminance(hex: string) {
  const [r, g, b] = hexToRgb(hex);
  return (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255;
}
