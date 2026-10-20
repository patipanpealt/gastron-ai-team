import { NextResponse } from "next/server";
import { cookies } from "next/headers";
import { AUTH_COOKIE, authUsers, verifySession } from "@/lib/auth";
import { kvEnabled } from "@/lib/kv";
import { getMember, listMembers, normEmail, removeMember, saveMember } from "@/lib/members";

// Admin-only: add people by email (they set their own password at first login), reset a password, remove someone.
async function admin() {
  const s = await verifySession((await cookies()).get(AUTH_COOKIE)?.value);
  return s?.role === "admin" ? s : null;
}
const deny = () => NextResponse.json({ error: "เฉพาะแอดมินเท่านั้น" }, { status: 403 });
const noKv = () => NextResponse.json({ error: "ยังไม่ได้เชื่อม Upstash Redis จึงเพิ่มสมาชิกจากหน้านี้ไม่ได้" }, { status: 503 });

export async function GET() {
  if (!(await admin())) return deny();
  const env = authUsers().map((u) => ({ email: u.email, role: u.role, source: "env" as const, hasPassword: true }));
  const members = (await listMembers()).map((m) => ({ email: m.email, role: m.role, source: "app" as const, hasPassword: !!m.hash }));
  return NextResponse.json({ canEdit: kvEnabled(), users: [...env, ...members] });
}

export async function POST(req: Request) {
  if (!(await admin())) return deny();
  if (!kvEnabled()) return noKv();
  const { email, role } = (await req.json()) as { email?: string; role?: string };
  const e = normEmail(email);
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(e)) return NextResponse.json({ error: "อีเมลไม่ถูกต้อง" }, { status: 400 });
  if (authUsers().some((u) => u.email.toLowerCase() === e) || (await getMember(e)))
    return NextResponse.json({ error: "อีเมลนี้อยู่ในระบบแล้ว" }, { status: 409 });
  await saveMember({ email: e, role: role === "admin" ? "admin" : "member", addedAt: Date.now() });
  return NextResponse.json({ ok: true });
}

// reset password: clears it, so the person sets a new one at next login
export async function PATCH(req: Request) {
  if (!(await admin())) return deny();
  const m = await getMember(normEmail(((await req.json()) as { email?: string }).email));
  if (!m) return NextResponse.json({ error: "ไม่พบสมาชิก (รีเซ็ตได้เฉพาะคนที่เพิ่มจากหน้านี้)" }, { status: 404 });
  await saveMember({ ...m, hash: undefined });
  return NextResponse.json({ ok: true });
}

export async function DELETE(req: Request) {
  const me = await admin();
  if (!me) return deny();
  const e = normEmail(((await req.json()) as { email?: string }).email);
  if (e === me.email.toLowerCase()) return NextResponse.json({ error: "ลบตัวเองไม่ได้" }, { status: 400 });
  await removeMember(e);
  return NextResponse.json({ ok: true });
}
