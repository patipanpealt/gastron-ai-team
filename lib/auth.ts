// Email + password login. Users live in the AUTH_USERS env var (JSON, with scrypt hashes — never plain passwords):
//   [{"email":"a@b.com","role":"admin","hash":"scrypt:<salt-hex>:<hash-hex>"}]
// A signed cookie (HMAC-SHA256 with AUTH_SECRET) carries email + role. No AUTH_USERS = no login (local dev).
import { getMember } from "./members";

export const AUTH_COOKIE = "office_session";
export const SESSION_DAYS = 30;

export type Role = "admin" | "member";
export interface Session {
  email: string;
  role: Role;
}
export interface AuthUser extends Session {
  hash: string;
}

export function authUsers(): AuthUser[] {
  try {
    const raw = JSON.parse(process.env.AUTH_USERS || "[]") as AuthUser[];
    return Array.isArray(raw) ? raw.filter((u) => u && typeof u.email === "string" && typeof u.hash === "string") : [];
  } catch {
    return [];
  }
}

export const loginRequired = () => authUsers().length > 0;

const b64 = (s: string) => btoa(s).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
const unb64 = (s: string) => atob(s.replace(/-/g, "+").replace(/_/g, "/"));

async function hmac(data: string) {
  const secret = process.env.AUTH_SECRET || "";
  const key = await crypto.subtle.importKey("raw", new TextEncoder().encode(secret), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const sig = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(data));
  return Array.from(new Uint8Array(sig), (b) => b.toString(16).padStart(2, "0")).join("");
}

export async function signSession(s: Session): Promise<string> {
  const body = b64(JSON.stringify({ e: s.email, r: s.role, x: Date.now() + SESSION_DAYS * 864e5 }));
  return `${body}.${await hmac(body)}`;
}

export async function verifySession(token: string | undefined): Promise<Session | null> {
  if (!token || !process.env.AUTH_SECRET) return null;
  const [body, sig] = token.split(".");
  if (!body || !sig || sig !== (await hmac(body))) return null;
  try {
    const d = JSON.parse(unb64(body)) as { e: string; r: Role; x: number };
    if (!d.e || d.x < Date.now()) return null;
    // the user must still exist (removing someone from AUTH_USERS or the member list logs them out)
    const u = authUsers().find((x) => x.email.toLowerCase() === d.e.toLowerCase()) ?? (await getMember(d.e));
    return u ? { email: u.email, role: u.role === "admin" ? "admin" : "member" } : null;
  } catch {
    return null;
  }
}
