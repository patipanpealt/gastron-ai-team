// Server-side: read a URL the user pasted as a reference and turn it into plain text.
// Public pages only. Private/internal addresses are refused so this cannot be used to probe the local network.
import { lookup } from "node:dns/promises";
import { isIP } from "node:net";

const MAX_BYTES = 1_500_000;
const MAX_TEXT = 14_000;

function isPrivateIp(ip: string) {
  if (ip.includes(":")) return ip === "::1" || ip.startsWith("fc") || ip.startsWith("fd") || ip.startsWith("fe80") || ip.startsWith("::ffff:127.") || ip === "::";
  const [a, b] = ip.split(".").map(Number);
  return a === 10 || a === 127 || a === 0 || (a === 169 && b === 254) || (a === 172 && b >= 16 && b <= 31) || (a === 192 && b === 168) || (a === 100 && b >= 64 && b <= 127);
}

async function assertPublic(u: URL) {
  if (u.protocol !== "http:" && u.protocol !== "https:") throw new Error("รองรับเฉพาะลิงก์ http/https");
  const host = u.hostname.replace(/^\[|\]$/g, "");
  if (host === "localhost" || host.endsWith(".local") || host.endsWith(".internal")) throw new Error("ไม่อ่านลิงก์ที่ชี้ไปยังเครื่อง/เครือข่ายภายใน");
  const ips = isIP(host) ? [host] : (await lookup(host, { all: true })).map((a) => a.address);
  if (!ips.length || ips.some(isPrivateIp)) throw new Error("ไม่อ่านลิงก์ที่ชี้ไปยังเครื่อง/เครือข่ายภายใน");
}

/** Google Docs / Sheets / Slides / Drive share links -> a URL that returns the content as text. */
export function exportUrl(raw: string): { url: string; note?: string } {
  const u = new URL(raw);
  if (u.hostname === "docs.google.com") {
    const m = u.pathname.match(/\/(document|spreadsheets|presentation)\/d\/([\w-]+)/);
    if (m) {
      const fmt = m[1] === "spreadsheets" ? "csv" : "txt";
      return { url: `https://docs.google.com/${m[1]}/d/${m[2]}/export?format=${fmt}` };
    }
  }
  if (u.hostname === "drive.google.com") {
    const id = u.pathname.match(/\/file\/d\/([\w-]+)/)?.[1] || u.searchParams.get("id");
    if (id) return { url: `https://drive.google.com/uc?export=download&id=${id}` };
  }
  return { url: raw };
}

function htmlToText(html: string) {
  const title = html.match(/<title[^>]*>([\s\S]*?)<\/title>/i)?.[1]?.trim() ?? "";
  const text = html
    .replace(/<(script|style|noscript|svg|nav|footer|header)[\s\S]*?<\/\1>/gi, " ")
    .replace(/<br\s*\/?>|<\/(p|div|li|h[1-6]|tr)>/gi, "\n")
    .replace(/<[^>]+>/g, " ")
    .replace(/&nbsp;/g, " ")
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/[ \t]+/g, " ")
    .replace(/\n\s*\n+/g, "\n")
    .trim();
  return (title ? `${title}\n\n` : "") + text;
}

export interface ReadResult {
  ok: boolean;
  text: string;
  /** Why nothing could be read, in Thai. */
  problem?: string;
}

export async function readUrl(raw: string): Promise<ReadResult> {
  let target: URL;
  try {
    target = new URL(exportUrl(raw.trim()).url);
  } catch {
    return { ok: false, text: "", problem: "ลิงก์ไม่ถูกต้อง" };
  }
  try {
    let res: Response | null = null;
    for (let hops = 0; hops < 5; hops++) {
      await assertPublic(target);
      res = await fetch(target, {
        redirect: "manual",
        signal: AbortSignal.timeout(15000),
        headers: { "User-Agent": "Mozilla/5.0 (compatible; GastronOfficeBot/1.0)", Accept: "text/html,text/plain,text/csv,application/json;q=0.9,*/*;q=0.5" },
      });
      const loc = res.headers.get("location");
      if (res.status >= 300 && res.status < 400 && loc) {
        target = new URL(loc, target);
        res = null;
        continue;
      }
      break;
    }
    if (!res) return { ok: false, text: "", problem: "ลิงก์ redirect มากเกินไป" };
    if (res.status === 401 || res.status === 403) return { ok: false, text: "", problem: "เข้าไม่ได้ — ไฟล์/หน้านี้ไม่ได้แชร์เป็นสาธารณะ (ตั้งเป็น “ทุกคนที่มีลิงก์ดูได้”)" };
    if (!res.ok) return { ok: false, text: "", problem: `เปิดลิงก์ไม่ได้ (HTTP ${res.status})` };
    const type = (res.headers.get("content-type") || "").toLowerCase();
    if (/^(image|video|audio)\//.test(type)) return { ok: false, text: "", problem: "เป็นรูป/วิดีโอ — ตอนนี้ AI อ่านได้เฉพาะข้อความ ให้อธิบายไว้ในช่องรายละเอียดแทน" };
    if (type.includes("pdf")) return { ok: false, text: "", problem: "ยังอ่าน PDF ไม่ได้ — ใช้ลิงก์ Google Docs/หน้าเว็บ หรือพิมพ์ใจความไว้ในช่องรายละเอียด" };
    // read at most MAX_BYTES
    const reader = res.body?.getReader();
    if (!reader) return { ok: false, text: "", problem: "ไม่มีเนื้อหา" };
    const chunks: Uint8Array[] = [];
    let size = 0;
    while (size < MAX_BYTES) {
      const { value, done } = await reader.read();
      if (done) break;
      chunks.push(value);
      size += value.length;
    }
    void reader.cancel().catch(() => undefined);
    const raw8 = Buffer.concat(chunks).toString("utf8");
    let text = type.includes("html") || /^\s*<(!doctype|html)/i.test(raw8) ? htmlToText(raw8) : raw8.trim();
    if (/accounts\.google\.com|ServiceLogin/.test(res.url || "") || (type.includes("html") && /sign in|ลงชื่อเข้าใช้/i.test(text.slice(0, 400)) && text.length < 1500)) {
      return { ok: false, text: "", problem: "ต้องล็อกอินก่อนถึงจะเห็น — ตั้งการแชร์เป็น “ทุกคนที่มีลิงก์ดูได้”" };
    }
    if (text.length < 40) return { ok: false, text: "", problem: "อ่านเนื้อหาไม่ได้ (หน้านี้อาจโหลดด้วย JavaScript หรือว่างเปล่า)" };
    text = text.slice(0, MAX_TEXT);
    return { ok: true, text };
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    return { ok: false, text: "", problem: /abort|timeout/i.test(msg) ? "เปิดลิงก์ช้าเกินไป (timeout)" : /ENOTFOUND|EAI_AGAIN/.test(msg) ? "หาเว็บนี้ไม่เจอ — ตรวจว่าลิงก์พิมพ์ถูกต้อง" : msg.slice(0, 160) };
  }
}
