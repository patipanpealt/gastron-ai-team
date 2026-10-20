// Members an admin adds from the UI (stored in Upstash). They have no password until they set one on first login.
// People in AUTH_USERS keep working as before and win over a member with the same email.
import { kv, kvEnabled } from "./kv";
import type { Role } from "./auth";

const MEMBERS = "gastron:members"; // hash: email (lowercase) -> Member JSON

export interface Member {
  email: string;
  role: Role;
  hash?: string; // set by the user on first login
  addedAt: number;
}

export const normEmail = (s: unknown) => String(s ?? "").trim().toLowerCase();

export async function getMember(email: string): Promise<Member | null> {
  if (!kvEnabled()) return null;
  const raw = await kv<string | null>("HGET", MEMBERS, normEmail(email));
  return raw ? (JSON.parse(raw) as Member) : null;
}

export async function listMembers(): Promise<Member[]> {
  if (!kvEnabled()) return [];
  const flat = await kv<string[]>("HGETALL", MEMBERS); // [field, value, field, value, ...]
  const out: Member[] = [];
  for (let i = 1; i < flat.length; i += 2) out.push(JSON.parse(flat[i]) as Member);
  return out.sort((a, b) => a.addedAt - b.addedAt);
}

export async function saveMember(m: Member) {
  await kv("HSET", MEMBERS, m.email, JSON.stringify(m));
}

export async function removeMember(email: string) {
  await kv("HDEL", MEMBERS, normEmail(email));
}
